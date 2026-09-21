from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from services.movie_service import movie_service
from services.show_service import show_service
from services.theatre_service import theatre_service
from services.seat_service import seat_service

movie_bp = Blueprint('movie_bp', __name__)

def _get_current_city():
    city = request.args.get('city') or request.cookies.get('selected_city') or 'Kochi'
    return city.strip()

@movie_bp.route('/movies')
def movies_page():
    status = request.args.get('status')
    genre = request.args.get('genre')
    search = request.args.get('search')
    sort_by = request.args.get('sort')
    selected_city = _get_current_city()
    cities = theatre_service.get_cities()

    movies = movie_service.get_movies(status=status, genre=genre, search=search, sort_by=sort_by)
    return render_template(
        'movies.html',
        movies=movies,
        current_search=search,
        current_genre=genre,
        current_sort=sort_by,
        cities=cities,
        selected_city=selected_city
    )

@movie_bp.route('/movie/<movie_id>')
def movie_details(movie_id):
    selected_city = _get_current_city()
    movie = movie_service.get_movie_by_id(movie_id)
    if not movie:
        return render_template('error.html', error_message="Movie not found."), 404

    shows = show_service.get_shows(movie_id=movie_id, city=selected_city)
    theatres = theatre_service.get_theatres(city=selected_city)
    cities = theatre_service.get_cities()

    reviews = movie_service.get_reviews(movie_id) or []
    review_stats = movie_service.get_review_stats(movie_id) or {
        'total': 0,
        'avg_rating': 0.0,
        'counts': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
        'percentages': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    }

    user_logged_in = 'user_id' in session
    current_user_name = session.get('name', '')

    return render_template(
        'movie_details.html',
        movie=movie,
        shows=shows,
        theatres=theatres,
        cities=cities,
        selected_city=selected_city,
        reviews=reviews,
        review_stats=review_stats,
        user_logged_in=user_logged_in,
        current_user_name=current_user_name
    )

@movie_bp.route('/movie/<movie_id>/review', methods=['POST'])
def add_movie_review(movie_id):
    if 'user_id' not in session:
        flash("You must be logged in to submit a review.", "danger")
        return redirect(url_for('auth_bp.login_page', next=request.path))

    user_id = session['user_id']
    user_name = session.get('name', 'Anonymous User')
    rating = request.form.get('rating', 5)
    comment = request.form.get('comment', '')

    success, message = movie_service.add_review(movie_id, user_id, user_name, rating, comment)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for('movie_bp.movie_details', movie_id=movie_id))

@movie_bp.route('/showtimes')
def showtimes_page():
    movie_id = request.args.get('movie_id')
    selected_city = _get_current_city()
    movie = movie_service.get_movie_by_id(movie_id) if movie_id else None
    shows = show_service.get_shows(movie_id=movie_id, city=selected_city)
    theatres = theatre_service.get_theatres(city=selected_city)
    cities = theatre_service.get_cities()
    return render_template(
        'showtimes.html',
        movie=movie,
        shows=shows,
        theatres=theatres,
        cities=cities,
        selected_city=selected_city
    )

# API Endpoints
@movie_bp.route('/api/movies', methods=['GET'])
def api_get_movies():
    status = request.args.get('status')
    genre = request.args.get('genre')
    search = request.args.get('search')
    sort_by = request.args.get('sort')

    movies = movie_service.get_movies(status=status, genre=genre, search=search, sort_by=sort_by)
    return jsonify({'success': True, 'movies': movies})

@movie_bp.route('/api/movies/<movie_id>', methods=['GET'])
def api_get_movie_details(movie_id):
    movie = movie_service.get_movie_by_id(movie_id)
    if not movie:
        return jsonify({'success': False, 'message': 'Movie not found'}), 404
    return jsonify({'success': True, 'movie': movie})

@movie_bp.route('/api/movies/<movie_id>/reviews', methods=['GET', 'POST'])
def api_movie_reviews(movie_id):
    if request.method == 'GET':
        reviews = movie_service.get_reviews(movie_id)
        stats = movie_service.get_review_stats(movie_id)
        return jsonify({'success': True, 'reviews': reviews, 'stats': stats})

    if 'user_id' not in session and not (request.json and request.json.get('user_id')):
        return jsonify({'success': False, 'message': 'Authentication required to post review'}), 401

    data = request.json or request.form
    user_id = session.get('user_id') or data.get('user_id')
    user_name = session.get('name') or data.get('user_name', 'Anonymous')
    rating = data.get('rating', 5)
    comment = data.get('comment', '')

    success, message = movie_service.add_review(movie_id, user_id, user_name, rating, comment)
    if not success:
        return jsonify({'success': False, 'message': message}), 400

    return jsonify({'success': True, 'message': message})

@movie_bp.route('/api/shows', methods=['GET'])
def api_get_shows():
    movie_id = request.args.get('movie_id') or request.args.get('movieId')
    theatre_id = request.args.get('theatre_id') or request.args.get('theatreId')
    date_str = request.args.get('date')
    city = request.args.get('city') or _get_current_city()

    shows = show_service.get_shows(movie_id=movie_id, theatre_id=theatre_id, date_str=date_str, city=city)
    return jsonify({'success': True, 'city': city, 'shows': shows, 'count': len(shows)})

@movie_bp.route('/api/shows/<show_id>/seats', methods=['GET'])
def api_get_show_seats(show_id):
    seats = seat_service.get_seats_for_show(show_id)
    return jsonify({'success': True, 'seats': seats})
