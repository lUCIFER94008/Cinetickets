from flask import Blueprint, render_template, jsonify, request
from services.movie_service import movie_service
from services.theatre_service import theatre_service
from services.mongodb_service import test_connection, get_db

main_bp = Blueprint('main_bp', __name__)

def _get_current_city():
    city = request.args.get('city') or request.cookies.get('selected_city') or 'Kochi'
    return city.strip()

@main_bp.route('/')
def index():
    selected_city = _get_current_city()
    now_showing = movie_service.get_movies(status='now_showing')
    coming_soon = movie_service.get_movies(status='coming_soon')
    theatres = theatre_service.get_theatres(city=selected_city)
    cities = theatre_service.get_cities()
    hero_movies = now_showing[:3] if now_showing else []

    return render_template(
        'home.html',
        now_showing=now_showing,
        coming_soon=coming_soon,
        theatres=theatres,
        cities=cities,
        selected_city=selected_city,
        hero_movies=hero_movies
    )

@main_bp.route('/api/cities', methods=['GET'])
def api_get_cities():
    cities = theatre_service.get_cities(active_only=True)
    return jsonify({'success': True, 'cities': cities, 'count': len(cities)})

@main_bp.route('/api/theatres', methods=['GET'])
def api_get_theatres():
    city = request.args.get('city')
    theatres = theatre_service.get_theatres(city=city)
    return jsonify({'success': True, 'city': city or 'All', 'theatres': theatres, 'count': len(theatres)})

@main_bp.route('/api/theatres/<theatre_id>', methods=['GET'])
def api_get_theatre_by_id(theatre_id):
    theatre = theatre_service.get_theatre_by_id(theatre_id)
    if not theatre:
        return jsonify({'success': False, 'message': 'Theatre not found'}), 404
    return jsonify({'success': True, 'theatre': theatre})

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
    total_cities = db.cities.count_documents({})
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
            'totalCities': total_cities,
            'totalShows': total_shows,
            'totalBookings': total_bookings,
            'totalRevenue': total_revenue
        }
    })
