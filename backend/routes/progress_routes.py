from flask import Blueprint, request, jsonify
from models import Progress
from database import db
from datetime import datetime

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

@progress_bp.route('', methods=['POST', 'OPTIONS'])
def create_progress():
    if request.method == 'OPTIONS': return '', 200

    data = request.get_json()
    user_id = data.get('user_id') # 👈 取得前端傳來的 userId
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    # 確認任務是否屬於該用戶
    from models.task import Task
    task = Task.query.filter_by(id=data['task_id'], user_id=user_id).first()
    if not task:
        return jsonify({'error': 'Unauthorized'}), 404

    new_progress = Progress(
        task_id=data['task_id'],
        user_id=user_id,  # 👈 關鍵：存入資料庫
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        progress_percent=data.get('progress_percent', 0),
        student_note=data.get('student_note', ''),
        score=data.get('score', 0)
    )
    db.session.add(new_progress)
    db.session.commit()
    return jsonify(new_progress.to_dict()), 201

@progress_bp.route('/with_tasks', methods=['GET', 'OPTIONS'])
def get_progress_with_tasks():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify([]), 401

    from models.task import Task
    tasks = Task.query.filter_by(user_id=user_id).all()
    results = []

    for task in tasks:
        progress = Progress.query.filter_by(task_id=task.id).first()
        combined = {
            'task_id': task.id,
            'subject': task.subject,
            'title': task.title,
            'type': task.type,
            'unit': task.unit,
            'target_date': task.date.strftime('%Y-%m-%d') if task.date else None,
            'created_at': task.date.strftime('%Y-%m-%d') if task.date else None,
            'progress_percent': progress.progress_percent if progress else 0,
            'student_note': progress.student_note if progress else '',
            'score': progress.score if progress else '',
            'id': progress.id if progress else None
        }
        results.append(combined)

    return jsonify(results)


@progress_bp.route('/<int:progress_id>', methods=['PATCH', 'OPTIONS'])
def update_progress(progress_id):
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    progress = Progress.query.get(progress_id)
    if not progress:
        return jsonify({'error': 'Progress not found'}), 404

    # 檢查該進度的任務是否屬於該使用者
    from models.task import Task
    task = Task.query.filter_by(id=progress.task_id, user_id=user_id).first()
    if not task:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # 更新進度欄位
    if 'progress_percent' in data:
        progress.progress_percent = data['progress_percent']
        
        # 🔥 核心聯動：如果百分比達到 100，自動更新 Task 狀態
        from models.task import Task
        target_task = Task.query.get(progress.task_id)
        if target_task:
            if int(data['progress_percent']) == 100:
                target_task.status = '已完成'
            elif int(data['progress_percent']) == 0:
                target_task.status = '未開始'
            else:
                target_task.status = '進行中'

    if 'student_note' in data:
        progress.student_note = data['student_note']
    if 'teacher_feedback' in data:
        progress.teacher_feedback = data['teacher_feedback']
    if 'score' in data:
        progress.score = data['score']
    if 'date' in data:
        progress.date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    db.session.commit()
    return jsonify(progress.to_dict())

