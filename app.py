from flask import Flask
import config
from auth import register_auth_routes
from routes import register_main_routes

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Register all routes
register_auth_routes(app)
register_main_routes(app)

if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=config.PORT)