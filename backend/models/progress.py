from database import db
from datetime import date

class Progress(db.Model):
    __tablename__ = 'progresses'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)  # ✅ 修正
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ✅ 修正
    date = db.Column(db.Date, default=date.today)
    progress_percent = db.Column(db.Integer, default=0)
    student_note = db.Column(db.Text)
    teacher_feedback = db.Column(db.Text)
    score = db.Column(db.Float)
    is_corrected = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'progress_percent': self.progress_percent,
            'student_note': self.student_note,
            'teacher_feedback': self.teacher_feedback,
            'score': self.score
        }

