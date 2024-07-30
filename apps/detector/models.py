from datetime import datetime

from apps.config import db

class UserImage(db.Model):
    __tablename__ = 'user_images'
    id = db.Column(db.Integer, primary_key=True)
    # user_id는 users 테이블의 id 컬럼을 외부 키로 설정한다
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_path = db.Column(db.String)
    is_detected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserImageTag(db.Model):
    __tablename__ = 'user_image_tags'

    id = db.Column(db.Integer, primary_key=True)
    user_image_id = db.Column(db.Integer, db.ForeignKey('user_images.id'))
    tag_name = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
