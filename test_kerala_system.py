import unittest
from app import app
from services.mongodb_service import get_db

class TestKeralaLocationSystem(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_api_cities(self):
        res = self.app.get('/api/cities')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 20)
        city_names = [c['name'] for c in data['cities']]
        self.assertIn('Kochi', city_names)
        self.assertIn('Thiruvananthapuram', city_names)
        self.assertIn('Thrissur', city_names)
        self.assertIn('Kozhikode', city_names)
        self.assertIn('Aluva', city_names)
        print(f"✅ Test 01 Passed: Found {data['count']} Kerala cities/towns in API.")

    def test_02_kochi_theatres(self):
        res = self.app.get('/api/theatres?city=Kochi')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        t_names = [t['name'] for t in data['theatres']]
        self.assertTrue(any('PVR' in name for name in t_names))
        print(f"✅ Test 02 Passed: Found {data['count']} theatres in Kochi.")

    def test_03_thrissur_theatres(self):
        res = self.app.get('/api/theatres?city=Thrissur')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        t_names = [t['name'] for t in data['theatres']]
        self.assertTrue(any('Ragam' in name or 'INOX' in name for name in t_names))
        print(f"✅ Test 03 Passed: Found {data['count']} theatres in Thrissur.")

    def test_04_kozhikode_theatres(self):
        res = self.app.get('/api/theatres?city=Kozhikode')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        t_names = [t['name'] for t in data['theatres']]
        self.assertTrue(any('Filmcity' in name or 'Coronation' in name for name in t_names))
        print(f"✅ Test 04 Passed: Found {data['count']} theatres in Kozhikode.")

    def test_05_tvm_theatres(self):
        res = self.app.get('/api/theatres?city=Thiruvananthapuram')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        t_names = [t['name'] for t in data['theatres']]
        self.assertTrue(any('Ariesplex' in name or 'Kairali' in name for name in t_names))
        print(f"✅ Test 05 Passed: Found {data['count']} theatres in Thiruvananthapuram.")

    def test_06_city_filtered_shows(self):
        res_kochi = self.app.get('/api/shows?city=Kochi')
        self.assertEqual(res_kochi.status_code, 200)
        shows_kochi = res_kochi.get_json()['shows']
        self.assertGreater(len(shows_kochi), 0)

        res_thrissur = self.app.get('/api/shows?city=Thrissur')
        self.assertEqual(res_thrissur.status_code, 200)
        shows_thrissur = res_thrissur.get_json()['shows']
        self.assertGreater(len(shows_thrissur), 0)

        # Verify no Thrissur show appears in Kochi filter
        kochi_theatre_cities = {s['theatre']['city'] for s in shows_kochi if s.get('theatre')}
        self.assertTrue(all(c.lower() == 'kochi' for c in kochi_theatre_cities))
        print("✅ Test 06 Passed: Shows strictly filtered by city without cross-city leaks.")

    def test_07_home_and_movie_routes(self):
        res_home = self.app.get('/?city=Thrissur')
        self.assertEqual(res_home.status_code, 200)
        self.assertIn(b'Thrissur', res_home.data)

        db = get_db()
        movie = db.movies.find_one({"title": "KALKI 2898 - AD"})
        if movie:
            res_movie = self.app.get(f"/movie/{movie['_id']}?city=Kozhikode")
            self.assertEqual(res_movie.status_code, 200)
            self.assertIn(b'Kozhikode', res_movie.data)
        print("✅ Test 07 Passed: Home and Movie pages render correctly with dynamic city parameter.")

if __name__ == '__main__':
    unittest.main()
