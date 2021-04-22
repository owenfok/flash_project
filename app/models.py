from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class infoEditions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(200))
    url = db.Column(db.String(200))
    desc = db.relationship('infoEditionsdesc', backref='editions', lazy='dynamic')


class infoEditionsdesc(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(200))
    infoeditions_id = db.Column(db.Integer, db.ForeignKey('info_editions.id'))


class cloudService(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(200))
    even = db.Column(db.String(200))


class mainProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    intro = db.Column(db.String(200))
    url = db.Column(db.String(200))
    icon = db.Column(db.String(200))


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    intro = db.Column(db.String(200))
    url = db.Column(db.String(200))
    desc = db.relationship('serviceType', backref='service', lazy='dynamic')


class serviceType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(200))
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))


class partnersContent(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_title = db.Column(db.String(100))
    content = db.Column(db.String(240))


class whysql(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    url = db.Column(db.String(240))
    content = db.relationship('whysqlContent', backref='whysql', lazy='dynamic')


class whysqlContent(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(240))
    whysql_id = db.Column(db.Integer, db.ForeignKey("whysql.id"))


class howtobuy(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(240))
    url = db.Column(db.String(240))


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_id = db.Column(db.Integer, db.ForeignKey("region.id"))
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"))
    phone = db.Column(db.String(200))
    email = db.Column(db.String(200))
    flag = db.Column(db.String(200))


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.String(100))
    regions = db.relationship('Contact', backref='region', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.region)


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(100))
    countrys = db.relationship('Contact', backref='country', lazy='dynamic')

    def __repr__(self):
        return ' {}'.format(self.country)


class Events(db.Model):
    Events_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Events_title = db.Column(db.String(100))
    Events_time = db.Column(db.String(200))
    Events_city = db.Column(db.String(200))
    Events_country = db.Column(db.String(200))
    Events_intro = db.Column(db.String(200))
