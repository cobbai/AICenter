import json
import os
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename

cv_bp = Blueprint("cv", __name__, url_prefix='/cv')


@cv_bp.route('/OCR/', methods=['GET', 'POST'])
def OCR():
    return "ok"