from flask import Blueprint, request, jsonify
from database import db, get_exam_dates, update_all_subject_configs 
from sqlalchemy import text

config_bp = Blueprint('config', __name__)

# 1. 獲取/儲存版本配置
@config_bp.route('/publishers', methods=['GET', 'POST', 'OPTIONS'])
def handle_publishers():
    if request.method == 'OPTIONS': return '', 200
    
    # --- GET 邏輯 ---
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id: return jsonify({"error": "User ID required"}), 400
        sql = text("SELECT subject_name, publisher, grade FROM subject_configs WHERE user_id = :uid")
        results = db.session.execute(sql, {'uid': user_id}).fetchall()
        return jsonify([{"subject_name": r.subject_name, "publisher": r.publisher, "grade": r.grade} for r in results])

    # --- POST 邏輯 ---
    data = request.json
    user_id = data.get('user_id')
    configs = data.get('configs')
    if not user_id or not configs: return jsonify({"error": "Invalid data"}), 400

    try:
        for item in configs:
            # PostgreSQL 的語法是 ON CONFLICT (欄位名) DO UPDATE SET
            # 💡 注意：這要求 subject_configs 的 (user_id, subject_name) 必須是唯一索引 (Unique Index)
            upsert_sql = text("""
                INSERT INTO subject_configs (user_id, subject_name, publisher, grade)
                VALUES (:uid, :sub, :pub, :grade)
                ON CONFLICT (user_id, subject_name) 
                DO UPDATE SET publisher = EXCLUDED.publisher, grade = EXCLUDED.grade
            """)
            db.session.execute(upsert_sql, {
                'uid': user_id, 'sub': item['subject_name'], 
                'pub': item['publisher'], 'grade': item['grade']
            })
        db.session.commit()
        return jsonify({"message": "設定已成功儲存"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# 2. 獲取/儲存全域考期
@config_bp.route('/global', methods=['GET', 'POST', 'OPTIONS'])
def handle_global_config():
    if request.method == 'OPTIONS': return '', 200
    
    user_id = request.args.get('user_id') if request.method == 'GET' else request.json.get('user_id')
    if not user_id: return jsonify({"error": "Missing user_id"}), 400

    if request.method == 'GET':
        dates = get_exam_dates(user_id)
        return jsonify(dates)

    # POST 儲存
    data = request.json
    success = update_all_subject_configs(user_id, data.get('grade'), data.get('midterm_date'), data.get('final_date'))
    return jsonify({"message": "全域設定儲存成功"}) if success else (jsonify({"error": "失敗"}), 500)

# 3. 處理 AI 設定
@config_bp.route('/ai', methods=['GET', 'POST', 'OPTIONS'])
def handle_ai_settings():
    if request.method == 'OPTIONS': return '', 200
    
    user_id = request.args.get('user_id') if request.method == 'GET' else request.json.get('user_id')
    if not user_id: return jsonify({"error": "User ID required"}), 400
    
    if request.method == 'POST':
        data = request.json
        # PostgreSQL ON CONFLICT 語法修正
        sql = text("""
            INSERT INTO ai_settings (user_id, api_key, system_prompt, model_name, base_url)
            VALUES (:uid, :key, :prompt, :model, :url)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                api_key = EXCLUDED.api_key, 
                system_prompt = EXCLUDED.system_prompt, 
                model_name = EXCLUDED.model_name, 
                base_url = EXCLUDED.base_url
        """)
        db.session.execute(sql, {
            'uid': user_id, 'key': data.get('api_key'),
            'prompt': data.get('system_prompt'), 'model': data.get('model_name'),
            'url': data.get('base_url')
        })
        db.session.commit()
        return jsonify({"message": "AI 設定已儲存"})

    # GET 讀取
    sql = text("SELECT api_key, system_prompt, model_name, base_url FROM ai_settings WHERE user_id = :uid")
    res = db.session.execute(sql, {'uid': user_id}).fetchone()
    return jsonify({
        "api_key": res.api_key, "system_prompt": res.system_prompt,
        "model_name": res.model_name, "base_url": res.base_url
    }) if res else jsonify({})
