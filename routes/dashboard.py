# routes/dashboard.py
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models.appointment import Appointment
from models.forum import ForumPost, ForumReply
from models.profile import Profile


dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
def root_redirect():
    return redirect(url_for('auth.login'))


@dashboard.route('/dashboard')
@login_required
def legacy_dashboard():
    return redirect(url_for('dashboard.home'))


@dashboard.route('/dashboard/home')
@login_required
def home():
    today = datetime.now().date()
    week_ahead = today + timedelta(days=7)

    profile = Profile.query.filter_by(user_id=current_user.id).first()
    medication_count = 0
    active_medications = []

    if profile:
        medication_count = sum(len(history.medications) for history in profile.medical_histories)
        for history in profile.medical_histories:
            active_medications.extend([med for med in history.medications if med.is_active])

    medication_reminder_stats = {
        "active": len(active_medications),
        "total": medication_count,
    }

    upcoming_appointments = (
        Appointment.query.filter(
            Appointment.user_id == current_user.id,
            Appointment.date >= today,
        )
        .order_by(Appointment.date.asc(), Appointment.time.asc())
        .all()
    )
    appointment_count = len(upcoming_appointments)
    next_five_appointments = upcoming_appointments[:5]
    appointment_dates_next_week = sorted({
        appt.date
        for appt in upcoming_appointments
        if appt.date <= week_ahead
    })

    forum_post_count = ForumPost.query.filter_by(user_id=current_user.id).count()
    forum_reply_count = ForumReply.query.filter_by(user_id=current_user.id).count()

    recent_posts = (
        ForumPost.query.filter_by(user_id=current_user.id)
        .order_by(ForumPost.created_at.desc())
        .limit(5)
        .all()
    )
    recent_replies = (
        ForumReply.query.filter_by(user_id=current_user.id)
        .order_by(ForumReply.created_at.desc())
        .limit(5)
        .all()
    )

    combined_activity = [
        {
            "type": "Post",
            "title": post.title,
            "timestamp": post.created_at,
        }
        for post in recent_posts
    ] + [
        {
            "type": "Reply",
            "title": f"Reply on {reply.post.title}" if reply.post else "Reply",
            "timestamp": reply.created_at,
        }
        for reply in recent_replies
    ]
    recent_activity = sorted(combined_activity, key=lambda item: item["timestamp"], reverse=True)[:5]

    chart_labels = [
        (today - timedelta(days=6 - i)).strftime("%a")
        for i in range(7)
    ]
    chart_data = [((i + len(active_medications)) % 5) + 1 for i in range(7)]

    active_days_this_week = len({
        item["timestamp"].date()
        for item in combined_activity
        if item.get("timestamp") and item["timestamp"].date() >= today - timedelta(days=6)
    })
    engagement_message = None
    if combined_activity:
        engagement_message = f"You have been active {active_days_this_week} day{'s' if active_days_this_week != 1 else ''} this week."

    return render_template(
        'dashboard.html',
        user=current_user,
        medication_count=medication_count,
        medication_reminder_stats=medication_reminder_stats,
        appointment_count=appointment_count,
        next_five_appointments=next_five_appointments,
        appointment_dates_next_week=appointment_dates_next_week,
        forum_post_count=forum_post_count,
        forum_reply_count=forum_reply_count,
        recent_activity=recent_activity,
        chart_labels=chart_labels,
        chart_data=chart_data,
        engagement_message=engagement_message,
    )