from flask import Flask, request, make_response
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from database import db
from routes.task_routes import task_bp
from routes.progress_routes import progress_bp
from routes.auth_routes import auth_bp
from routes.review_routes import review_bp
from routes.teacher_routes import teacher_bp
from routes.config_routes import config_bp
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)

# ✅ 開放所有 API 路由給前端
#CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
#CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
# 允許你的 Vercel 網址連過來
#CORS(app, supports_credentials=True, origins=["https://ai-self-study-manager.vercel.app"])
# 1. 基礎設定
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# 2. 強制手動處理 OPTIONS 請求（這是解決 CORS 的絕招）
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "https://ai-self-study-manager.vercel.app")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response


# 註冊藍圖
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
    app.run(debug=True)






