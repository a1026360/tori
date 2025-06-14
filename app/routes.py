from flask import jsonify

def configure_routes(app):
    @app.route("/test", methods=["GET"])
    def home():
        return jsonify({"message": "Hello, World!"})

