from pathlib import Path
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask import render_template

basedir = Path(__file__).parent.parent


class BaseConfig:
    SECRET_KEY = "thisiskey"
    WTF_CSRF_SECRET_KEY = "thisiskey"

    # User 가 업로드하는 이미지의 저장 디렉토리
    UPLOAD_FOLDER = str(Path(basedir, "apps", "images"))

    # dectector 앱에 필요한 이미지 스캐닝 labels
    LABELS = [
        "unlabeled",
        "person",
        "bicycle",
        "car",
        "motorcycle",
        "airplane",
        "bus",
        "train",
        "truck",
        "boat",
        "traffic light",
        "fire hydrant",
        "street sign",
        "stop sign",
        "parking meter",
        "bench",
        "bird",
        "cat",
        "dog",
        "horse",
        "sheep",
        "cow",
        "elephant",
        "bear",
        "zebra",
        "giraffe",
        "hat",
        "backpack",
        "umbrella",
        "shoe",
        "eye glasses",
        "handbag",
        "tie",
        "suitcase",
        "frisbee",
        "skis",
        "snowboard",
        "sports ball",
        "kite",
        "baseball bat",
        "baseball glove",
        "skateboard",
        "surfboard",
        "tennis racket",
        "bottle",
        "plate",
        "wine glass",
        "cup",
        "fork",
        "knife",
        "spoon",
        "bowl",
        "banana",
        "apple",
        "sandwich",
        "orange",
        "broccoli",
        "carrot",
        "hot dog",
        "pizza",
        "donut",
        "cake",
        "chair",
        "couch",
        "potted plant",
        "bed",
        "mirror",
        "dining table",
        "window",
        "desk",
        "toilet",
        "door",
        "tv",
        "laptop",
        "mouse",
        "remote",
        "keyboard",
        "cell phone",
        "microwave",
        "oven",
        "toaster",
        "sink",
        "refrigerator",
        "blender",
        "book",
        "clock",
        "vase",
        "scissors",
        "teddy bear",
        "hair drier",
        "toothbrush",
    ]


class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'testing.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

    # 이미지 업로드처에 tests/detector/images 를 지정한다.
    UPLOAD_FOLDER = str(Path(basedir, "tests", "detector", "imgs"))


config_mode = {
    "testing": TestingConfig,
    "local": LocalConfig,
}

# SQLAlchemy를 인스턴스화한다
db = SQLAlchemy()

# LoginManager를 인스턴스화한다
login_manager = LoginManager()

csrf = CSRFProtect()

def app_config_builder(app, config_key):

    # 앱의 config 설정을 돋는다
    """
    config_mode = {
        "testing": TestingConfig,
        "local": LocalConfig,
    }
    """

    # login_view 속성에 미로그인 시 리다이렉트하는 엔드포인트를 지정
    login_manager.login_view = "auth.signup"
    # login_message 속성에 로그인 후에 표시할 메시지를 지정
    # 여기에서는 아무것도 표시하지 않도록 공백을 지정
    login_manager.login_message = ""

    app.config.from_object(config_mode[config_key])

    # SQLAlchemy와 앱을 연계한다
    db.init_app(app=app)

    # csrf를 앱과 연계
    csrf.init_app(app=app)

    # Migrate와 앱을 연계한다
    Migrate(app=app, db=db)

    # login_manager를 애플리케이션과 연계
    login_manager.init_app(app=app)

    return app


def app_blueprint_builder(app):

    from apps.auth import views as auth_views

    app.register_blueprint(blueprint=auth_views.auth, url_prefix="/auth")

    from apps.detector import views as dt_views

    app.register_blueprint(blueprint=dt_views.dt)

    return app


# error handler
def page_not_found(e):
        return render_template("404.html"), 404

def internal_server_error(e):
    return render_template("500.html"), 500


