from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post, Comment, User, Subscribers
from flaskblog.posts.forms import PostForm, CommentForm
posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['POST', 'GET'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been succesfully created", 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New post', form=form, legend="New Post", button="Post")


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['POST', 'GET'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.user_role != "Adminstrator":
        if post.author != current_user:
            abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been Updated', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update post', form=form, legend="Update Post", button="Update")


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.user_role != "Adminstrator":
        if post.author != current_user:
            abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


# @posts.route('/user/<string:username>')
# def user_posts(username):
#     page = request.args.get('page', 1, type=int)
#     user = User.query.filter_by(username=username).first_or_404()
#     # posts = Post.query.order_by(Post.date_posted.desc()).filter_by(author=user).paginate(page=page, per_page=5)
#     return render_template("user_posts.html", posts=posts, title=username + "'s posts", user=user)


@posts.route("/adminstrator/posts_table")
@login_required
def posts_table():
    if current_user.user_role != "Adminstrator":
        flash('You do not have Adminstrator priviledges to access this page.', 'danger')
        return redirect(url_for('main.home'))
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    posts_count = Post.query.filter_by(is_auth=0).count()
    users_count = User.query.filter_by(is_auth=0).count()
    subscribers_count = Subscribers.query.count()
    return render_template('posts_table.html', posts=posts, users_count=users_count, posts_count=posts_count, subscribers_count=subscribers_count, title="Admin")


@posts.route('/admin_post_auth/<int:post_id>')
@login_required
def admin_post_auth(post_id):
    if current_user.user_role != "Adminstrator":
        abort(403)
    post = Post.query.filter_by(id=post_id).first()
    post.is_auth = 1
    db.session.commit()
    return redirect(url_for('posts.posts_table'))


@posts.route('/comment/<int:post_id>', methods=['GET', 'POST'])
@login_required
def comment(post_id):
    post = Post.query.filter_by(id=post_id).first()
    comments = Comment.query.order_by(Comment.id.desc())
    form1 = CommentForm()
    if form1.validate_on_submit():
        post_comment = Comment(comment=post, comment_author=current_user, content=form1.comment.data)
        db.session.add(post_comment)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('comment.html', form1=form1, post=post, comments=comments)


@posts.route('/admin/comments')
def admin_comments():
    comments = Comment.query.all()
    posts_count = Post.query.filter_by(is_auth=0).count()
    users_count = User.query.filter_by(is_auth=0).count()
    subscribers_count = Subscribers.query.count()
    return render_template('admin_comments.html', title='Admin', subscribers_count=subscribers_count, users_count=users_count, posts_count=posts_count, comments=comments)
