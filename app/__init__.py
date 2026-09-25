import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
from app.models import db, AdminUser


migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "admin.login"
login_manager.login_message = "Please log in to access the admin panel."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id: str):
    return AdminUser.query.get(int(user_id))


def create_app(config_name: str = None):
    app = Flask(__name__, instance_relative_config=True)

    env = config_name or os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config[env])

    os.makedirs(app.instance_path, exist_ok=True)

    # ── Extensions ──
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # ── Health check ──
    @app.route("/healthz")
    def healthz():
        return jsonify(status="ok", env=env), 200

    # ── Blueprints ──
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app