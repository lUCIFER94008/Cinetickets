import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'cinetickets_super_secret_key_2026')

# Import Blueprints
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.movie_routes import movie_bp
from routes.booking_routes import booking_bp
from routes.payment_routes import payment_bp
from routes.profile_routes import profile_bp
from routes.admin_routes import admin_bp

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(movie_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)


from utils.auth import get_current_user
from services.mongodb_service import test_connection, MONGO_DB_NAME

# Global Jinja Context Processor
@app.context_processor
def inject_user():
    user = get_current_user()
    return dict(current_user=user)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message="Page not found (404)."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_message="Internal server error (500). Please try again later."), 500

if __name__ == '__main__':
    connected = test_connection()
    status_str = "Connected" if connected else "Disconnected / Error"
    
    print("\n=================================")
    print("CineTickets")
    print("=================================")
    print(f"MongoDB: {status_str}")
    print(f"Database: {MONGO_DB_NAME}")
    print("Flask: Ready")
    print("URL: http://127.0.0.1:5000")
    print("=================================\n")

    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

