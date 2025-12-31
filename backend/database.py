from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


db = SQLAlchemy()

# --- 原有函式：保持不變以確保現有功能運作 ---

def get_subject_publisher(user_id, subject):
    """ 通用工具：從資料庫抓取指定學科的出版社設定 """
    try:
        sql = text("SELECT publisher FROM subject_configs WHERE user_id = :uid AND subject_name = :sub")
        result = db.session.execute(sql, {'uid': user_id, 'sub': subject}).fetchone()
        if result:
            return result[0]
        defaults = {"國語": "翰林", "數學": "康軒", "社會": "康軒", "自然": "康軒", "英文": "康軒"}
        return defaults.get(subject, "康軒")
    except Exception as e:
        print(f"查詢出版社出錯: {e}")
        return "康軒"

def get_subject_config(user_id, subject):
    """ 原有邏輯：回傳出版社與年級 """
    sql = text("SELECT publisher, grade FROM subject_configs WHERE user_id = :uid AND subject_name = :sub")
    result = db.session.execute(sql, {'uid': user_id, 'sub': subject}).fetchone()
    if result:
        return {"publisher": result[0], "grade": result[1]}
    return {"publisher": "康軒", "grade": 6}

# --- 新增功能：專門處理考期與擴充設定 ---

def get_exam_dates(user_id):
    """
    專門抓取考期設定。
    因為考期對所有科目通用，我們直接抓取該使用者在 subject_configs 裡存的日期。
    """
    try:
        # 抓取第一筆有日期的資料即可
        sql = text("SELECT midterm_date, final_date FROM subject_configs WHERE user_id = :uid AND midterm_date IS NOT NULL LIMIT 1")
        result = db.session.execute(sql, {'uid': user_id}).fetchone()
        
        if result:
            return {
                "midterm_date": result[0].strftime('%Y-%m-%d') if result[0] else None,
                "final_date": result[1].strftime('%Y-%m-%d') if result[1] else None
            }
        return {"midterm_date": None, "final_date": None}
    except Exception as e:
        print(f"查詢考期出錯: {e}")
        return {"midterm_date": None, "final_date": None}

def update_all_subject_configs(user_id, grade, midterm_date, final_date):
    """
    一次性更新該使用者所有科目的年級與考期。
    這解決了「年級」與「考期」全科目一致的問題。
    """
    try:
        sql = text("""
            UPDATE subject_configs 
            SET grade = :grade, midterm_date = :md, final_date = :fd 
            WHERE user_id = :uid
        """)
        db.session.execute(sql, {
            'uid': user_id,
            'grade': grade,
            'md': midterm_date,
            'fd': final_date
        })
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"更新全域設定出錯: {e}")
        return False
    

def get_user_ai_config(user_id):
    """
    從資料庫抓取特定用戶的 AI 配置
    """
    conn = db.connect('learning_system.db')
    conn.row_factory = db.Row
    cursor = conn.cursor()
    
    # 這裡的資料表結構應包含: api_key, system_prompt, model_name, base_url
    cursor.execute('SELECT * FROM ai_settings WHERE user_id = ?', (user_id,))
    config = cursor.fetchone()
    conn.close()
    
    return config