from flask import Flask


def create_app(config='kingofthehill.config.Config'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        from kingofthehill import hash
        return app
