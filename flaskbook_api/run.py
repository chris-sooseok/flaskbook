import os

from flask import Flask

# 아래에 있는 config 같은경우 config 패키지에 있는 __init__.py 에서 정의된 경우이다.
from flaskbook_api.api.config import config
# 아래 api도 Blueprint의 객체로 api 패키지에 있는 __init__.py 에서 정의된 것이다.
from flaskbook_api.api import api

config_name = os.environ.get('CONFIG', "local")

app = Flask(__name__)
app.config.from_object(config[config_name])
# Bluprint를 애플리케이션에 등록
app.register_blueprint(api)


