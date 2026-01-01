from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

db = SQLAlchemy()

# ✅ 新增：定義資料表結構，這會讓 db.create_all() 知道要建立 subject_configs
class SubjectConfig(db.Model):
    __tablename__ = 'subject_configs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    subject_name = db.Column(db.String(50), nullable=False)
    publisher = db.Column(db.String(50), default='康軒')
    grade = db.Column(db.Integer, default=6)
    midterm_date = db.Column(db.Date, nullable=True)
    final_date = db.Column(db.Date, nullable=True)
    # 設定複合唯一索引，防止重複資料
    __table_args__ = (db.UniqueConstraint('user_id', 'subject_name', name='_user_subject_uc'),)

# ✅ 新增：AI 設定資料表定義
class AISetting(db.Model):
    __tablename__ = 'ai_settings'
    user_id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(255))
    system_prompt = db.Column(db.Text)
    model_name = db.Column(db.String(50))
    base_url = db.Column(db.String(255))

# --- 修改原有函式，移除 SQLite 殘留邏輯 ---

def get_subject_publisher(user_id, subject):
    try:
        sql = text("SELECT publisher FROM subject_configs WHERE user_id = :uid AND subject_name = :sub")
        result = db.session.execute(sql, {'uid': user_id, 'sub': subject}).fetchone()
        if result:
            return result[0]
        return "康軒"
    except Exception as e:
        print(f"查詢出版社出錯: {e}")
        return "康軒"

def get_exam_dates(user_id):
    try:
        # PostgreSQL 日期處理需注意類型
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
        # 確保日期格式正確或為 None
        md = midterm_date if midterm_date else None
        fd = final_date if final_date else None
        
        sql = text("""
            UPDATE subject_configs 
            SET grade = :grade, midterm_date = :md, final_date = :fd 
            WHERE user_id = :uid
        """)
        db.session.execute(sql, {'uid': user_id, 'grade': grade, 'md': md, 'fd': fd})
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"更新全域設定出錯: {e}")
        return False

# ❌ 刪除原本的 get_user_ai_config，因為它使用了 conn = db.connect('learning_system.db')
# ✅ 改用 SQLAlchemy 版本的 AI 讀取
def get_user_ai_config(user_id):
    try:
        sql = text("SELECT * FROM ai_settings WHERE user_id = :uid")
        result = db.session.execute(sql, {'uid': user_id}).fetchone()
        return result
    except Exception as e:
        print(f"讀取 AI 設定出錯: {e}")
        return None


