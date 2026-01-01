from flask import Blueprint, request, jsonify, make_response
from database import db, get_subject_publisher, get_subject_config
import re, traceback
# 🚀 引入 AI 服務
from ai_service import ask_ai

review_bp = Blueprint('review', __name__)

def parse_note_content(subject, note, db_insight=None):
    """
    核心解析引擎：處理診斷內容
    """
    if not note:
        return "", [], "", db_insight or ""
        
    pages_match = re.search(r'[pP]\.?\s?\d+.*?\d+', note)
    pages = pages_match.group(0) if pages_match else ""
    
    tags = []
    insight = db_insight or ""
    sub = str(subject or "")
    
    if not db_insight:
        if "社會" in sub:
            if any(k in note for k in ['時序', '年份']): tags.append('🗓️ 時序')
        elif "數學" in sub:
            if any(k in note for k in ['計算', '算式']): tags.append('🧮 計算')
            if "單位" in note: tags.append('📏 單位細節')

    clean_note = re.sub(r'[pP]\.?\s?\d+.*?\d+', '', note).strip()
    return pages, tags, clean_note, insight

# --- 統一格式：加入 OPTIONS 處理與簡化路徑 ---

@review_bp.route('/list', methods=['GET', 'OPTIONS'])
def get_review_list():
    if request.method == 'OPTIONS': return '', 200
    
    subject = request.args.get('subject', '') 
    user_id = request.args.get('user_id')
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not user_id:
        return jsonify([]), 401

    sql = """
        SELECT p.id, t.subject, t.unit, t.type, p.student_note, p.score, p.date, p.is_corrected, p.ai_insight
        FROM tasks t
        JOIN progresses p ON t.id = p.task_id
        WHERE t.user_id = :uid 
          AND p.user_id = :uid 
          AND t.subject LIKE :sub 
          AND p.score < 100
          AND p.date BETWEEN :start AND :end
        ORDER BY p.date DESC
    """
    
    params = {
        'uid': user_id, 
        'sub': f'%{subject}%',
        'start': start_date,
        'end': end_date
    }
    
    try:
        results = db.session.execute(db.text(sql), params).fetchall()
        processed_data = []
        for row in results:
            pages, tags, clean_note, insight = parse_note_content(row.subject, row.student_note, row.ai_insight)
            processed_data.append({
                "id": row.id, "subject": row.subject, "unit": row.unit, "type": row.type,
                "score": row.score, "date": str(row.date),
                "is_corrected": bool(row.is_corrected),
                "pages": pages, "tags": tags, "clean_note": clean_note, "insight": insight
            })
        return jsonify(processed_data)
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@review_bp.route('/ai_diagnose', methods=['POST', 'OPTIONS'])
def ai_diagnose():
    if request.method == 'OPTIONS': return '', 200
    
    try:
        data = request.json or {}
        record_id = data.get('id')
        subject = data.get('subject', '社會')
        unit = data.get('unit', '')
        note = data.get('note', '')
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "缺少 User ID"}), 400

        publisher = get_subject_publisher(user_id, subject)
        config = get_subject_config(user_id, subject)
        grade_text = f"{config['grade']}年級" if config['grade'] <= 6 else f"國中{config['grade']-6}年級"
        
        user_question = f"教材背景：{grade_text}、版本：{publisher}。請針對學生在『{subject}』單元『{unit}』遇到的錯誤：『{note}』進行精簡診斷，200字內。"

        ai_response = ask_ai(user_id, user_question)

        if "error" in ai_response:
            return jsonify({"insight": f"💡 {ai_response['error']}"}), 200

        ai_result = ai_response.get('content', '').strip()

        if record_id and ai_result:
            db.session.execute(
                db.text("UPDATE progresses SET ai_insight = :insight WHERE id = :id"),
                {'insight': ai_result, 'id': record_id}
            )
            db.session.commit()
        
        return jsonify({"insight": ai_result})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "系統處理失敗"}), 500
    
@review_bp.route('/toggle', methods=['POST', 'OPTIONS'])
def toggle_review_status():
    if request.method == 'OPTIONS': return '', 200
    
    try:
        data = request.json
        record_id = data.get('id')
        is_corrected = data.get('is_corrected')

        if record_id is None:
            return jsonify({"error": "缺少 ID"}), 400

        sql = "UPDATE progresses SET is_corrected = :status WHERE id = :id"
        db.session.execute(db.text(sql), {
            'status': 1 if is_corrected else 0, 
            'id': record_id
        })
        db.session.commit()
        
        return jsonify({"message": "OK", "id": record_id, "new_status": is_corrected})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "更新失敗"}), 500
