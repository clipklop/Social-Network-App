from flask_login import LoginManager, login_user, logout_user, login_required
from flask import (
    Flask, g, render_template, flash, redirect, url_for)
from flask_bcrypt import check_password_hash

import models
import forms


DEBUG = True
PORT = 8000
HOST = '0.0.0.0'


app = Flask(__name__)
app.secret_key = 'aasdasdzczxc3213xxcxzx$@#!#234*'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.pw.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the db before each request."""
    g.db = models.DB
    g.db.connect()


@app.after_request
def after_request(response):
    """Close the db connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('Yay, you registered!', 'success')
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "success")
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='mischalove',
            email='mischa@mischa.com',
            password='password',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=True, host=HOST, port=PORT)
