from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask
from apps.config import app_config_builder, app_blueprint_builder
from apps.config import page_not_found, internal_server_error
import os

# config_key 같은 경우 .env 파일에서부터 argument 변수를 가져온다

app = Flask(__name__)

app = app_config_builder(app, os.environ.get('CONFIG_MODE'))
app = app_blueprint_builder(app)
toolbar = DebugToolbarExtension(app)

# register_error_handler 는 자체적인 오류 핸들러를 추가하는 기능
# Blueprint로 등록된 커스텀 오류는 앱에서 저녕ㄱ에 등ㄹ혹한 것보다도 우선으로 표시된다.
# 그러나 404 오류는 Blueprint가 결정되기 전의 경로 결정의 레벨에서 발생하므로 404 오류는 처리할 수 없다
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)

if __name__ == '__main__':
   app.run(debug=True)
