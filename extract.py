import json
import os
from flaskblog import create_app, db
from flaskblog.models import User, Post, Comment
app = create_app()
app.app_context().push()
# users = User.query.all()
# comment = Comment.query.all()
# print(comment)
# print(help(db))
# print(help(app))
# db.drop(table='User')
# db.create_all()

# extract users
# with open('users.json', 'w') as f:
#     users = User.query.all()
#     people = []
#     for user in users:
#         for i in range(1):
#             id = user.id
#             is_auth = user.is_auth
#             username = user.username
#             email = user.email
#             password = user.password
#             active = user.is_online
#             pic = user.image_file
#             role = user.user_role
#             person = {}
#             person['is_auth'] = is_auth
#             person['id'] = id
#             person['username'] = username
#             person['email'] = email
#             person['active'] = active
#             person['pic'] = pic
#             person['role'] = role
#             person['password'] = password
#         people.append(person)
#     json.dump(people, f, indent=2)


# insert users
# with open('users.json') as f:
#     data = json.load(f)

# for user in data:
#     add = User(username=user['username'], id=user['id'], email=user['email'], password=user['password'], is_auth=user['is_auth'], is_online=user['active'], image_file=user['pic'], user_role=user['role'])
#     db.session.add(add)
#     db.session.commit()


# insertpost
# with open('db.json') as f:
#     data = json.load(f)
#     for post in data:
#         user = User.query.filter_by(id=post['user_id']).first()
#         add = Post(title=post['title'], content=post['content'], author=user)
#         db.session.add(add)
#         db.session.commit()

os.remove('flaskblog.log')
