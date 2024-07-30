from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf.form import FlaskForm
from wtforms.fields.simple import SubmitField

class UploadImageForm(FlaskForm):
    # 파일 업로드에 필요한 유효성 검증을 설정
    image = FileField(
        validators=[FileRequired(['Select An Image File']),
            FileAllowed(['jpg', 'jpeg', 'png'], 'Not A Supported Image Type')],
    )
    submit = SubmitField('Upload')

class DetectForm(FlaskForm):
    submit = SubmitField('Scan')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

