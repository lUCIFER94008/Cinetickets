from flask import Blueprint, render_template, jsonify
from services.movie_service import movie_service
from services.theatre_service import theatre_service
from services.mongodb_service import test_connection, get_db

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    now_showing = movie_service.get_movies(status='now_showing')
    coming_soon = movie_service.get_movies(status='coming_soon')
    theatres = theatre_service.get_theatres()
    hero_movies = now_showing[:3] if now_showing else []

    return render_template('home.html', 
                           now_showing=now_showing, 
                           coming_soon=coming_soon, 
                           theatres=theatres, 
                           hero_movies=hero_movies)

@main_bp.route('/health')
def health_check():
    connected = test_connection()
    if connected:
        return jsonify({'status': 'ok', 'database': 'connected'}), 200
    else:
        return jsonify({'status': 'error', 'database': 'disconnected'}), 503

@main_bp.route('/api/admin/stats')
def admin_stats():
    db = get_db()
    total_users = db.users.count_documents({})
    total_movies = db.movies.count_documents({})
    total_theatres = db.theatres.count_documents({})
    total_shows = db.shows.count_documents({})
    total_bookings = db.bookings.count_documents({})

    revenue_agg = list(db.bookings.aggregate([
        {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
    ]))
    total_revenue = revenue_agg[0]['total'] if revenue_agg else 0.0

    return jsonify({
        'success': True,
        'stats': {
            'totalUsers': total_users,
            'totalMovies': total_movies,
            'totalTheatres': total_theatres,
            'totalShows': total_shows,
            'totalBookings': total_bookings,
            'totalRevenue': total_revenue
        }
    })
