import pytest
import os
import shutil

from apps.create_app import create_app
from apps.config import db

from apps.auth.models import User
from apps.detector.models import UserImage, UserImageTag

@pytest.fixture
def fixture_app():
    # 설정 처리
    # 테스트용의 config를 사용하기 위해서 인수에 testing을 지정
    app = create_app("testing")

    # 데이터베이스를 이용하기 위한 선언
    app.app_context().push()

    # 테스트용 데이터베이스의 테이블을 작성
    with app.app_context():
        db.create_all()

    # 테스트용의 이미지 업로드 디렉터리를 작성
    os.mkdir(app.config["UPLOAD_FOLDER"])

    # 테스트를 실행
    yield app

    # 클린업 처리
    # user 테이블 레코드를 삭제
    User.query.delete()

    # user_image 테이블 레코드를 삭제
    UserImage.query.delete()

    # user_image_tags 테이블의 레코드를 삭제
    UserImageTag.query.delete()

    # 테스트용 이미지 업로드 디렉터리를 삭제
    shutil.rmtree(app.config["UPLOAD_FOLDER"])

    db.session.commit()

@pytest.fixture
def client(fixture_app):
    # Flask의 테스트용 클라이언트를 반환
    return fixture_app.test_client()
