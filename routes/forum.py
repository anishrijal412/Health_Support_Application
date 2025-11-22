# routes/forum.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.forum import ForumPost, ForumReply
from models.flagged_log import FlaggedLog
from routes.moderation import is_safe_content_ai

def derive_category(detail: str, text: str) -> str:
    detail_lower = (detail or "").lower()
    text_lower = (text or "").lower()
    category_keywords = {
        "suicide": ["suicide", "self-harm", "self harm"],
        "violence": ["violence", "harm", "attack", "kill"],
        "abuse": ["abuse", "harassment", "bullying"],
        "threat": ["threat", "danger"],
    }

    for category, keywords in category_keywords.items():
        if any(keyword in detail_lower or keyword in text_lower for keyword in keywords):
            return category
    return "unspecified"


def log_flagged_content(user_id: int, text: str, reason: str, category: str, source_type: str):
    log_entry = FlaggedLog(
        user_id=user_id,
        text=text,
        reason=reason or "Content blocked by moderation.",
        category=category,
        source_type=source_type,
    )
    db.session.add(log_entry)
    db.session.commit()

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

    # Run moderation
    moderation_result = is_safe_content_ai(f"{title}\n{content}")
    is_safe = moderation_result[0]
    detail = moderation_result[1] if len(moderation_result) > 1 else "Content blocked by moderation."
    category = moderation_result[2] if len(moderation_result) > 2 else derive_category(detail, f"{title}\n{content}")

    # If unsafe → block and stop
    if not is_safe:
        log_flagged_content(
            current_user.id,
            f"{title}\n{content}",
            detail,
            category,
            "post",
        )
        flash(f'⚠️ Post blocked: {detail}', 'danger')
        return redirect(url_for('forum.forum_home'))

    # SAFE → Save the post
    post = ForumPost(
        user_id=current_user.id,
        title=title,
        content=content
    )
    db.session.add(post)
    db.session.commit()

    flash('✅ Post added successfully!', 'success')
    return redirect(url_for('forum.forum_home'))

@forum.route('/forum/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You are not authorized to edit this post.', 'danger')
        return redirect(url_for('forum.forum_home'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Please fill out all fields.', 'warning')
            return redirect(url_for('forum.edit_post', post_id=post_id))

        moderation_result = is_safe_content_ai(f"{title}\n{content}")
        is_safe = moderation_result[0]
        detail = moderation_result[1] if len(moderation_result) > 1 else "Content blocked by moderation."
        category = moderation_result[2] if len(moderation_result) > 2 else derive_category(detail, f"{title}\n{content}")
        if not is_safe:
            log_flagged_content(
                current_user.id,
                f"{title}\n{content}",
                detail,
                category,
                "post",
            )
            flash(f'⚠️ Update blocked: {detail}', 'danger')
            return redirect(url_for('forum.edit_post', post_id=post_id))

        post.title = title
        post.content = content
        db.session.commit()
        flash('✅ Post updated successfully!', 'success')
        return redirect(url_for('forum.forum_home'))

    return render_template('edit_post.html', post=post)

@forum.route('/forum/<int:post_id>/reply', methods=['POST'])
@login_required
def reply_post(post_id):
    content = request.form.get('content')
    if not content:
        flash('Reply cannot be empty.', 'warning')
        return redirect(url_for('forum.forum_home'))

    moderation_result = is_safe_content_ai(content)
    is_safe = moderation_result[0]
    detail = moderation_result[1] if len(moderation_result) > 1 else "Content blocked by moderation."
    category = moderation_result[2] if len(moderation_result) > 2 else derive_category(detail, content)
    if not is_safe:
        log_flagged_content(
            current_user.id,
            content,
            detail,
            category,
            "reply",
        )
        flash(f'⚠️ Reply blocked: {detail}', 'danger')
        return redirect(url_for('forum.forum_home'))

    reply = ForumReply(
        post_id=post_id, 
        user_id=current_user.id, 
        content=content
    )
    db.session.add(reply)
    db.session.commit()

    flash('💬 Reply added successfully.', 'success')
    return redirect(url_for('forum.forum_home'))



@forum.route('/forum/edit-reply/<int:reply_id>', methods=['GET', 'POST'])
@login_required
def edit_reply(reply_id):
    reply = ForumReply.query.get_or_404(reply_id)
    if reply.user_id != current_user.id:
        flash('You are not authorized to edit this reply.', 'danger')
        return redirect(url_for('forum.forum_home'))

    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Reply cannot be empty.', 'warning')
            return redirect(url_for('forum.edit_reply', reply_id=reply_id))

        moderation_result = is_safe_content_ai(content)
        is_safe = moderation_result[0]
        detail = moderation_result[1] if len(moderation_result) > 1 else "Content blocked by moderation."
        category = moderation_result[2] if len(moderation_result) > 2 else derive_category(detail, content)
        if not is_safe:
            log_flagged_content(
                current_user.id,
                content,
                detail,
                category,
                "reply",
            )
            flash(f'⚠️ Update blocked: {detail}', 'danger')
            return redirect(url_for('forum.edit_reply', reply_id=reply_id))

        reply.content = content
        db.session.commit()
        flash('✅ Reply updated successfully!', 'success')
        return redirect(url_for('forum.forum_home'))

    return render_template('edit_reply.html', reply=reply)


@forum.route('/forum/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('forum.forum_home'))

    ForumReply.query.filter_by(post_id=post.id).delete()
    db.session.delete(post)
    db.session.commit()
    flash('🗑️ Post and its replies deleted successfully.', 'success')
    return redirect(url_for('forum.forum_home'))


@forum.route('/forum/delete-reply/<int:reply_id>', methods=['POST'])
@login_required
def delete_reply(reply_id):
    reply = ForumReply.query.get_or_404(reply_id)
    if reply.user_id != current_user.id:
        flash('You are not authorized to delete this reply.', 'danger')
        return redirect(url_for('forum.forum_home'))

    db.session.delete(reply)
    db.session.commit()
    flash('🗑️ Reply deleted successfully.', 'success')
    return redirect(url_for('forum.forum_home'))
