from flask import Blueprint, request, jsonify
from database import db, get_subject_publisher, get_subject_config
import re, traceback
# 🚀 引入你剛寫好的通用 AI 服務
from ai_service import ask_ai, get_ai_config

review_bp = Blueprint('review', __name__)

def parse_note_content(subject, note, db_insight=None):
    """
    核心解析引擎：處理診斷內容
    """
    pages_match = re.search(r'[pP]\.?\s?\d+.*?\d+', note)
    pages = pages_match.group(0) if pages_match else ""
    
    tags = []
    insight = ""
    sub = str(subject or "")
    
    # 只有當資料庫「已經存有」AI 診斷時，才將其填入 insight
    if db_insight:
        insight = db_insight
    else:
        if "社會" in sub:
            if any(k in note for k in ['時序', '年份']): tags.append('🗓️ 時序')
        elif "數學" in sub:
            if any(k in note for k in ['計算', '算式']): tags.append('🧮 計算')
            if "單位" in note: tags.append('📏 單位細節')

    clean_note = re.sub(r'[pP]\.?\s?\d+.*?\d+', '', note).strip()
    return pages, tags, clean_note, insight


@review_bp.route('/list', methods=['GET'])
def get_review_list():
    subject = request.args.get('subject', '') 
    user_id = request.args.get('user_id')
    # 🚀 1. 接收前端傳來的日期參數
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # 🚀 2. 修改 SQL：加入日期過濾條件 p.date BETWEEN :start AND :end
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
    
    # 🚀 3. 將日期參數放入 params 字典中
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

@review_bp.route('/ai_diagnose', methods=['POST'])
def ai_diagnose():
    try:
        data = request.json or {}
        record_id = data.get('id')
        subject = data.get('subject', '社會')
        unit = data.get('unit', '')
        note = data.get('note', '')
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "缺少 User ID"}), 400

        print(f"📥 召喚 AI 老師 - ID: {record_id}")

        # 1. 獲取教材背景資訊
        publisher = get_subject_publisher(user_id, subject)
        config = get_subject_config(user_id, subject)
        grade_text = f"{config['grade']}年級" if config['grade'] <= 6 else f"國中{config['grade']-6}年級"
        
        # 2. 組合本次問題的內容 (這會傳給 ask_ai 作為 user_message)
        # 注意：我們不再需要在這裡組合整個 Prompt，因為 system_prompt 已經存在資料庫了
        user_question = f"目前的教材背景是：{grade_text}、版本：{publisher}。請針對學生在『{subject}』科單元『{unit}』遇到的錯誤內容：『{note}』進行精簡診斷，200字內。"

        # 3. 🚀 調用通用 AI 服務 (它會自動去資料庫抓你的 Key 和 關鍵字)
        ai_response = ask_ai(user_id, user_question)

        # 檢查是否有 error
        if "error" in ai_response:
            return jsonify({"insight": f"💡 {ai_response['error']}"}), 200

        ai_result = ai_response.get('content', '').strip()

        # 4. 💾 存入資料庫
        if record_id and ai_result:
            db.session.execute(
                db.text("UPDATE progresses SET ai_insight = :insight WHERE id = :id"),
                {'insight': ai_result, 'id': record_id}
            )
            db.session.commit()
            print(f"✅ AI 診斷已存入資料庫 ID: {record_id}")
        
        return jsonify({"insight": ai_result})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "系統處理失敗，請稍後再試"}), 500
    
@review_bp.route('/toggle', methods=['POST'])
def toggle_review_status():
    try:
        data = request.json
        record_id = data.get('id')
        is_corrected = data.get('is_corrected')

        if record_id is None:
            return jsonify({"error": "缺少 ID"}), 400

        # 將布林值轉為資料庫通常使用的 0 或 1 (視你的資料庫欄位類型而定)
        # 如果你的資料庫欄位是 BOOLEAN，直接傳 is_corrected 即可
        sql = "UPDATE progresses SET is_corrected = :status WHERE id = :id"
        db.session.execute(db.text(sql), {
            'status': 1 if is_corrected else 0, 
            'id': record_id
        })
        db.session.commit()
        
        return jsonify({"message": "狀態更新成功", "id": record_id, "new_status": is_corrected})

    except Exception as e:
        db.session.rollback()
        print(f"❌ 更新狀態失敗: {e}")

        return jsonify({"error": "更新失敗"}), 500
