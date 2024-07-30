from datetime import datetime
from apps.config import db, login_manager
from flask_login import UserMixin
# werkzeug 는 WSGI 툴킷으로 플라스크는 werkzeug를 바탕으로 만들어져 있으므로 기능을 이용할 수 있다w
from werkzeug.security import generate_password_hash, check_password_hash

# db.Model을 상속한 User 클래스를 작성
# User 클래스를 db.Model에 더해서 UserMixin을 상속한다
class User(db.Model, UserMixin):
    # 테이블명을 지정
    __tablename__ = 'users'

    # 컬럼을 지정
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # backref를 이용하여 relation 정보를 설정
    user_images = db.relationship('UserImage', backref='user', order_by='desc(UserImage.id)')


    # 비밀번호를 설정하기 위한 프로퍼티
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 비밀번호를 설정하기 위해 setter 함수로 해시화한 비밀번호를 설정
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # check password
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # check email duplication
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None

# 로그인하고 있는 사용자 정보를 취득하는 함수를 작성
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))