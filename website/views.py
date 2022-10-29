from flask import Blueprint, render_template, request, flash, jsonify

views = Blueprint('views', __name__)


@views.route('/login.html', methods=['GET', 'POST'])
#@login_required
def home():
    return render_template("home.html")


