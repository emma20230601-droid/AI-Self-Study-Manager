from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from database import db  # ✅ 確保引入 db 以執行儲存動作
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- 登入 API ---
@auth_bp.route('/login', methods=['POST'])
@cross_origin(origins="http://localhost:5173")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    
    # 這裡配合你原本的明碼比對邏輯
    # 注意：如果資料庫欄位是 password_hash，請確認 User model 的屬性名稱
    if user and user.password == password:  
        return jsonify({'user_id': user.id, 'username': user.username}), 200
    else:
        return jsonify({'error': '帳號或密碼錯誤'}), 401

# --- 註冊 API (新增) ---
@auth_bp.route('/register', methods=['POST'])
@cross_origin(origins="http://localhost:5173")
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '帳號與密碼不能為空'}), 400

    # 檢查帳號是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': '帳號已存在'}), 409

    # 建立新使用者 (依照你目前的明碼邏輯)
    # 注意：請確認你的 User model 定義中，密碼欄位是叫 password 還是 password_hash
    new_user = User(
        username=username,
        password=password  
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '註冊成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'註冊失敗: {str(e)}'}), 500