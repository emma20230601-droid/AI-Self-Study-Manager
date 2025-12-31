import os
from flask import Flask, request, make_response
from flask_cors import CORS
from database import db
# 匯入藍圖
from routes.task_routes import task_bp
from routes.progress_routes import progress_bp
from routes.auth_routes import auth_bp
from routes.review_routes import review_bp
from routes.teacher_routes import teacher_bp
from routes.config_routes import config_bp
# 匯入原本的 config 作為備援
try:
    from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
except ImportError:
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)

# --- 資料庫配置 ---
# 優先讀取 Render 的 DATABASE_URL 環境變數
db_url = os.environ.get('DATABASE_URL')

if db_url:
    # 修正 Render 常見的 postgres:// 格式問題
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # 如果環境變數不存在，才使用 config.py 的設定
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
db.init_app(app)

# --- CORS 設定 ---
# 1. 基礎設定：允許認證資訊
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# 2. 強制手動處理 OPTIONS 預檢請求，解決 Vercel CORS 報錯
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        # 這裡建議換成你實際的 Vercel 網址以增加安全性，目前先用 *
        response.headers.add("Access-Control-Allow-Origin", "https://ai-self-study-manager.vercel.app")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# --- 自動建立資料庫表 ---
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# --- 註冊藍圖 ---
app.register_blueprint(task_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(review_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(config_bp)

@app.route('/')
def hello():
    return 'Flask Self-Study Backend OK!'

if __name__ == '__main__':
    # Render 會自動設定 PORT 環境變數，本地則預設 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
