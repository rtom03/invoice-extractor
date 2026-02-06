import os
from flask import Flask
from flask_cors import CORS
from db import init_db, seed_db
from routes.extract import extract_bp
from routes.health import health_bp
from routes.orders import orders_bp


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(health_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(extract_bp)

    init_db()
    seed_db()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
