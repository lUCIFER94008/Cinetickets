import unittest
from app import app
from services.admin_service import admin_service
from services.mongodb_service import get_db

class TestAdminBookings(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = get_db()
        admin = db.users.find_one({'role': 'admin'})
        self.admin_user_id = str(admin['_id']) if admin else None

    def test_01_admin_bookings_filtered_service(self):
        """Test admin_service.get_admin_bookings_filtered method"""
        data = admin_service.get_admin_bookings_filtered(date_str='2026-09-11')
        self.assertIsNotNone(data)
        self.assertEqual(data['selected_date'], '2026-09-11')
        self.assertEqual(len(data['week_days']), 7)
        self.assertEqual(data['summary']['total_bookings'], 13)
        self.assertIn('₹', data['summary']['total_revenue_formatted'])
        print("✅ Test 01 Passed: Filtered 13 bookings for 2026-09-11 from MongoDB.")

    def test_02_weekly_overview_counts(self):
        """Test weekly counts calculation in week_days"""
        data = admin_service.get_admin_bookings_filtered(date_str='2026-09-11')
        day_counts = {d['date_str']: d['count'] for d in data['week_days']}
        self.assertEqual(day_counts['2026-09-11'], 13)
        self.assertEqual(day_counts['2026-09-08'], 2)
        self.assertEqual(day_counts['2026-09-09'], 7)
        self.assertEqual(day_counts['2026-09-10'], 5)
        print("✅ Test 02 Passed: Weekly overview count breakdown verified (8th: 2, 9th: 7, 10th: 5, 11th: 13).")

    def test_03_week_navigation_math(self):
        """Test previous and next week navigation calculation"""
        data = admin_service.get_admin_bookings_filtered(date_str='2026-09-11', start_date_str='2026-09-07')
        self.assertEqual(data['start_date'], '2026-09-07')
        self.assertEqual(data['end_date'], '2026-09-13')
        self.assertEqual(data['prev_week_start'], '2026-08-31')
        self.assertEqual(data['next_week_start'], '2026-09-14')
        print("✅ Test 03 Passed: Week navigation start/end dates verified.")

    def test_04_search_and_status_filters(self):
        """Test search and status filtering logic"""
        data = admin_service.get_admin_bookings_filtered(date_str='2026-09-11', search='MAHARAJA')
        self.assertEqual(len(data['bookings']), 4)
        
        data_all = admin_service.get_admin_bookings_filtered(date_str='2026-09-11', search='Movie Ticket')
        self.assertEqual(len(data_all['bookings']), 9)

        data_empty_search = admin_service.get_admin_bookings_filtered(date_str='2026-09-11', search='NONEXISTENTMOVIE')
        self.assertEqual(len(data_empty_search['bookings']), 0)
        self.assertEqual(data_empty_search['summary']['total_bookings'], 0)
        print("✅ Test 04 Passed: Search filter correctly restricts results.")

    def test_05_admin_bookings_api_endpoint(self):
        """Test /api/admin/bookings HTTP API endpoint with admin session"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.admin_user_id
            
            res = client.get('/api/admin/bookings?date=2026-09-11')
            self.assertEqual(res.status_code, 200)
            json_data = res.get_json()
            self.assertTrue(json_data['success'])
            self.assertEqual(json_data['data']['summary']['total_bookings'], 13)
            print("✅ Test 05 Passed: API /api/admin/bookings returned HTTP 200 with JSON payload.")

if __name__ == '__main__':
    unittest.main()
