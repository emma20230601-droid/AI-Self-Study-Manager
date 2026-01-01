from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

db = SQLAlchemy()

# ✅ 修正：將類別名稱改為 SubjectConfig (避免與函式名衝突)
class SubjectConfig(db.Model):
    __tablename__ = 'subject_configs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    subject_name = db.Column(db.String(50), nullable=False)
    publisher = db.Column(db.String(50), default='康軒')
    grade = db.Column(db.Integer, default=6)
    midterm_date = db.Column(db.Date, nullable=True)
    final_date = db.Column(db.Date, nullable=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'subject_name', name='_user_subject_uc'),)

# AI 設定資料表
class AISetting(db.Model):
    __tablename__ = 'ai_settings'
    user_id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(255))
    system_prompt = db.Column(db.Text)
    model_name = db.Column(db.String(50))
    base_url = db.Column(db.String(255))

# --- 函式部分 ---

def get_subject_publisher(user_id, subject):
    try:
        sql = text("SELECT publisher FROM subject_configs WHERE user_id = :uid AND subject_name = :sub")
        result = db.session.execute(sql, {'uid': user_id, 'sub': subject}).fetchone()
        return result[0] if result else "康軒"
    except Exception as e:
        print(f"查詢出版社出錯: {e}")
        return "康軒"

# ✅ 補回遺失的函式：這是 review_routes.py 正在找的東西
def get_subject_config(user_id, subject):
    """ 供路由調用：回傳特定學科的出版社與年級 """
    try:
        sql = text("SELECT publisher, grade FROM subject_configs WHERE user_id = :uid AND subject_name = :sub")
        result = db.session.execute(sql, {'uid': user_id, 'sub': subject}).fetchone()
        if result:
            return {"publisher": result[0], "grade": result[1]}
        return {"publisher": "康軒", "grade": 6}
    except Exception as e:
        print(f"get_subject_config 出錯: {e}")
        return {"publisher": "康軒", "grade": 6}

def get_exam_dates(user_id):
    try:
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
    try:
        sql = text("""
            UPDATE subject_configs 
            SET grade = :grade, midterm_date = :md, final_date = :fd 
            WHERE user_id = :uid
        """)
        db.session.execute(sql, {'uid': user_id, 'grade': grade, 'md': midterm_date, 'fd': final_date})
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

def get_user_ai_config(user_id):
    try:
        sql = text("SELECT * FROM ai_settings WHERE user_id = :uid")
        return db.session.execute(sql, {'uid': user_id}).fetchone()
    except Exception as e:
        return None
