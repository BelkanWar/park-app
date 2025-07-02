# models.py
import random
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    photo_url = db.Column(db.String(255), default='default_user.png') # 用於使用者照片的路徑
    location_name = db.Column(db.String(255), default='未知區域') # 使用者目前位置的文字描述
    location_x = db.Column(db.Integer, default=random.randint(300, 600)) # 地圖上的 X 座標
    location_y = db.Column(db.Integer, default=random.randint(200, 400)) # 地圖上的 Y 座標

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'