from flask import Flask
from flask import render_template, redirect, url_for, request, Blueprint

from .auth import login_required

app = Flask(__name__)

bp = Blueprint('base', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('basics/index.html')

@bp.route('/about')
@login_required
def about():
    return render_template('basics/about.html')
