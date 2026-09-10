import os
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from services.mongodb_service import get_db, create_indexes

def seed_database():
    print("🌱 Starting CineTickets MongoDB Atlas Seeding...")
    db = get_db()
    if db is None:
        print("❌ Cannot connect to MongoDB Atlas. Aborting seeding.")
        return

    create_indexes(db)

    # 1. Seed Movies with rich details, cast & backdrop URLs
    movies_data = [
        {
            "title": "KALKI 2898 - AD",
            "short_description": "A modern avatar of Vishnu descends to Earth to protect human life from demonic forces in a dystopian futuristic city of Kasi.",
            "full_description": "Kalki 2898 AD is a landmark Indian sci-fi epic set in the year 2898 AD in Kasi, the world's last surviving city ruled by the authoritarian Supreme Yaskin. As prophesied, a supreme mother named Sumathi carries the unborn 10th avatar of Lord Vishnu. The immortal warrior Ashwatthama emerges from centuries of meditation to guard her, while Bhairava, a shrewd bounty hunter, embarks on a mission to capture her for a ticket to the opulent Complex.",
            "poster_url": "/static/images/movies/kalki-2898-ad.jpg",
            "banner_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1600&auto=format&fit=crop",
            "trailer_url": "https://www.youtube.com/embed/k95k4H6kY3E",
            "genre": ["Action", "Drama", "Sci-Fi"],
            "language": "Telugu",
            "duration": "2h 56m",
            "certificate": "UA",
            "rating": 4.8,
            "status": "now_showing",
            "release_date": "27 June 2024",
            "director": "Nag Ashwin",
            "producer": "C. Aswani Dutt",
            "production_company": "Vyjayanthi Movies",
            "cast": [
                {"name": "Prabhas", "character": "Bhairava / Karna", "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=300&auto=format&fit=crop"},
                {"name": "Amitabh Bachchan", "character": "Ashwatthama", "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=300&auto=format&fit=crop"},
                {"name": "Deepika Padukone", "character": "Sumathi", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=300&auto=format&fit=crop"},
                {"name": "Kamal Haasan", "character": "Supreme Yaskin", "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=300&auto=format&fit=crop"}
            ],
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "FURIOSA: A MAD MAX SAGA",
            "short_description": "The origin story of renegade warrior Furiosa before her team-up with Mad Max in the wasteland.",
            "full_description": "As the world fell, young Furiosa is snatched from the Green Place of Many Mothers and falls into the hands of a great Biker Horde led by the Warlord Dementus. Sweeping through the Wasteland, they come across the Citadel presided over by The Immortan Joe. As the two Tyrants war for dominance, Furiosa must survive many trials as she puts together the means to find her way home.",
            "poster_url": "/static/images/movies/furiosa.jpg",
            "banner_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1600&auto=format&fit=crop",
            "trailer_url": "https://www.youtube.com/embed/XJMuhwVlca4",
            "genre": ["Action", "Adventure", "Sci-Fi"],
            "language": "English",
            "duration": "2h 28m",
            "certificate": "A",
            "rating": 4.6,
            "status": "now_showing",
            "release_date": "24 May 2024",
            "director": "George Miller",
            "producer": "Doug Mitchell, George Miller",
            "production_company": "Warner Bros. Pictures",
            "cast": [
                {"name": "Anya Taylor-Joy", "character": "Imperator Furiosa", "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=300&auto=format&fit=crop"},
                {"name": "Chris Hemsworth", "character": "Warlord Dementus", "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=300&auto=format&fit=crop"},
                {"name": "Tom Burke", "character": "Praetorian Jack", "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?q=80&w=300&auto=format&fit=crop"}
            ],
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "DEADPOOL & WOLVERINE",
            "short_description": "Wolverine is recovering from his injuries when he crosses paths with the loudmouth Deadpool.",
            "full_description": "Six years after the events of Deadpool 2, Wade Wilson is living a quiet life, having left his time as the mercenary Deadpool behind him, until the Time Variance Authority (TVA) pulls him into a new mission. With his home universe facing an existential threat, Wilson reluctantly joins forces with an even more reluctant Wolverine on a mission that will change the history of the Marvel Cinematic Universe.",
            "poster_url": "/static/images/movies/deadpool-wolverine.jpg",
            "banner_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?q=80&w=1600&auto=format&fit=crop",
            "trailer_url": "https://www.youtube.com/embed/73_1biulk6s",
            "genre": ["Action", "Comedy", "Sci-Fi"],
            "language": "English",
            "duration": "2h 07m",
            "certificate": "A",
            "rating": 4.9,
            "status": "now_showing",
            "release_date": "26 July 2024",
            "director": "Shawn Levy",
            "producer": "Kevin Feige, Ryan Reynolds, Shawn Levy",
            "production_company": "Marvel Studios",
            "cast": [
                {"name": "Ryan Reynolds", "character": "Wade Wilson / Deadpool", "image_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=300&auto=format&fit=crop"},
                {"name": "Hugh Jackman", "character": "Logan / Wolverine", "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=300&auto=format&fit=crop"},
                {"name": "Emma Corrin", "character": "Cassandra Nova", "image_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=300&auto=format&fit=crop"}
            ],
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "INSIDE OUT 2",
            "short_description": "Follow Riley, in her teenage years, encountering new emotions like Anxiety, Envy, and Embarrassment.",
            "full_description": "Disney and Pixar's Inside Out 2 returns to the mind of newly minted teenager Riley just as headquarters is undergoing a sudden demolition to make room for something entirely unexpected: new Emotions! Joy, Sadness, Anger, Fear and Disgust aren't sure how to feel when Anxiety shows up.",
            "poster_url": "/static/images/movies/inside-out-2.jpg",
            "banner_url": "https://images.unsplash.com/photo-1513151233558-d860c5398176?q=80&w=1600&auto=format&fit=crop",
            "trailer_url": "https://www.youtube.com/embed/LEjhY15eCx0",
            "genre": ["Animation", "Comedy", "Family"],
            "language": "English",
            "duration": "1h 36m",
            "certificate": "U",
            "rating": 4.7,
            "status": "now_showing",
            "release_date": "14 June 2024",
            "director": "Kelsey Mann",
            "producer": "Mark Nielsen",
            "production_company": "Disney / Pixar Animation Studios",
            "cast": [
                {"name": "Amy Poehler", "character": "Joy", "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=300&auto=format&fit=crop"},
                {"name": "Maya Hawke", "character": "Anxiety", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=300&auto=format&fit=crop"},
                {"name": "Kensington Tallman", "character": "Riley Andersen", "image_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=300&auto=format&fit=crop"}
            ],
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "MAHARAJA",
            "short_description": "A barber seeks vengeance after his beloved dustbin, Lakshmi, is stolen during a burglary.",
            "full_description": "A quiet barber in Chennai named Maharaja files a police complaint claiming that his beloved dustbin, named Lakshmi, has been stolen after a home break-in. When the police scoff at his strange request, Maharaja refuses to leave until justice is served, uncovering a chilling web of secrets and vengeance.",
            "poster_url": "/static/images/movies/maharaja.jpg",
            "banner_url": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=1600&auto=format&fit=crop",
            "trailer_url": "https://www.youtube.com/embed/1_0X0uT2b7A",
            "genre": ["Action", "Drama", "Thriller"],
            "language": "Tamil",
            "duration": "2h 21m",
            "certificate": "UA",
            "rating": 4.9,
            "status": "now_showing",
            "release_date": "14 June 2024",
            "director": "Nithilan Swaminathan",
            "producer": "Sudhan Sundaram, Jagadish Palanisamy",
            "production_company": "Passion Studios",
            "cast": [
                {"name": "Vijay Sethupathi", "character": "Maharaja", "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=300&auto=format&fit=crop"},
                {"name": "Anurag Kashyap", "character": "Selvam", "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=300&auto=format&fit=crop"},
                {"name": "Mamta Mohandas", "character": "Asifa", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=300&auto=format&fit=crop"}
            ],
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "STREE 2",
            "short_description": "The town of Chanderi is haunted once again by a terrifying headless entity named Sarkata.",
            "full_description": "The town of Chanderi is plagued by a new menace: a headless creature known as Sarkata that abducts progressive women. Vicky and his loyal friends must team up with the mysterious woman once again to save their town from complete annihilation.",
            "poster_url": "/static/images/movies/stree-2.jpg",
            "banner_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1600&auto=format&fit=crop",
            "trailer_url": "https://www.youtube.com/embed/kv1BT6aVaHk",
            "genre": ["Comedy", "Horror"],
            "language": "Hindi",
            "duration": "2h 27m",
            "certificate": "UA",
            "rating": 4.7,
            "status": "coming_soon",
            "release_date": "15 August 2024",
            "director": "Amar Kaushik",
            "producer": "Dinesh Vijan, Jyoti Deshpande",
            "production_company": "Maddock Films",
            "cast": [
                {"name": "Rajkummar Rao", "character": "Vicky", "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=300&auto=format&fit=crop"},
                {"name": "Shraddha Kapoor", "character": "Unknown Woman", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=300&auto=format&fit=crop"},
                {"name": "Pankaj Tripathi", "character": "Rudra", "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=300&auto=format&fit=crop"}
            ],
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "PUSHPA 2: THE RULE",
            "short_description": "The clash continues between Pushpa Raj and SP Bhanwar Singh Shekhawat in red sandalwood smuggling.",
            "full_description": "Pushpa Raj rules the red sandalwood smuggling empire with an iron fist, asserting dominance over rivals and police alike. However, SP Bhanwar Singh Shekhawat vows revenge, leading to an explosive war of egos, power, and survival.",
            "poster_url": "/static/images/movies/pushpa-2.jpg",
            "banner_url": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=1600&auto=format&fit=crop",
            "trailer_url": "https://www.youtube.com/embed/1kmkA18H8YY",
            "genre": ["Action", "Drama", "Crime"],
            "language": "Telugu",
            "duration": "3h 05m",
            "certificate": "UA",
            "rating": 4.9,
            "status": "coming_soon",
            "release_date": "05 December 2024",
            "director": "Sukumar",
            "producer": "Naveen Yerneni, Y. Ravi Shankar",
            "production_company": "Mythri Movie Makers",
            "cast": [
                {"name": "Allu Arjun", "character": "Pushpa Raj", "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=300&auto=format&fit=crop"},
                {"name": "Fahadh Faasil", "character": "SP Bhanwar Singh Shekhawat", "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=300&auto=format&fit=crop"},
                {"name": "Rashmika Mandanna", "character": "Srivalli", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=300&auto=format&fit=crop"}
            ],
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "THE GREATEST OF ALL TIME (GOAT)",
            "short_description": "A field agent for the Special Anti-Terrorist Squad embarks on a high stakes mission that resurfaces ghost pasts.",
            "full_description": "Gandhi is a former hostage negotiator and field agent for the Special Anti-Terrorist Squad (SATS). After years of quiet retirement, past unresolved missions resurface, forcing him into a globe-trotting battle against a shadow enemy with deep personal ties.",
            "poster_url": "/static/images/movies/goat.jpg",
            "banner_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1600&auto=format&fit=crop",
            "trailer_url": "https://www.youtube.com/embed/jxCRlebieWc",
            "genre": ["Action", "Sci-Fi", "Thriller"],
            "language": "Tamil",
            "duration": "2h 59m",
            "certificate": "UA",
            "rating": 4.5,
            "status": "coming_soon",
            "release_date": "05 September 2024",
            "director": "Venkat Prabhu",
            "producer": "Kalpathi S. Aghoram",
            "production_company": "AGS Entertainment",
            "cast": [
                {"name": "Vijay", "character": "Gandhi / Jeevan", "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=300&auto=format&fit=crop"},
                {"name": "Prashanth", "character": "Sunil Thiagarajan", "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=300&auto=format&fit=crop"},
                {"name": "Prabhu Deva", "character": "Kalyan Sundaram", "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=300&auto=format&fit=crop"}
            ],
            "created_at": datetime.now(timezone.utc)
        }
    ]

    inserted_movies = []
    for m in movies_data:
        existing = db.movies.find_one({"title": m["title"]})
        if not existing:
            res = db.movies.insert_one(m)
            m["_id"] = res.inserted_id
            inserted_movies.append(m)
        else:
            db.movies.update_one({"_id": existing["_id"]}, {"$set": {
                "poster_url": m["poster_url"],
                "banner_url": m["banner_url"],
                "poster": m["poster_url"],
                "backdrop": m["banner_url"],
                "short_description": m["short_description"],
                "full_description": m["full_description"],
                "description": m["full_description"],
                "director": m["director"],
                "producer": m["producer"],
                "production_company": m["production_company"],
                "cast": m["cast"],
                "release_date": m["release_date"],
                "certificate": m["certificate"],
                "language": m["language"],
                "duration": m["duration"],
                "rating": m["rating"]
            }})
            m["_id"] = existing["_id"]
            inserted_movies.append(m)

    print(f"✅ Seeded/Updated {len(inserted_movies)} movies with rich details and cast.")

    # Seed Sample Reviews for movies
    if db.reviews.count_documents({}) == 0:
        sample_reviews = [
            {
                "user_name": "Rahul Verma",
                "rating": 5,
                "comment": "Mind-blowing visual spectacle! The world-building and Mahabharata climax scenes were breathtaking.",
                "verified_booking": True,
                "created_at": datetime.now(timezone.utc) - timedelta(days=2)
            },
            {
                "user_name": "Ananya Sharma",
                "rating": 5,
                "comment": "Absolue masterpiece of Indian Cinema! Amitabh Bachchan as Ashwatthama stole every single scene.",
                "verified_booking": True,
                "created_at": datetime.now(timezone.utc) - timedelta(days=4)
            },
            {
                "user_name": "Vikram Nair",
                "rating": 4,
                "comment": "Great background score and cinematography. Loved Prabhas's entrance and the action choreography.",
                "verified_booking": False,
                "created_at": datetime.now(timezone.utc) - timedelta(days=7)
            }
        ]
        for m in inserted_movies:
            for rev in sample_reviews:
                r_doc = dict(rev)
                r_doc["movie_id"] = m["_id"]
                db.reviews.insert_one(r_doc)
        print("✅ Preloaded sample user reviews for movies.")

    # 2. Seed Theatres
    theatres_data = [
        {
            "name": "PVR Cinemas, Lulu Mall",
            "location": "Edappally, Lulu Mall",
            "city": "Kochi",
            "address": "Lulu International Shopping Mall, NH 47, Edappally, Kochi, Kerala 682024",
            "distance": "4.6 km",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "name": "Cinepolis, Centre Square Mall",
            "location": "MG Road",
            "city": "Kochi",
            "address": "Centre Square Mall, MG Road, Shenoys, Kochi, Kerala 682035",
            "distance": "6.2 km",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "name": "INOX, Oberon Mall",
            "location": "Bypass Edappally",
            "city": "Kochi",
            "address": "Oberon Mall, NH Bypass, Edappally, Kochi, Kerala 682024",
            "distance": "8.1 km",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "name": "Vanitha Cineplex 4K Dolby Atmos",
            "location": "Edappally Toll",
            "city": "Kochi",
            "address": "Toll Junction, Edappally, Kochi, Kerala 682024",
            "distance": "3.5 km",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "name": "Shenoys Cineplex 4K",
            "location": "MG Road",
            "city": "Kochi",
            "address": "MG Road, Shenoys, Kochi, Kerala 682035",
            "distance": "5.8 km",
            "created_at": datetime.now(timezone.utc)
        }
    ]

    inserted_theatres = []
    for t in theatres_data:
        existing = db.theatres.find_one({"name": t["name"]})
        if not existing:
            res = db.theatres.insert_one(t)
            t["_id"] = res.inserted_id
            inserted_theatres.append(t)
        else:
            t["_id"] = existing["_id"]
            inserted_theatres.append(existing)

    print(f"✅ Preloaded {len(inserted_theatres)} theatres.")

    # 3. Seed Users
    admin_email = "admin@cinetickets.com"
    user_email = "user@cinetickets.com"

    if not db.users.find_one({"email": admin_email}):
        db.users.insert_one({
            "name": "Administrator",
            "email": admin_email,
            "phone": "+919876543210",
            "password_hash": generate_password_hash("Admin@123"),
            "role": "admin",
            "created_at": datetime.now(timezone.utc)
        })

    if not db.users.find_one({"email": user_email}):
        db.users.insert_one({
            "name": "John Doe",
            "email": user_email,
            "phone": "+919123456789",
            "password_hash": generate_password_hash("user123"),
            "role": "user",
            "created_at": datetime.now(timezone.utc)
        })

    print("🚀 CineTickets MongoDB Atlas Seeding Completed Successfully!")

if __name__ == '__main__':
    seed_database()
