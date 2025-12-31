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
db_url = os.environ.get('DATABASE_URL')
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
db.init_app(app)

# --- CORS 終極設定 ---
# 1. 基礎設定
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://ai-self-study-manager.vercel.app"}})

# 2. 全域攔截器：確保所有回應（包含報錯）都有 CORS 標頭
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "https://ai-self-study-manager.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Allow-Credentials"] = "true"
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

