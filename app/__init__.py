from flask import Flask

server = Flask(__name__)

from app.routes import configure_routes

configure_routes(server)
