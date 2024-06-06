from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/send', methods=['POST'])
@login_required
def send():
    receiver_username = request.form['receiver']
    message_content = request.form['message']
    receiver = User.query.filter_by(username=receiver_username).first()
    
    if receiver:
        new_message = Message(content=message_content, sender_id=current_user.id, receiver_id=receiver.id)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('sent'))
    else:
        flash('Receiver not found.', 'danger')
    
    return redirect(url_for('index'))

@app.route('/sent')
@login_required
def sent():
    return render_template('sent.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/messages')
@login_required
def messages():
    messages = Message.query.filter_by(receiver_id=current_user.id).all()
    return render_template('messages.html', messages=messages)

@app.route('/delete_message/<int:message_id>')
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.receiver_id == current_user.id:
        db.session.delete(message)
        db.session.commit()
        flash('Message deleted successfully.', 'success')
    else:
        flash('You do not have permission to delete this message.', 'danger')
    return redirect(url_for('messages'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
