from services.mongodb_service import get_db
from utils.youtube_helpers import get_youtube_embed_url, extract_youtube_id

TRAILER_MAPPINGS = {
    "KALKI 2898 - AD": "https://www.youtube.com/watch?v=kQDd1AhGIHk",
    "FURIOSA: A MAD MAX SAGA": "https://www.youtube.com/watch?v=XJMuhwVwcaU",
    "DEADPOOL & WOLVERINE": "https://www.youtube.com/watch?v=73_1biulkYk",
    "INSIDE OUT 2": "https://www.youtube.com/watch?v=LEjhY15eCx0",
    "MAHARAJA": "https://www.youtube.com/watch?v=48nFk_v_OaI",
    "STREE 2": "https://www.youtube.com/watch?v=KVnheXwqF08",
    "PUSHPA 2: THE RULE": "https://www.youtube.com/watch?v=1kvkL2rV35k",
    "THE GREATEST OF ALL TIME": "https://www.youtube.com/watch?v=jxCRle3j_vk",
    "ARM": "https://www.youtube.com/watch?v=5rT88f2qG18",
    "DEVARA": "https://www.youtube.com/watch?v=2Tz8i8WbCFA",
}

def seed_trailers():
    db = get_db()
    movies = list(db.movies.find())
    updated_count = 0
    for movie in movies:
        title = movie.get('title', '').strip()
        matched_url = None
        for key, url in TRAILER_MAPPINGS.items():
            if key.lower() in title.lower() or title.lower() in key.lower():
                matched_url = url
                break
        
        if matched_url:
            embed_url = get_youtube_embed_url(matched_url)
            video_id = extract_youtube_id(matched_url)
            db.movies.update_one(
                {'_id': movie['_id']},
                {'$set': {
                    'trailer_url': matched_url,
                    'youtube_embed_url': embed_url,
                    'youtube_id': video_id
                }}
            )
            print(f"✅ Updated trailer for '{title}': {matched_url}")
            updated_count += 1
        else:
            print(f"ℹ️ No trailer mapping for '{title}', keeping existing/empty.")

    print(f"\nCompleted seeding trailers! Total movies updated: {updated_count}")

if __name__ == '__main__':
    seed_trailers()
