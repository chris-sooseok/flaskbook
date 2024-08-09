def test_index(client):
    rv = client.get("/")
    assert "Log In" in rv.data.decode()
    assert "Register New Image" in rv.data.decode()

def signup(client, username, email, password):

    data = dict(username=username, email=email, password=password)
    return client.post("/auth/signup", data=data, follow_redirects=True)

def test_index_signup(client):

    rv = signup(client,"test", "flaskbook@example.com", "<PASSWORD>")
    assert "test" in rv.data.decode()

    rv = client.get("/")
    assert "Log Out" in rv.data.decode()
    assert "Register New Image" in rv.data.decode()

def test_upload_no_auth(client):
    rv = client.get("/upload", follow_redirects=True)
    # 이미지 업로드 화면에 접근 불가
    assert "Upload" not in rv.data.decode()
    assert "Email" in rv.data.decode()
    assert "Password" in rv.data.decode()

def test_upload_signup_get(client):
    signup(client,"test", "flaskbook@example.com", "<PASSWORD>")
    rv = client.get("/upload")
    assert "Upload" in rv.data.decode()

from pathlib import Path
from flask.helpers import get_root_path
from werkzeug.datastructures import FileStorage

def upload_image(client, image_path):

    image = Path(get_root_path("tests"), image_path)

    test_file = (
        FileStorage(
            stream=open(image, "rb"),
            filename=Path(image_path).name,
            content_type="multipart/form-data",
        ),
    )

    data = dict(image=test_file)

    return client.post("/upload", data=data, follow_redirects=True)

def test_upload_signup_post_validate(client):
    signup(client, "test", "flaskbook@example.com", "<PASSWORD>")
    rv = upload_image(client,
                      "detector/testdata/test_invalid_file.txt")
    assert 'Not A Supported Image Type' in rv.data.decode()

from apps.detector.models import UserImage
def test_upload_signup_post(client):
    signup(client, "test", "flaskbook@example.com", "<PASSWORD>")
    rv = upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()
    assert user_image.image_path in rv.data.decode()


def test_detect_no_user_image(client):
    signup(client, "test", "flaskbook@example.com", "<PASSWORD>")
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    #
    rv = client.post("/detect/notxitstid", follow_redirects=True)
    assert "물체 감지 대상의 이미지가 존재하지 않습니다" in rv.data.decode()

def test_detect(client):
    signup(client, "test", "flaskbook@example.com", "<PASSWORD>")
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()

    rv = client.post(f"/detect/{user_image.id}", follow_redirects=True)
    user_image = UserImage.query.first()
    assert user_image.image_path in rv.data.decode()
    assert "dog" in rv.data.decode()

def test_detect_search(client):
    signup(client, "test", "flaskbook@example.com", "<PASSWORD>")
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()

    # 물체를 감지한다
    client.post(f"/detect/{user_image.id}", follow_redirects=True)

    rv = client.get("/images/search?search=dog")
    assert user_image.image_path in rv.data.decode()
    assert "dog" in rv.data.decode()

    # test 단어 검색
    rv = client.get("/images/search?search=test")
    assert user_image.image_path not in rv.data.decode()
    assert "dog" not in rv.data.decode()


def test_delete(client):
    signup(client, "test", "flaskbook@example.com", "<PASSWORD>")
    upload_image(client, "detector/testdata/test_valid_image.jpg")

    user_image = UserImage.query.first()
    image_path = user_image.image_path
    rv = client.post(f"/images/delete/{user_image.id}", follow_redirects=True)
    assert image_path not in rv.data.decode()

def test_custom_error(client):
    rv = client.get("/notfound")
    assert "404 Not Found" in rv.data.decode()




