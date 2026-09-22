import unittest
from app import app
from utils.youtube_helpers import extract_youtube_id, get_youtube_embed_url
from services.movie_service import movie_service
from services.mongodb_service import get_db

class TestMovieTrailers(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_youtube_helpers_extraction(self):
        """Test YouTube ID extraction for all URL formats"""
        urls = [
            ("https://www.youtube.com/watch?v=kQDd1AhGIHk", "kQDd1AhGIHk"),
            ("https://youtu.be/XJMuhwVwcaU", "XJMuhwVwcaU"),
            ("https://www.youtube.com/embed/73_1biulkYk", "73_1biulkYk"),
            ("https://www.youtube.com/watch?v=LEjhY15eCx0&feature=shared", "LEjhY15eCx0"),
            ("48nFk_v_OaI", "48nFk_v_OaI")
        ]
        for url, expected_id in urls:
            extracted = extract_youtube_id(url)
            self.assertEqual(extracted, expected_id)
            embed_url = get_youtube_embed_url(url)
            self.assertEqual(embed_url, f"https://www.youtube.com/embed/{expected_id}")
        
        # Invalid URL fallback test
        self.assertIsNone(extract_youtube_id("invalid-not-youtube-url"))
        self.assertIsNone(get_youtube_embed_url("invalid-not-youtube-url"))
        print("✅ Test 01 Passed: YouTube URL parser and embed generator verified.")

    def test_02_movies_enrichment(self):
        """Test that movies loaded from MongoDB have trailer_url and youtube_embed_url"""
        movies = movie_service.get_movies()
        self.assertGreater(len(movies), 0)
        
        # Check Kalki or Furiosa
        furiosa = next((m for m in movies if "FURIOSA" in m.get('title', '').upper()), None)
        self.assertIsNotNone(furiosa)
        self.assertEqual(furiosa.get('trailer_url'), "https://www.youtube.com/watch?v=XJMuhwVwcaU")
        self.assertEqual(furiosa.get('youtube_embed_url'), "https://www.youtube.com/embed/XJMuhwVwcaU")
        print("✅ Test 02 Passed: Furiosa movie doc enriched with embed URL.")

    def test_03_missing_trailer_fallback(self):
        """Test that movies without trailer URL return None embed URL without breaking"""
        test_movie = next((m for m in movie_service.get_movies() if m.get('title') == "TEST AUTOMATED MOVIE"), None)
        if test_movie:
            self.assertIsNone(test_movie.get('youtube_embed_url'))
        print("✅ Test 03 Passed: Safe fallback for movies without trailer URLs verified.")

    def test_04_movie_details_route(self):
        """Test movie details page HTTP response and trailer section rendering"""
        movies = movie_service.get_movies()
        furiosa = next((m for m in movies if "FURIOSA" in m.get('title', '').upper()), movies[0])
        movie_id = str(furiosa['_id'])

        res = self.app.get(f'/movie/{movie_id}')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('OFFICIAL TRAILER', html)
        self.assertIn('https://www.youtube.com/embed/XJMuhwVwcaU', html)
        print("✅ Test 04 Passed: Movie details page renders OFFICIAL TRAILER iframe.")

if __name__ == '__main__':
    unittest.main()
