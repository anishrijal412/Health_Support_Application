# routes/forum.py
from flask import Blueprint

forum = Blueprint('forum', __name__)

@forum.route("/forum")
def forum_home():
    return "<h2>Forum Page — Coming Soon</h2>"
