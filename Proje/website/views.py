import random
import string
from flask import Blueprint, render_template, request, flash, redirect,url_for
from flask_login import login_required, current_user,logout_user
from website.forms import GroupForm, OylamaForm
from .models import Group, Member, Poll, User,Vote
from . import db
import json
from .models import get_user_votes,get_user_groups
from .decorators import admin_required 
from datetime import datetime,timedelta

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

def create_vote_code():
    """Rastgele bir oy verme kodu oluşturur."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=7))

@views.route('/create_group', methods=['GET', 'POST'])
@login_required
@admin_required
def create_group():
    form = GroupForm()
    if form.validate_on_submit():
        name = form.name.data

        # Valid email adreslerini topluyoruz
        valid_emails = [email_form.email.data for email_form in form.emails if email_form.email.data.strip()]

        if not valid_emails:
            flash("En az bir geçerli email adresi girmelisiniz.", category='error')
            return redirect(url_for('views.create_group'))

        # Grup oluşturma işlemleri
        new_group = Group(name=name, created_by=current_user.id)
        db.session.add(new_group)
        db.session.commit()

        for email in valid_emails:
            new_member = Member(group_id=new_group.id, email=email)
            db.session.add(new_member)

        db.session.commit()
        flash('Grup başarıyla oluşturuldu!', category='success')
        return redirect(url_for('views.home'))

    return render_template('create_group.html', user=current_user, form=form)

@views.route('/create_poll', methods=['GET', 'POST'])
@login_required
@admin_required
def create_poll():
    form = OylamaForm()
    user_groups = Group.query.join(Member).filter(Member.user_id == current_user.id).all()
    form.group_id.choices = [(group.id, group.name) for group in user_groups]

    if form.validate_on_submit():
        question = form.question.data
        options = request.form.getlist('options')  # Formdan gelen tüm seçenekleri al
        group_id = form.group_id.data
        days = form.days.data
        hours = form.hours.data
        minutes = form.minutes.data

        duration = timedelta(days=days, hours=hours, minutes=minutes)  # Aktif kalma süresini oluşturma

        # Oylamanın bitiş zamanını hesaplama
        end_time = datetime.utcnow() + duration

        vote_code = Poll.generate_vote_code()

        new_poll = Poll(
            question=question,
            options=json.dumps(options),  # Seçenekleri JSON formatında sakla
            group_id=group_id,
            created_by=current_user.id,
            vote_code=vote_code,
            end_time=end_time
        )
        db.session.add(new_poll)
        db.session.commit()

        flash(f"Oylama başarıyla oluşturuldu! \nOylama Katılım Kodu: {vote_code}", category='success')
        return redirect(url_for('views.home'))

    return render_template('create_poll.html', user=current_user, form=form)

@views.route('/vote/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def vote(poll_id):
    poll = Poll.query.get(poll_id)
    if not poll:
        flash('Oylama bulunamadı.', category='error')
        return redirect(url_for('views.home'))

    # Kullanıcının bu oylamaya daha önce katılıp katılmadığını kontrol etme
    existing_vote = Vote.query.filter_by(user_id=current_user.id, poll_id=poll_id).first()
    if existing_vote:
        flash('Bu oylamaya zaten katıldınız.', category='error')
        return redirect(url_for('views.home'))

    # Oylama süresi kontrolü
    if poll.end_time and poll.end_time < datetime.utcnow():
        flash('Oylama süresi dolmuştur, oy kullanamazsınız.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        choice = request.form.get('choice')
        new_vote = Vote(user_id=current_user.id, poll_id=poll_id, choice=choice)
        db.session.add(new_vote)
        db.session.commit()

        flash('Oy başarıyla gönderildi!', category='success')
        return redirect(url_for('views.home'))

    options = poll.get_options()
    return render_template("vote.html", user=current_user, poll=poll, options=options)

@views.route('/poll/<int:poll_id>/results')
@login_required
def view_results(poll_id):
    poll = Poll.query.get(poll_id)
    if not poll:
        flash('Anket bulunamadı.', category='error')
        return redirect(url_for('views.home'))

    # Bitiş zamanını kontrol et
    if poll.end_time and poll.end_time > datetime.utcnow():
        flash('Oylama sonuçları henüz erişilebilir değil.', category='error')
        return redirect(url_for('views.home'))

    votes = Vote.query.filter_by(poll_id=poll_id).all()

    # Oyların sayısını hesaplama
    total_votes = len(votes)

    # Tüm seçenekleri alma
    options = poll.get_options()

    # Seçeneklerin oy sayılarını hesaplama
    option_vote_counts = {}
    
    for option in options:
        option_vote_counts[option] = 0

    for vote in votes:
        if vote.choice in option_vote_counts:
            option_vote_counts[vote.choice] += 1

    return render_template("poll_results.html", user=current_user, poll=poll, option_vote_counts=option_vote_counts, total_votes=total_votes)

@views.route('/polls')
@login_required
def list_polls():
    user_group_ids = [member.group_id for member in current_user.groups]
    available_polls = Poll.query.filter(Poll.group_id.in_(user_group_ids)).all()
    
    return render_template("polls.html", user=current_user, polls=available_polls)

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))