import os

# 1. 取得雲端環境變數 (Render 會自動提供 DATABASE_URL)
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # 修正常見的連線協定名稱錯誤 (PostgreSQL 在 SQLAlchemy 需要使用 postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
else:
    # 2. 如果沒有環境變數，代表是在本地開發，使用你原本的 MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost/selfstudy_db'

SQLALCHEMY_TRACK_MODIFICATIONS = False
