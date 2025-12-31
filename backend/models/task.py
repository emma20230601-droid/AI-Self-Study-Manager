from database import db

class Task(db.Model):
    __tablename__ = 'tasks'  # ✅ 明確指定表名

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(20))
    title = db.Column(db.String(100))
    type = db.Column(db.String(20))
    date = db.Column(db.Date)
    status = db.Column(db.String(100))
    unit = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #user = db.relationship('User', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'title': self.title,
            'type': self.type,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'status': self.status,
            'unit': self.unit,
            'user_id': self.user_id
        }
