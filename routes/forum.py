# routes/forum.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.forum import ForumPost, ForumReply

forum = Blueprint('forum', __name__)

@forum.route('/forum')
@login_required
def forum_home():
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
    return render_template('forum.html', posts=posts)

@forum.route('/forum/new', methods=['POST'])
@login_required
def new_post():
    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        flash('Please fill out all fields.', 'warning')
        return redirect(url_for('forum.forum_home'))

    # Simple moderation placeholder (replace later with real API)
    if not is_safe_content(content):
        flash('⚠️ Post contains unsafe content and was blocked.', 'danger')
        return redirect(url_for('forum.forum_home'))

    post = ForumPost(user_id=current_user.id, title=title, content=content)
    db.session.add(post)
    db.session.commit()
    flash('✅ Post added successfully!', 'success')
    return redirect(url_for('forum.forum_home'))

@forum.route('/forum/<int:post_id>/reply', methods=['POST'])
@login_required
def reply_post(post_id):
    content = request.form.get('content')
    if not content:
        flash('Reply cannot be empty.', 'warning')
        return redirect(url_for('forum.forum_home'))

    if not is_safe_content(content):
        flash('⚠️ Reply blocked due to unsafe content.', 'danger')
        return redirect(url_for('forum.forum_home'))

    reply = ForumReply(post_id=post_id, user_id=current_user.id, content=content)
    db.session.add(reply)
    db.session.commit()
    flash('💬 Reply added successfully.', 'success')
    return redirect(url_for('forum.forum_home'))

def is_safe_content(text):
    """Temporary moderation placeholder"""
    banned_words = ['suicide', 'kill', 'self-harm', 'harm', 'abuse']
    return not any(word in text.lower() for word in banned_words)
