# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from models import db, User
import os
import uuid # 用於生成唯一檔名
from werkzeug.utils import secure_filename # 確保檔名安全

app = Flask(__name__)

# 配置 SQLite 資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24) # 用於簽署 session cookies，務必設置一個安全的隨機字串

# 配置上傳檔案的資料夾
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 確保上傳資料夾存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db.init_app(app)

# 在應用程式啟動時創建資料庫表 (只在第一次運行或需要重置時執行)
with app.app_context():
    db.create_all()

# --- 輔助函數 ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 路由定義 ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('登入成功！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('使用者名稱或密碼錯誤。', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 檢查使用者名稱是否已存在
        if User.query.filter_by(username=username).first():
            flash('此使用者名稱已被註冊。', 'danger')
            return render_template('register.html', username=username)

        # 檢查密碼是否一致
        if password != confirm_password:
            flash('兩次輸入的密碼不一致。', 'danger')
            return render_template('register.html', username=username)

        # 處理照片上傳
        photo_url = 'default_user.png' # 預設照片
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '' and allowed_file(file.filename):
                # 生成唯一檔名
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + '_' + filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                photo_url = unique_filename # 只儲存檔名，前端用 /static/uploads/ 拼接

        new_user = User(username=username, photo_url=photo_url)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('註冊成功！請登入。', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'註冊失敗，請重試。錯誤：{e}', 'danger')

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('請先登入。', 'info')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user:
        # 園區地圖的尺寸 (配合前端 CSS)
        map_width = 800
        map_height = 600
        
        # 傳遞使用者位置給模板
        return render_template('dashboard.html', user=user, map_width=map_width, map_height=map_height)
    else:
        session.pop('user_id', None)
        flash('使用者資訊異常，請重新登入。', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('您已成功登出。', 'success')
    return redirect(url_for('login'))

# 提供上傳檔案的服務
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- 測試用的創建預設使用者，方便開發 ---
@app.route('/create_default_users')
def create_default_users():
    with app.app_context():
        try:
            if not User.query.filter_by(username='testuser').first():
                user1 = User(username='testuser')
                user1.set_password('password123')
                user1.photo_url = 'default_user.png' # 預設圖片
                user1.location_name = '行政大樓入口'
                user1.location_x = 200 # 假設的座標
                user1.location_y = 300 # 假設的座標
                db.session.add(user1)

            if not User.query.filter_by(username='alice').first():
                user2 = User(username='alice')
                user2.set_password('alicepass')
                user2.photo_url = 'https://via.placeholder.com/150/FF0000/FFFFFF?text=Alice' # 外部圖片
                user2.location_name = '休憩區涼亭'
                user2.location_x = 550 # 假設的座標
                user2.location_y = 150 # 假設的座標
                db.session.add(user2)

            db.session.commit()
            flash('預設測試使用者已創建/檢查完畢。', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'創建預設使用者時發生錯誤: {e}', 'danger')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)