from flask import Blueprint
from flask_cors import CORS, cross_origin

health_bp = Blueprint('health', __name__)

@health_bp.route("/api/v1/health", methods=['GET'])
@cross_origin()

def health():
    return {
        'status': 'ok'
    }