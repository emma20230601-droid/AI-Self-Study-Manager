from flask import Blueprint, request, jsonify
from models.task import Task
from models.progress import Progress  # 確保這裡引用正確
from database import db
from datetime import datetime

task_bp = Blueprint('task', __name__)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify([]), 401 

    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks])


@task_bp.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    new_task = Task(
        subject=data['subject'],
        title=data['title'],
        type=data['type'],
        date=date,
        status=data.get('status', '未完成'),
        unit=data.get('unit', ''),
        user_id=user_id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201


# task_routes.py

@task_bp.route('/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    data = request.get_json()
    user_id = data.get('user_id')  # 確保從前端 payload 拿到 user_id
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'error': 'Task not found or unauthorized'}), 404

    # 1. 更新任務基本欄位
    for field in ['subject', 'title', 'type', 'date', 'status', 'unit']:
        if field in data:
            if field == 'date':
                date_str = data[field][:10]
                setattr(task, field, datetime.strptime(date_str, '%Y-%m-%d').date())
            else:
                setattr(task, field, data[field])

    # 2. 🔥 聯動邏輯：同步更新 Progress 表
    if 'status' in data:
        progress = Progress.query.filter_by(task_id=task.id).first()
        
        if data['status'] == '已完成':
            if progress:
                progress.progress_percent = 100
            else:
                # 修正此處：確保包含 user_id，且 score 給予 None 而非空字串
                new_progress = Progress(
                    task_id=task.id,
                    user_id=user_id,  # 👈 補上這行，避免插入時 user_id 為空
                    date=datetime.now().date(),
                    progress_percent=100,
                    student_note='任務狀態由月曆標記為已完成',
                    score=0  # 👈 改成 0，避免 Data truncated 錯誤
                )
                db.session.add(new_progress)
        
        elif data['status'] == '未開始':
            if progress:
                progress.progress_percent = 0

    try:
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        db.session.rollback()
        print(f"❌ 更新失敗: {e}") # 這裡會印出剛才那個錯誤
        return jsonify({'error': str(e)}), 500


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    user_id = request.args.get('user_id')
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        # 🔥 在刪除 Task 之前，先手動把這筆任務的所有 Progress 刪掉
        # 這樣就不會觸發資料庫的外鍵保護報錯了
        Progress.query.filter_by(task_id=task_id).delete()
        
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500