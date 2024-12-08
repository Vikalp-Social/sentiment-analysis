from flask import Blueprint
from .timeline import timeline_bp
from .auth import auth_bp
from .health import health_bp
from .follow import follow_bp
from .profile import profile_bp
from .search import search_bp
from .status import status_bp

viaklp_bp = Blueprint('viaklp_bp', __name__)

viaklp_bp.register_blueprint(timeline_bp)
viaklp_bp.register_blueprint(auth_bp)
viaklp_bp.register_blueprint(health_bp)
viaklp_bp.register_blueprint(follow_bp)
viaklp_bp.register_blueprint(profile_bp)
viaklp_bp.register_blueprint(search_bp)
viaklp_bp.register_blueprint(status_bp)