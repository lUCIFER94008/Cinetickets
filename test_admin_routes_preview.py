import unittest
from app import app
from services.mongodb_service import get_db

class TestAdminShowtimesSeats(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = get_db()
        admin = db.users.find_one({'role': 'admin'})
        self.admin_user_id = str(admin['_id']) if admin else None

    def test_01_admin_showtimes_page(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.admin_user_id
            
            res = client.get('/admin/showtimes')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('SHOWTIME MANAGEMENT', html)
            print("✅ Test 01 Passed: GET /admin/showtimes rendered successfully.")

    def test_02_admin_seats_page(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.admin_user_id
            
            res = client.get('/admin/seats')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('SEAT MANAGEMENT', html)
            print("✅ Test 02 Passed: GET /admin/seats rendered successfully.")

if __name__ == '__main__':
    unittest.main()
