from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user, remember=True)
                if user.is_admin:  # Yönetici kontrolü
                    flash('Admin olarak giriş yapıldı!', category='success')
                else:
                    flash('Giriş yapıldı!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Yanlış şifre, tekrar deneyiniz.', category='error')
        else:
            flash('Email eşleşmiyor.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email zaten mevcut.', category='error')
        elif len(email) < 4:
            flash('Email 3 karakterden daha fazla olmalı.', category='error')
        elif len(first_name) < 2:
            flash('İsminiz 1 karakterden uzun olmalı.', category='error')
        elif password1 != password2:
            flash('Şifreler eşleşmiyor.', category='error')
        elif len(password1) < 7:
            flash('Şifre en az 7 karakter olmalıdır.', category='error')
        else:
            hashed_password = bcrypt.generate_password_hash(password1).decode('utf-8')
            # Eğer belirli bir email adresine sahip bir kullanıcı kaydediliyorsa, admin olarak işaretle
            if email == "admin@gmail.com":
                new_user = User(email=email, first_name=first_name, password=hashed_password, is_admin=True)
            else:
                new_user = User(email=email, first_name=first_name, password=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Hesap Oluşturuldu!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)