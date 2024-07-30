from flask import Blueprint, render_template, redirect, url_for, flash, request
from apps.config import db
from apps.auth.forms import SignUpForm, LoginForm
from apps.auth.models import User
from flask_login import login_user, logout_user

auth = Blueprint(name='auth', import_name=__name__,
                 template_folder='templates',
                 static_folder='static')


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    # SignUpForm을 인스턴스화 한다
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )

        # check email duplication
        if user.is_duplicate_email():
            flash("You have already registered.")
            return redirect(url_for("auth.signup"))

        # register the user
        db.session.add(user)
        db.session.commit()

        # save user on session
        login_user(user=user)

        # 회원가입 환료 시의 리다이렉트될 곳을 detector.index로 변경한다
        next_ = request.args.get(key="next")
        if next_ is None or not next_.startswith("/"):
            next_ = url_for(endpoint="detector.index")
        return redirect(next_)

    return render_template("auth/signup.html", form=form)

@auth.route(rule="/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # check if user's email is in DB
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(password=form.password.data):
            login_user(user=user)
            return redirect(url_for(endpoint="detector.index"))

        flash(message="Invalid username or password.")

    return render_template(template_name_or_list="auth/login.html", form=form)

@auth.route(rule="/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
