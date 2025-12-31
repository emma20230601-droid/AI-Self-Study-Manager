import traceback
from flask import Blueprint, request, jsonify
from database import db, get_subject_publisher, get_subject_config
from datetime import datetime
# 🚀 引入通用 AI 服務
from ai_service import ask_ai 

teacher_bp = Blueprint('teacher', __name__)

# --- 路由 1：教師診斷分析看板數據 (不涉及 AI，保持原樣但優化效能) ---
@teacher_bp.route('/api/teacher/analysis', methods=['GET'])
def get_teacher_analysis():
    try:
        subject = request.args.get('subject', '')
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        sql = """
            SELECT t.unit, p.score, p.student_note, t.subject, p.date
            FROM tasks t
            JOIN progresses p ON t.id = p.task_id
            WHERE t.user_id = :uid 
              AND t.subject LIKE :sub 
              AND p.date BETWEEN :start AND :end
        """
        params = {'uid': user_id, 'sub': f'%{subject}%', 'start': start_date, 'end': end_date}
        results = db.session.execute(db.text(sql), params).fetchall()

        analysis = {
            "summary": {"total_count": len(results), "avg_score": 0, "failed_count": 0},
            "unit_stats": []
        }

        if not results:
            return jsonify(analysis)

        unit_map = {}
        total_score = 0
        for row in results:
            current_score = int(row.score) if row.score else 0
            total_score += current_score
            if current_score < 90:
                analysis["summary"]["failed_count"] += 1

            if row.unit not in unit_map:
                unit_map[row.unit] = {"total": 0, "count": 0}
            unit_map[row.unit]["total"] += current_score
            unit_map[row.unit]["count"] += 1

        analysis["summary"]["avg_score"] = round(total_score / len(results), 1)

        for unit, data in unit_map.items():
            avg = round(data["total"] / data["count"], 1)
            analysis["unit_stats"].append({
                "unit": unit,
                "count": data["count"],
                "avg": avg,
                "level": "精熟" if avg >= 95 else ("尚可" if avg >= 85 else "待加強")
            })
        
        analysis["unit_stats"] = sorted(analysis["unit_stats"], key=lambda x: x['avg'])
        return jsonify(analysis)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --- 路由 2：一鍵生成補救考卷 (🚀 去 Key 化版本) ---
@teacher_bp.route('/api/teacher/generate_quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.json
        subject = data.get('subject', '社會')
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400

        # 1. 獲取教材背景
        publisher = get_subject_publisher(user_id, subject)
        config = get_subject_config(user_id, subject)
        grade_text = f"{config['grade']}年級" if config['grade'] <= 6 else f"國中{config['grade']-6}年級"

        # 2. 撈取近期錯題
        sql = """
            SELECT t.unit, t.title, p.student_note, p.score
            FROM tasks t
            JOIN progresses p ON t.id = p.task_id
            WHERE t.user_id = :uid 
              AND t.subject = :sub 
              AND p.score < 100
            ORDER BY p.date DESC
            LIMIT 8
        """
        error_results = db.session.execute(db.text(sql), {'uid': user_id, 'sub': subject}).fetchall()

        if not error_results:
            return jsonify({"quiz_content": f"⚠️ 目前找不到您的 {subject} 科錯題紀錄。"})

        context_data = ""
        for i, row in enumerate(error_results):
            context_data += f"{i+1}. [{row.unit}] {row.title} (得分:{row.score})\n"

        # 3. 建立發送給 AI 的內容 (User Message)
        # 注意：我們只需提供事實數據，角色扮演(Prompt)可放在資料庫的 system_prompt 中
        user_message = f"""
請針對『{publisher}版』{grade_text}『{subject}』，根據以下真實錯題數據出一份補救練習：
{context_data}
要求：3 題選擇題與 2 題應用題，並附上答案與解析。
"""

        # 4. 🚀 呼叫 AI 服務 (自動處理 Key、URL 與超時)
        ai_response = ask_ai(user_id, user_message)

        if "error" in ai_response:
            return jsonify({"error": f"AI 老師暫時無法出題: {ai_response['error']}"}), 200

        return jsonify({
            "quiz_content": ai_response.get('content'),
            "publisher": publisher
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"系統錯誤: {str(e)}"}), 500