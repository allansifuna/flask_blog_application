from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post, Subscribers, Comment
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   ResetRequestForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_reset_email, send_register_email

users = Blueprint('users', __name__)


# @users.route('/subscribe')
# def subscribe():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     form = SubscriptionForm()
#     if form.validate_on_submit():
#         subscriber = Subscribers(email=form.email.data)
#         db.session.add(subscriber)
#         db.session.commit()
#         send_subscription_confirm_email(subscriber)
#         flash("You have successfully subscribed to my Blog. Thank you for subscribing", 'success')
#     return render_template("home.html", form=form)


@users.route('/authenticate/<token>')
def authenticate(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.dashboard'))
    else:
        user.is_auth = 1
        db.session.commit()
        flash(f'Your email has been authenticated. You can now log in', 'success')
        return redirect(url_for('users.login'))


@users.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title="Dashboard")


@users.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect('home')
    else:
        if form.validate_on_submit():
            password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=password)
            db.session.add(user)
            db.session.commit()
            send_register_email(user)
            flash(f'Account created succesfully for {form.username.data}.', 'success')
            return redirect(url_for('users.dashboard'))

    return render_template("register.html", title='register', form=form)


@users.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    else:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash("Login unsuccessful. Please check email and password", "danger")
                return redirect(url_for('users.login'))
            if user.is_auth == 0:
                if current_user.is_authenticated:
                    flash("You need to Confirm you email address for you to log in", "info")
                    return redirect(url_for('users.logout'))
                flash("You need to Confirm you email address for you to log in", "info")
                return redirect(url_for('users.dashboard'))
            else:
                if user and bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    current_user.is_online = "Active"
                    db.session.commit()
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('main.home'))
                else:
                    flash("Login unsuccessful. Please check email and password", "danger")

    return render_template("login.html", title='login', form=form)


@users.route('/logout')
def logout():
    current_user.is_online = "Offline"
    db.session.commit()
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/accountDetails/<string:username>", methods=['GET', 'POST'])
@login_required
def accountDetails(username):
    if current_user.user_role != "Adminstrator":
        abort(403)
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(author=user)
    count = posts.count()
    return render_template('account_details.html', title='Account Details', count=count, user=user)


@users.route("/account_details", methods=['GET', 'POST'])
@login_required
def account_details():
    if current_user.is_auth == 0:
        if current_user.is_authenticated:
            flash("You need to Confirm you email address for you to log in", "info")
            return redirect(url_for('users.logout'))
        flash("You need to Confirm you email address for you to log in", "info")
        return redirect(url_for('users.dashboard'))
    posts = Post.query.filter_by(author=current_user)
    count = posts.count()
    return render_template('account_details.html', title='Account', count=count, user=current_user)


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if current_user.is_auth == 0:
        if current_user.is_authenticated:
            flash("You need to Confirm you email address for you to log in", "info")
            return redirect(url_for('users.logout'))
        flash("You need to Confirm you email address for you to log in", "info")
        return redirect(url_for('users.dashboard'))
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account_details'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pic/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@users.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password", 'info')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = password
        db.session.commit()
        flash(f'Your password has been updated. You can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template("reset_token.html", title="Reset Password", form=form)


@users.route('/user/<string:username>')
def user_posts(username):

    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(is_auth=1).order_by(Post.date_posted.desc()).filter_by(author=user).paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, title=username + "'s posts", user=user)


@users.route('/adminstrator/users')
@login_required
def users_table():
    if current_user.user_role != "Adminstrator":
        flash('You do not have Adminstrator priviledges to access this page.', 'danger')
        return redirect(url_for('main.home'))
    if current_user.is_auth == 0:
        if current_user.is_authenticated:
            flash("You need to Confirm you email address for you to log in", "info")
            return redirect(url_for('users.logout'))
        flash("You need to Confirm you email address for you to log in", "info")
        return redirect(url_for('users.dashboard'))
    users = User.query.order_by(User.id.desc()).all()
    posts = Post.query
    posts_count = Post.query.filter_by(is_auth=0).count()
    users_count = User.query.filter_by(is_auth=0).count()
    subscribers_count = Subscribers.query.count()
    online = User.query.filter_by(is_online="Active")
    comments = Comment.query
    count = online.count()
    return render_template('users.html', title="Admin", users_count=users_count, posts_count=posts_count, subscribers_count=subscribers_count, users=users, posts=posts, count=count, comments=comments, current_user=current_user)


@users.route('/adminstrator/subscribers')
@login_required
def subscribers():
    posts_count = Post.query.filter_by(is_auth=0).count()
    users_count = User.query.filter_by(is_auth=0).count()
    subscribers = Subscribers.query.all()
    subscribers_count = Subscribers.query.count()
    return render_template('subs.html', subscribers=subscribers, subscribers_count=subscribers_count, users_count=users_count, posts_count=posts_count, title="Admin")


@users.route('/admin_auth/<string:username>')
@login_required
def admin_auth(username):
    if current_user.user_role != "Adminstrator":
        abort(403)
    user = User.query.filter_by(username=username).first()
    user.is_auth = 1
    db.session.commit()
    return redirect(url_for('users.users_table'))
