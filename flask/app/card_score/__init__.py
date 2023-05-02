from flask import Blueprint

bp = Blueprint('card_score', __name__)


from app.card_score import routes