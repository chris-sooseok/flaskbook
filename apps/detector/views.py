import numpy as np
import torch
import torchvision
from PIL import Image
from flask import Blueprint, render_template, current_app, send_from_directory, url_for, redirect, flash, request
from flask_login import current_user, login_required
from apps.config import db
from apps.auth.models import User
from apps.detector.models import UserImage, UserImageTag
import uuid
from pathlib import Path
from apps.detector.forms import UploadImageForm, DetectForm, DeleteForm
import random, cv2
from sqlalchemy.exc import SQLAlchemyError


dt = Blueprint(name='detector', import_name=__name__,
               template_folder='templates')


# join(UserImage, User.id == UserImage.user_id) would combine User and UserImage table displaying rows from User and UserImage where User.id == UserImage.user_id
# this join method also return a list of query results, not the query command itself

@dt.route('/')
def index():
    # 이미지 일람을 가져온다
    user_images = (
        db.session.query(User, UserImage).join(UserImage).filter(User.id == UserImage.user_id).all()
    )

    # 태그 일람을 가져온다
    user_image_tag_dict = {}
    for user_image in user_images:
        user_image_tags = (db.session.query(UserImageTag).filter(UserImageTag.user_image_id == user_image.UserImage.id).all())
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

    # 사용자가 detect 요청을 전송할 수 있도록 객체를 생성
    detector_form = DetectForm()

    # 사용자가 delete 요청을 전송할 수 있도록 객체를 생성
    delete_form = DeleteForm()

    return render_template("detector/index.html",
    user_images=user_images, user_image_tag_dict=user_image_tag_dict,
    detector_form=detector_form, delete_form=delete_form)


# 이러한 이미지들은 client 요청으로 개별적인 url로 다이렉트 될 수 있다.
@dt.route('/images:<path:filename>')
def image_file(filename):

    # 모델에 저장된 각 image_path 를 참조하여 이미지의 소스를 가지고 온다
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@dt.route("/upload", methods=['GET', 'POST'])
@login_required
def upload_image():
    form = UploadImageForm()

    if form.validate_on_submit():
        # 업로드된 이미지 파일을 취득
        file = form.image.data

        # 파일의 파일명과 확장자를 취득하고, 파일명을 uuid로 반환
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext

        # save the image
        image_path = Path(current_app.config['UPLOAD_FOLDER'], image_uuid_file_name)
        file.save(image_path)

        # save in DB
        user_image = UserImage(user_id=current_user.id, image_path=image_uuid_file_name)

        db.session.add(user_image)
        db.session.commit()

        return redirect(url_for('detector.index'))
    return render_template("detector/upload.html", form=form)

@dt.route("/detect/<string:image_id>", methods=['GET', 'POST'])
@login_required
def detect(image_id):
    # user_images 테이블로부터 레코드를 가져온다
    user_image = db.session.query(UserImage).filter(
        UserImage.id == image_id
    ).first()

    if user_image is None:
        flash("물체 감지 대상의 이미지가 존재하지 않습니다")
        return redirect(url_for('detector.index'))

    # 물체 감지 대상의 이미지 경로를 취득
    target_image_path = Path(
        current_app.config["UPLOAD_FOLDER"], user_image.image_path)

    # 물체 감지를 실행하여 태그와 변환 후의 이미지 경로를 취득
    tags, detected_image_file_name = exec_detect(target_image_path)

    try:
        # 데이터베이스에 태그와 변환 후의 이미지 경로 정보를 저장
        save_detected_image_tags(user_image, tags, detected_image_file_name)
    except SQLAlchemyError as e:
        flash("물체 감지 처리에서 오류가 발생")

        db.session.rollback()

        current_app.logger.error(e)

    return redirect(url_for('detector.index'))

def exec_detect(target_image_path):
    # read labels
    config_labels = current_app.config["LABELS"]
    # read images
    image = Image.open(target_image_path)

    # 이미지 데이터를 텐서 타입의 수치 데이터로 변환
    image_tensor = torchvision.transforms.functional.to_tensor(image)
    # 학습 완료 모델를 읽어 들이기
    model = torch.load(Path(current_app.root_path, "detector", "model.pt"))
    # 모델의 추론 모드로 전환
    model = model.eval()
    # 추론 실행
    output = model([image_tensor])[0]

    tags = []
    result_image = np.array(image.copy())

    # 학습 완료 모델이 감지한 각 물체만큼 이미지에 덧붙여 씀
    for box, label, score in zip(
        output["boxes"], output["labels"], output["scores"]
    ):
        if score > 0.8 and config_labels[label] not in tags:
            # 테두리 선의 색 결정
            color = make_color(config_labels)
            # 테두리 선의 작성
            line = make_line(result_image)
            # 감지 이미지의 테두리 선과 텍스트 라벨의 테두리 선의 위치 정보
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))
            # 이미지에 테두리 선을 덧붙여 씀
            cv2 = draw_lines(c1, c2, result_image, line, color)
            # 이미지에 텍스트 라벨을 덧붙여 씀
            cv2 = draw_texts(result_image, line, c1, cv2, color, config_labels, label)
            tags.append(config_labels[label])

    # 감지 후의 이미지 파일명을 생성
    detected_image_file_name = str(uuid.uuid4()) + '.jpg'

    # 이미지 복사처 경로를 취득
    detected_image_file_path = str(Path(current_app.config['UPLOAD_FOLDER'], detected_image_file_name))

    # 변환 후의 이미지 파일을 보존처로 복사
    cv2.imwrite(detected_image_file_path, cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))

    return tags, detected_image_file_name

def save_detected_image_tags(user_image, tags, detected_image_file_name):
    # 감지 후 이미지의 저장처 경로를 DB에 저장
    user_image.image_path = detected_image_file_name
    # 감지 플래그를 True로 설정
    user_image.is_detected = True
    db.session.add(user_image)

    # user_image_tags 레코드를 작성
    for tag in tags:
        user_image_tag = UserImageTag(
            user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)

    db.session.commit()

@dt.route("/images/search", methods=['GET', 'POST'])
def search():
    # list images
    user_images = db.session.query(User, UserImage).join(UserImage, User.id == UserImage.user_id)

    # GET 파라미터로부터 검색 단어를 가져온다
    print("-------------" + request.endpoint + "---------------")
    search_text = request.args.get("search")
    user_image_tag_dict = {}
    filtered_user_images = []

    # user_images를 반복하여 user_images에 연결된 정보를 검색한다
    for user_image in user_images:
        # 검색 단어가 빈 경우는 모든 태그를 가져온다
        if not search_text:
            user_images_tags = (db.session.query(UserImageTag).filter(UserImageTag.user_image_id == user_image.UserImage.id).all())
        else:
            # 검색 단어로 추출한 태그를 가져온다
            user_image_tags = (db.session.query(UserImageTag).filter(
                UserImageTag.user_image_id == user_image.UserImage.id).filter(UserImageTag.tag_name.like("%" + search_text + "%")
            ).all())

            # 태그를 찾을 수 없다면 반환하지 않는다
            if not user_image_tags:
                continue

            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id).all()
            )

        # user_image_id 를 키로 하는 사전에 태그 정보를 설정
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

        # 추출 결과의 user_image 정보를 배열 설정
        filtered_user_images.append(user_image)

    delete_form = DeleteForm()
    detector_form = DetectForm()

    return render_template("detector/index.html",
            # 추출한 user_images 배여을 전달한다
            user_images=filtered_user_images,
            # 이미지에 연결된 태그 일람의 사진을 전달
            user_image_tag_dict=user_image_tag_dict,
            delete_form=delete_form,
            detector_form=detector_form)


def make_color(labels):
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color

def make_line(result_image):
    line = round(0.002 * max(result_image.shape[0:2])) + 1
    return line

def draw_lines(c1, c2, result_image, line, color):
    # cv2 is OpenCV, a library commonly used for image and video processing
    cv2.rectangle(result_image, c1, c2, color,thickness=line)
    return cv2

def draw_texts(result_image, line, c1, cv2, color, labels, label):
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [255, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )

    return cv2

@dt.route("/images/delete/<string:image_id>", methods=['POST'])
@login_required
def delete_image(image_id):
    try:
        # user_image_tags 테이블로부터 레코드를 삭제
        db.session.query(UserImageTag).filter(
            UserImageTag.user_image_id == image_id
        ).delete()
        # user_images 테이블로부터 레코드를 삭제
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()

        db.session.commit()
    except SQLAlchemyError as e:
        flash("이미지 삭제 처리에서 오류 발생")
        # 로그 출력
        current_app.logger.error(e)
        db.session.rollback()

    return redirect(url_for('detector.index'))










