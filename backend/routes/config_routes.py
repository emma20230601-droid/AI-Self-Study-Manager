from flask import Blueprint, request, jsonify
from database import db, get_exam_dates, update_all_subject_configs # ✅ 引入新工具函式
from sqlalchemy import text

config_bp = Blueprint('config', __name__)

@config_bp.route('/api/config/publishers', methods=['GET'])
def get_publishers():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
        
    sql = text("SELECT subject_name, publisher, grade FROM subject_configs WHERE user_id = :uid")
    results = db.session.execute(sql, {'uid': user_id}).fetchall()
    
    # 格式化為前端易用的字典清單
    config_list = [
        {"subject_name": row.subject_name, "publisher": row.publisher, "grade": row.grade} 
        for row in results
    ]
    return jsonify(config_list)

@config_bp.route('/api/config/publishers', methods=['POST'])
def save_publishers():
    data = request.json
    user_id = data.get('user_id')
    configs = data.get('configs') # 預期是一個清單 [{subject_name, publisher, grade}, ...]

    if not user_id or not configs:
        return jsonify({"error": "Invalid data"}), 400

    try:
        for item in configs:
            upsert_sql = text("""
                INSERT INTO subject_configs (user_id, subject_name, publisher, grade)
                VALUES (:uid, :sub, :pub, :grade)
                ON DUPLICATE KEY UPDATE publisher = :pub, grade = :grade
            """)
            db.session.execute(upsert_sql, {
                'uid': user_id, 
                'sub': item['subject_name'], 
                'pub': item['publisher'],
                'grade': item['grade']
            })
        db.session.commit()
        return jsonify({"message": "設定已成功儲存"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

# --- 新增程式碼：處理全域考期與年級設定 ---

@config_bp.route('/api/config/global', methods=['GET'])
def get_global_config():
    """ 獲取該使用者的考期設定 """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    
    dates = get_exam_dates(user_id)
    return jsonify(dates)

@config_bp.route('/api/config/global', methods=['POST'])
def save_global_config():
    """ 一次性儲存全科目的年級與考期 """
    data = request.json
    user_id = data.get('user_id')
    grade = data.get('grade')
    midterm_date = data.get('midterm_date')
    final_date = data.get('final_date')

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    success = update_all_subject_configs(user_id, grade, midterm_date, final_date)
    
    if success:
        return jsonify({"message": "全域設定（年級與考期）儲存成功"})
    else:
        return jsonify({"error": "儲存失敗"}), 500


@config_bp.route('/api/config/ai', methods=['GET', 'POST'])
def handle_ai_settings():
    user_id = request.args.get('user_id') if request.method == 'GET' else request.json.get('user_id')
    
    if request.method == 'POST':
        data = request.json
        # Upsert (新增或更新) AI 設定
        sql = text("""
            INSERT INTO ai_settings (user_id, api_key, system_prompt, model_name, base_url)
            VALUES (:uid, :key, :prompt, :model, :url)
            ON DUPLICATE KEY UPDATE 
                api_key = :key, system_prompt = :prompt, model_name = :model, base_url = :url
        """)
        db.session.execute(sql, {
            'uid': user_id,
            'key': data.get('api_key'),
            'prompt': data.get('system_prompt'),
            'model': data.get('model_name'),
            'url': data.get('base_url')
        })
        db.session.commit()
        return jsonify({"message": "AI 設定已儲存"})

    # GET 讀取時，API Key 可以做遮罩處理 (例如: sk-....abcd)
    sql = text("SELECT api_key, system_prompt, model_name, base_url FROM ai_settings WHERE user_id = :uid")
    res = db.session.execute(sql, {'uid': user_id}).fetchone()
    if res:
        return jsonify({
            "api_key": res.api_key, 
            "system_prompt": res.system_prompt,
            "model_name": res.model_name,
            "base_url": res.base_url
        })
    return jsonify({})