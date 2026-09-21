import unittest
from datetime import datetime, timedelta
from app import app
from services.show_service import show_service
from services.mongodb_service import get_db

class TestWeeklyShowtimeSystem(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_weekly_dates_helper(self):
        dates = show_service.get_weekly_dates()
        self.assertEqual(len(dates), 7)
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(dates[0]['date_str'], today_str)
        self.assertTrue(dates[0]['is_today'])
        self.assertIn('day_name', dates[0])
        self.assertIn('day_num', dates[0])
        self.assertIn('month_name', dates[0])
        print(f"✅ Test 01 Passed: Generated 7 dynamic dates starting {dates[0]['formatted']}.")

    def test_02_api_showtimes_by_date(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        res_today = self.app.get(f'/api/showtimes?city=Kochi&date={today_str}')
        self.assertEqual(res_today.status_code, 200)
        data_today = res_today.get_json()
        self.assertTrue(data_today['success'])

        res_tomorrow = self.app.get(f'/api/showtimes?city=Kochi&date={tomorrow_str}')
        self.assertEqual(res_tomorrow.status_code, 200)
        data_tomorrow = res_tomorrow.get_json()
        self.assertTrue(data_tomorrow['success'])

        print(f"✅ Test 02 Passed: Successfully queried showtimes for {today_str} and {tomorrow_str}.")

    def test_03_seat_availability_flags(self):
        db = get_db()
        movie = db.movies.find_one({"title": "KALKI 2898 - AD"})
        self.assertIsNotNone(movie)

        today_str = datetime.now().strftime("%Y-%m-%d")
        shows = show_service.get_shows(movie_id=str(movie['_id']), date_str=today_str, city="Kochi")
        self.assertGreater(len(shows), 0)

        for s in shows:
            self.assertIn('available_seats', s)
            self.assertIn('status', s)
            self.assertIn(s['status'], ['available', 'filling_fast', 'sold_out'])

        print(f"✅ Test 03 Passed: Verified availability badges for {len(shows)} shows on {today_str}.")

    def test_04_date_propagation_in_ticket(self):
        db = get_db()
        movie = db.movies.find_one({"title": "KALKI 2898 - AD"})
        theatre = db.theatres.find_one({"city": "Kochi"})
        
        target_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        show = show_service.find_or_create_show(
            movie_id=str(movie['_id']),
            theatre_id=str(theatre['_id']),
            time_str="08:30 PM",
            date_str=target_date,
            screen="Screen 1",
            price=250
        )
        self.assertEqual(show['date'], target_date)
        print(f"✅ Test 04 Passed: Verified exact showtime date propagation for {target_date}.")

if __name__ == '__main__':
    unittest.main()
