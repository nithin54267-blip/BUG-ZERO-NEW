from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from models.db import init_db
from routes.analyze_routes import analyze_bp
from routes.auth_routes import auth_bp
from routes.history_routes import history_bp


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(analyze_bp, url_prefix="/api")
    app.register_blueprint(history_bp, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="Not found."), 404

    # Serve the frontend from the same server so one command runs everything.
    @app.get("/")
    def index():
        return send_from_directory(Config.FRONTEND_DIR, "index.html")

    @app.get("/<path:path>")
    def frontend(path):
        return send_from_directory(Config.FRONTEND_DIR, path)

    init_db()
    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
