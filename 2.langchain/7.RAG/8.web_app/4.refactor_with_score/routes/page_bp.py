"""페이지 라우트 — HTML 화면 서빙."""

from flask import Blueprint, render_template

page_bp = Blueprint("page", __name__)


@page_bp.get("/")
def index():
    return render_template("index.html")
