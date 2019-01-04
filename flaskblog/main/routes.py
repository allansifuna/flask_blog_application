from flask import render_template, request, Blueprint, flash
from flaskblog.models import Post, Subscribers, Comment
from flaskblog import db
from flaskblog.users.forms import SubscriptionForm

from flaskblog.users.utils import send_subscription_confirm_email

main = Blueprint('main', __name__)


@main.route('/', methods=['POST', 'GET'])
@main.route('/home', methods=['POST', 'GET'])
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_auth=1).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    comments = Comment.query.order_by(Comment.id.desc())
    list = Comment.query.all()
    ids = []
    for comment in list:
        ids.append(comment.comment.id)
    form = SubscriptionForm()
    if form.validate_on_submit():
        subscriber = Subscribers(email=form.email.data)
        db.session.add(subscriber)
        db.session.commit()
        send_subscription_confirm_email(subscriber)
        flash("You have successfully subscribed to my Blog. Thank you for subscribing", 'success')
    return render_template("home.html", posts=posts, title="home", form=form, comments=comments, ids=ids)


@main.route('/about')
def about():
    return render_template("about.html")
