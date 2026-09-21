import os
from datetime import datetime, timedelta, timezone
from services.mongodb_service import get_db, create_indexes

def seed_kerala_data():
    print("🌱 Starting Kerala Cities, Theatres & Showtimes Seeding...")
    db = get_db()
    if db is None:
        print("❌ Cannot connect to MongoDB Atlas.")
        return

    create_indexes(db)

    # 1. Kerala Cities & Major Towns
    cities_data = [
        # Major Districts / Metros
        {"name": "Kochi", "state": "Kerala", "district": "Ernakulam", "is_district": True, "active": True},
        {"name": "Thiruvananthapuram", "state": "Kerala", "district": "Thiruvananthapuram", "is_district": True, "active": True},
        {"name": "Kozhikode", "state": "Kerala", "district": "Kozhikode", "is_district": True, "active": True},
        {"name": "Thrissur", "state": "Kerala", "district": "Thrissur", "is_district": True, "active": True},
        {"name": "Kollam", "state": "Kerala", "district": "Kollam", "is_district": True, "active": True},
        {"name": "Kannur", "state": "Kerala", "district": "Kannur", "is_district": True, "active": True},
        {"name": "Kottayam", "state": "Kerala", "district": "Kottayam", "is_district": True, "active": True},
        {"name": "Alappuzha", "state": "Kerala", "district": "Alappuzha", "is_district": True, "active": True},
        {"name": "Palakkad", "state": "Kerala", "district": "Palakkad", "is_district": True, "active": True},
        {"name": "Malappuram", "state": "Kerala", "district": "Malappuram", "is_district": True, "active": True},
        {"name": "Kasaragod", "state": "Kerala", "district": "Kasaragod", "is_district": True, "active": True},
        {"name": "Pathanamthitta", "state": "Kerala", "district": "Pathanamthitta", "is_district": True, "active": True},
        {"name": "Idukki", "state": "Kerala", "district": "Idukki", "is_district": True, "active": True},
        {"name": "Wayanad", "state": "Kerala", "district": "Wayanad", "is_district": True, "active": True},

        # Major Cinema Towns
        {"name": "Aluva", "state": "Kerala", "district": "Ernakulam", "is_district": False, "active": True},
        {"name": "Angamaly", "state": "Kerala", "district": "Ernakulam", "is_district": False, "active": True},
        {"name": "Perumbavur", "state": "Kerala", "district": "Ernakulam", "is_district": False, "active": True},
        {"name": "Muvattupuzha", "state": "Kerala", "district": "Ernakulam", "is_district": False, "active": True},
        {"name": "North Paravur", "state": "Kerala", "district": "Ernakulam", "is_district": False, "active": True},
        {"name": "Changanassery", "state": "Kerala", "district": "Kottayam", "is_district": False, "active": True},
        {"name": "Pala", "state": "Kerala", "district": "Kottayam", "is_district": False, "active": True},
        {"name": "Thodupuzha", "state": "Kerala", "district": "Idukki", "is_district": False, "active": True},
        {"name": "Guruvayur", "state": "Kerala", "district": "Thrissur", "is_district": False, "active": True},
        {"name": "Kunnamkulam", "state": "Kerala", "district": "Thrissur", "is_district": False, "active": True},
        {"name": "Chalakudy", "state": "Kerala", "district": "Thrissur", "is_district": False, "active": True},
        {"name": "Irinjalakuda", "state": "Kerala", "district": "Thrissur", "is_district": False, "active": True},
        {"name": "Kodungallur", "state": "Kerala", "district": "Thrissur", "is_district": False, "active": True},
        {"name": "Manjeri", "state": "Kerala", "district": "Malappuram", "is_district": False, "active": True},
        {"name": "Perinthalmanna", "state": "Kerala", "district": "Malappuram", "is_district": False, "active": True},
        {"name": "Tirur", "state": "Kerala", "district": "Malappuram", "is_district": False, "active": True},
        {"name": "Ponnani", "state": "Kerala", "district": "Malappuram", "is_district": False, "active": True},
        {"name": "Vadakara", "state": "Kerala", "district": "Kozhikode", "is_district": False, "active": True},
        {"name": "Thalassery", "state": "Kerala", "district": "Kannur", "is_district": False, "active": True},
        {"name": "Payyanur", "state": "Kerala", "district": "Kannur", "is_district": False, "active": True},
        {"name": "Kanhangad", "state": "Kerala", "district": "Kasaragod", "is_district": False, "active": True}
    ]

    city_id_map = {}
    for c in cities_data:
        existing = db.cities.find_one({"name": c["name"]})
        if not existing:
            res = db.cities.insert_one(c)
            city_id_map[c["name"]] = res.inserted_id
        else:
            db.cities.update_one({"_id": existing["_id"]}, {"$set": c})
            city_id_map[c["name"]] = existing["_id"]

    print(f"✅ Seeded/Updated {len(cities_data)} Kerala cities & towns in database.")

    # 2. Kerala Realistic Theatres Setup
    theatres_seed = [
        # KOCHI
        {
            "name": "PVR Cinemas, Lulu Mall",
            "city": "Kochi",
            "district": "Ernakulam",
            "address": "Lulu International Shopping Mall, Edappally, Kochi, Kerala 682024",
            "screens": 9,
            "formats": ["2D", "3D", "IMAX", "Dolby Atmos", "4DX"],
            "distance": "3.5 km",
            "active": True
        },
        {
            "name": "Cinepolis, Centre Square Mall",
            "city": "Kochi",
            "district": "Ernakulam",
            "address": "Centre Square Mall, MG Road, Shenoys, Kochi, Kerala 682035",
            "screens": 11,
            "formats": ["2D", "3D", "Dolby Atmos", "4DX"],
            "distance": "5.2 km",
            "active": True
        },
        {
            "name": "INOX, Oberon Mall",
            "city": "Kochi",
            "district": "Ernakulam",
            "address": "Oberon Mall, NH Bypass, Edappally, Kochi, Kerala 682024",
            "screens": 4,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "4.1 km",
            "active": True
        },
        {
            "name": "Vanitha Vineetha Cineplex",
            "city": "Kochi",
            "district": "Ernakulam",
            "address": "Toll Junction, Edappally, Kochi, Kerala 682024",
            "screens": 2,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "2.8 km",
            "active": True
        },
        {
            "name": "Shenoys Cineplex 4K",
            "city": "Kochi",
            "district": "Ernakulam",
            "address": "MG Road, Shenoys, Kochi, Kerala 682035",
            "screens": 5,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "5.5 km",
            "active": True
        },

        # THIRUVANANTHAPURAM
        {
            "name": "Ariesplex SL Media Plex",
            "city": "Thiruvananthapuram",
            "district": "Thiruvananthapuram",
            "address": "Overbridge, Thampanoor, Thiruvananthapuram, Kerala 695001",
            "screens": 6,
            "formats": ["2D", "3D", "4K Dolby Atmos"],
            "distance": "1.2 km",
            "active": True
        },
        {
            "name": "Kairali Theatre",
            "city": "Thiruvananthapuram",
            "district": "Thiruvananthapuram",
            "address": "KSFDC Complex, KSRTC Bus Stand Rd, Thampanoor, Thiruvananthapuram, Kerala 695001",
            "screens": 1,
            "formats": ["2D", "Dolby Atmos"],
            "distance": "1.5 km",
            "active": True
        },
        {
            "name": "Sree Theatre",
            "city": "Thiruvananthapuram",
            "district": "Thiruvananthapuram",
            "address": "KSFDC Complex, Thampanoor, Thiruvananthapuram, Kerala 695001",
            "screens": 1,
            "formats": ["2D", "3D"],
            "distance": "1.5 km",
            "active": True
        },
        {
            "name": "Nila Theatre",
            "city": "Thiruvananthapuram",
            "district": "Thiruvananthapuram",
            "address": "KSFDC Complex, Thampanoor, Thiruvananthapuram, Kerala 695001",
            "screens": 1,
            "formats": ["2D"],
            "distance": "1.5 km",
            "active": True
        },
        {
            "name": "Lenin Cinemas",
            "city": "Thiruvananthapuram",
            "district": "Thiruvananthapuram",
            "address": "Vanchiyoor, Thiruvananthapuram, Kerala 695035",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "2.8 km",
            "active": True
        },
        {
            "name": "Kalabhavan Theatre",
            "city": "Thiruvananthapuram",
            "district": "Thiruvananthapuram",
            "address": "Vazhuthacaud, Thiruvananthapuram, Kerala 695014",
            "screens": 1,
            "formats": ["2D", "4K"],
            "distance": "3.1 km",
            "active": True
        },
        {
            "name": "Kripa Cinemas",
            "city": "Thiruvananthapuram",
            "district": "Thiruvananthapuram",
            "address": "MG Road, Overbridge, Thampanoor, Thiruvananthapuram, Kerala 695001",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "1.0 km",
            "active": True
        },

        # THRISSUR
        {
            "name": "INOX, Sobha City Mall",
            "city": "Thrissur",
            "district": "Thrissur",
            "address": "Sobha City Mall, Puzhakkal, Thrissur, Kerala 680553",
            "screens": 6,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "4.2 km",
            "active": True
        },
        {
            "name": "Ragam Theatre",
            "city": "Thrissur",
            "district": "Thrissur",
            "address": "Swaraj Round West, Thrissur, Kerala 680001",
            "screens": 2,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "0.8 km",
            "active": True
        },
        {
            "name": "Georgettan's Ragam Cineplex",
            "city": "Thrissur",
            "district": "Thrissur",
            "address": "High Road, Swaraj Round, Thrissur, Kerala 680001",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "0.9 km",
            "active": True
        },
        {
            "name": "Kairali Theatre",
            "city": "Thrissur",
            "district": "Thrissur",
            "address": "Round North, Thrissur, Kerala 680001",
            "screens": 1,
            "formats": ["2D"],
            "distance": "0.5 km",
            "active": True
        },
        {
            "name": "Sree Theatre",
            "city": "Thrissur",
            "district": "Thrissur",
            "address": "Round North, Thrissur, Kerala 680001",
            "screens": 1,
            "formats": ["2D", "3D"],
            "distance": "0.5 km",
            "active": True
        },

        # KOZHIKODE
        {
            "name": "Filmcity Cinemas",
            "city": "Kozhikode",
            "district": "Kozhikode",
            "address": "RP Mall, Mavoor Road, Kozhikode, Kerala 673004",
            "screens": 5,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "1.5 km",
            "active": True
        },
        {
            "name": "Coronation Theatre",
            "city": "Kozhikode",
            "district": "Kozhikode",
            "address": "Mavoor Road, Arayidathupalam, Kozhikode, Kerala 673004",
            "screens": 2,
            "formats": ["2D", "3D", "4K Dolby Atmos"],
            "distance": "1.8 km",
            "active": True
        },
        {
            "name": "Ashok CNC",
            "city": "Kozhikode",
            "district": "Kozhikode",
            "address": "Mavoor Road, Kozhikode, Kerala 673004",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "2.0 km",
            "active": True
        },
        {
            "name": "Kairali Theatre",
            "city": "Kozhikode",
            "district": "Kozhikode",
            "address": "Pavamani Road, Kozhikode, Kerala 673001",
            "screens": 1,
            "formats": ["2D"],
            "distance": "1.1 km",
            "active": True
        },
        {
            "name": "Sree Theatre",
            "city": "Kozhikode",
            "district": "Kozhikode",
            "address": "Pavamani Road, Kozhikode, Kerala 673001",
            "screens": 1,
            "formats": ["2D", "3D"],
            "distance": "1.1 km",
            "active": True
        },

        # ALAPPUZHA
        {
            "name": "Pan Cinemas",
            "city": "Alappuzha",
            "district": "Alappuzha",
            "address": "Velocity Mall, Zero Junction, Alappuzha, Kerala 688001",
            "screens": 4,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "1.2 km",
            "active": True
        },
        {
            "name": "Raiban Cine House",
            "city": "Alappuzha",
            "district": "Alappuzha",
            "address": "CCSSB Road, Near KSRTC Stand, Alappuzha, Kerala 688011",
            "screens": 3,
            "formats": ["2D", "3D"],
            "distance": "0.9 km",
            "active": True
        },
        {
            "name": "Kairali Theatre",
            "city": "Alappuzha",
            "district": "Alappuzha",
            "address": "Mullakkal, Alappuzha, Kerala 688011",
            "screens": 1,
            "formats": ["2D"],
            "distance": "1.5 km",
            "active": True
        },
        {
            "name": "Sree Theatre",
            "city": "Alappuzha",
            "district": "Alappuzha",
            "address": "Mullakkal, Alappuzha, Kerala 688011",
            "screens": 1,
            "formats": ["2D"],
            "distance": "1.5 km",
            "active": True
        },

        # KOLLAM
        {
            "name": "Pranavam Theatre",
            "city": "Kollam",
            "district": "Kollam",
            "address": "Polayathode, Kollam, Kerala 691001",
            "screens": 2,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "2.1 km",
            "active": True
        },
        {
            "name": "Usha Theatre",
            "city": "Kollam",
            "district": "Kollam",
            "address": "Chinnakada, Kollam, Kerala 691001",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "0.6 km",
            "active": True
        },
        {
            "name": "Sree Dhanya Cine Max",
            "city": "Kollam",
            "district": "Kollam",
            "address": "Kottarakkara Road, Kollam, Kerala 691001",
            "screens": 3,
            "formats": ["2D", "3D"],
            "distance": "3.5 km",
            "active": True
        },

        # KANNUR
        {
            "name": "Dhanraj Theatre",
            "city": "Kannur",
            "district": "Kannur",
            "address": "Fort Road, Kannur, Kerala 670001",
            "screens": 2,
            "formats": ["2D", "3D", "4K"],
            "distance": "0.7 km",
            "active": True
        },
        {
            "name": "Liberty Paradise",
            "city": "Kannur",
            "district": "Kannur",
            "address": "Liberty Complex, Stadium Road, Kannur, Kerala 670001",
            "screens": 1,
            "formats": ["2D", "Dolby Atmos"],
            "distance": "1.0 km",
            "active": True
        },
        {
            "name": "Liberty Suite",
            "city": "Kannur",
            "district": "Kannur",
            "address": "Liberty Complex, Stadium Road, Kannur, Kerala 670001",
            "screens": 1,
            "formats": ["2D", "3D"],
            "distance": "1.0 km",
            "active": True
        },
        {
            "name": "Liberty Gold",
            "city": "Kannur",
            "district": "Kannur",
            "address": "Liberty Complex, Stadium Road, Kannur, Kerala 670001",
            "screens": 1,
            "formats": ["2D"],
            "distance": "1.0 km",
            "active": True
        },
        {
            "name": "Kavitha Theatre",
            "city": "Kannur",
            "district": "Kannur",
            "address": "Caltex Junction, Kannur, Kerala 670002",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "1.8 km",
            "active": True
        },

        # KOTTAYAM
        {
            "name": "Abhilash Theatre",
            "city": "Kottayam",
            "district": "Kottayam",
            "address": "TB Road, Kottayam, Kerala 686001",
            "screens": 2,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "0.8 km",
            "active": True
        },
        {
            "name": "Ramya Theatre",
            "city": "Kottayam",
            "district": "Kottayam",
            "address": "KSRTC Bus Stand Road, Kottayam, Kerala 686001",
            "screens": 1,
            "formats": ["2D", "3D"],
            "distance": "1.1 km",
            "active": True
        },
        {
            "name": "Anand Theatre",
            "city": "Kottayam",
            "district": "Kottayam",
            "address": "KK Road, Kottayam, Kerala 686001",
            "screens": 2,
            "formats": ["2D"],
            "distance": "1.4 km",
            "active": True
        },

        # PALAKKAD
        {
            "name": "Priya Theatre",
            "city": "Palakkad",
            "district": "Palakkad",
            "address": "Stadium Bypass Road, Palakkad, Kerala 678001",
            "screens": 2,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "1.2 km",
            "active": True
        },
        {
            "name": "Sree Devi Durga",
            "city": "Palakkad",
            "district": "Palakkad",
            "address": "Gb Road, Palakkad, Kerala 678001",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "0.9 km",
            "active": True
        },
        {
            "name": "Sathya Movie House",
            "city": "Palakkad",
            "district": "Palakkad",
            "address": "Coimbatore Road, Palakkad, Kerala 678001",
            "screens": 2,
            "formats": ["2D"],
            "distance": "2.0 km",
            "active": True
        },
        {
            "name": "Jayabharath Cinema",
            "city": "Palakkad",
            "district": "Palakkad",
            "address": "Near KSRTC Stand, Palakkad, Kerala 678001",
            "screens": 1,
            "formats": ["2D"],
            "distance": "1.5 km",
            "active": True
        },

        # MALAPPURAM
        {
            "name": "Sridevi Cine Palace",
            "city": "Malappuram",
            "district": "Malappuram",
            "address": "Kottappadi, Malappuram, Kerala 676505",
            "screens": 3,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "0.5 km",
            "active": True
        },
        {
            "name": "Vismaya Cinemas",
            "city": "Malappuram",
            "district": "Malappuram",
            "address": "Down Hill, Malappuram, Kerala 676505",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "1.8 km",
            "active": True
        },
        {
            "name": "Carnival Cinemas",
            "city": "Malappuram",
            "district": "Malappuram",
            "address": "Manjeri Road, Malappuram, Kerala 676505",
            "screens": 4,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "3.2 km",
            "active": True
        },
        {
            "name": "Aishwarya Movies",
            "city": "Malappuram",
            "district": "Malappuram",
            "address": "Calicut Road, Malappuram, Kerala 676505",
            "screens": 2,
            "formats": ["2D"],
            "distance": "2.1 km",
            "active": True
        },

        # KASARAGOD & KANHANGAD
        {
            "name": "New Vinayaka",
            "city": "Kasaragod",
            "district": "Kasaragod",
            "address": "MG Road, Kasaragod, Kerala 671121",
            "screens": 2,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "0.8 km",
            "active": True
        },
        {
            "name": "Vinayaka Paradise",
            "city": "Kanhangad",
            "district": "Kasaragod",
            "address": "Kanhangad Town, Kasaragod, Kerala 671315",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "1.5 km",
            "active": True
        },

        # PATHANAMTHITTA
        {
            "name": "Trinity Cinemas",
            "city": "Pathanamthitta",
            "district": "Pathanamthitta",
            "address": "College Road, Pathanamthitta, Kerala 689645",
            "screens": 2,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "1.0 km",
            "active": True
        },
        {
            "name": "Aishwarya Complex",
            "city": "Pathanamthitta",
            "district": "Pathanamthitta",
            "address": "Aban Junction, Pathanamthitta, Kerala 689645",
            "screens": 2,
            "formats": ["2D"],
            "distance": "1.2 km",
            "active": True
        },

        # IDUKKI & THODUPUZHA
        {
            "name": "Laya Cinemas",
            "city": "Thodupuzha",
            "district": "Idukki",
            "address": "Temple Road, Thodupuzha, Kerala 685584",
            "screens": 3,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "1.1 km",
            "active": True
        },
        {
            "name": "Sagara Cinemas",
            "city": "Idukki",
            "district": "Idukki",
            "address": "Kattappana Central, Idukki, Kerala 685508",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "2.5 km",
            "active": True
        },

        # WAYANAD
        {
            "name": "Veena Theatre",
            "city": "Wayanad",
            "district": "Wayanad",
            "address": "Kalpetta Town, Wayanad, Kerala 673121",
            "screens": 2,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "0.9 km",
            "active": True
        },
        {
            "name": "Matha Theatre",
            "city": "Wayanad",
            "district": "Wayanad",
            "address": "Sulthan Bathery, Wayanad, Kerala 673592",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "1.4 km",
            "active": True
        },

        # CINEMA TOWNS SEEDS
        {
            "name": "Matha Theatre, Aluva",
            "city": "Aluva",
            "district": "Ernakulam",
            "address": "Bank Road, Aluva, Ernakulam, Kerala 683101",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "1.0 km",
            "active": True
        },
        {
            "name": "Carnival Cinemas, Angamaly",
            "city": "Angamaly",
            "district": "Ernakulam",
            "address": "Mall of Joy, Angamaly, Ernakulam, Kerala 683572",
            "screens": 3,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "1.2 km",
            "active": True
        },
        {
            "name": "Surabhi Cinema, Chalakudy",
            "city": "Chalakudy",
            "district": "Thrissur",
            "address": "Main Road, Chalakudy, Thrissur, Kerala 680307",
            "screens": 2,
            "formats": ["2D", "3D"],
            "distance": "0.8 km",
            "active": True
        },
        {
            "name": "Liberty Movie House, Thalassery",
            "city": "Thalassery",
            "district": "Kannur",
            "address": "LOGS Road, Thalassery, Kannur, Kerala 670101",
            "screens": 3,
            "formats": ["2D", "3D", "Dolby Atmos"],
            "distance": "0.7 km",
            "active": True
        },
        {
            "name": "Vismaya Cine Max, Perinthalmanna",
            "city": "Perinthalmanna",
            "district": "Malappuram",
            "address": "Bypass Road, Perinthalmanna, Malappuram, Kerala 679322",
            "screens": 3,
            "formats": ["2D", "3D"],
            "distance": "1.1 km",
            "active": True
        }
    ]

    theatre_id_map = {}
    for t in theatres_seed:
        t["city_id"] = city_id_map.get(t["city"])
        existing = db.theatres.find_one({"name": t["name"], "city": t["city"]})
        if not existing:
            t["created_at"] = datetime.now(timezone.utc)
            res = db.theatres.insert_one(t)
            theatre_id_map[t["name"]] = res.inserted_id
        else:
            db.theatres.update_one({"_id": existing["_id"]}, {"$set": {
                "city_id": t["city_id"],
                "address": t["address"],
                "screens": t["screens"],
                "formats": t["formats"],
                "distance": t["distance"],
                "district": t["district"],
                "active": True
            }})
            theatre_id_map[t["name"]] = existing["_id"]

    print(f"✅ Seeded/Updated {len(theatres_seed)} realistic Kerala theatres.")

    # 3. Seed Shows across major movies & theatres for 7 FULL DAYS
    movies = list(db.movies.find({"status": "now_showing"}))
    theatres = list(db.theatres.find({"active": True}))

    if not movies:
        print("⚠️ No active now_showing movies found. Please run seed_database.py first.")
        return

    # Generate 7 consecutive days starting today
    now = datetime.now()
    dates = [(now + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    # Varied schedule templates per weekday type
    weekday_slots = [
        {"time": "10:00 AM", "start_time": "10:00 AM", "end_time": "12:45 PM", "price": 180, "screen": "Screen 1", "format": "2D"},
        {"time": "01:30 PM", "start_time": "01:30 PM", "end_time": "04:15 PM", "price": 220, "screen": "Screen 1", "format": "3D"},
        {"time": "05:00 PM", "start_time": "05:00 PM", "end_time": "07:45 PM", "price": 250, "screen": "Screen 2", "format": "Dolby Atmos"},
        {"time": "08:30 PM", "start_time": "08:30 PM", "end_time": "11:15 PM", "price": 280, "screen": "Screen 1", "format": "4K Dolby Atmos"}
    ]

    weekend_slots = [
        {"time": "09:30 AM", "start_time": "09:30 AM", "end_time": "12:15 PM", "price": 200, "screen": "Screen 1", "format": "2D"},
        {"time": "12:45 PM", "start_time": "12:45 PM", "end_time": "03:30 PM", "price": 250, "screen": "Screen 2", "format": "3D"},
        {"time": "04:15 PM", "start_time": "04:15 PM", "end_time": "07:00 PM", "price": 280, "screen": "Screen 1", "format": "IMAX"},
        {"time": "07:45 PM", "start_time": "07:45 PM", "end_time": "10:30 PM", "price": 300, "screen": "Screen 1", "format": "Dolby Atmos"},
        {"time": "10:45 PM", "start_time": "10:45 PM", "end_time": "01:30 AM", "price": 250, "screen": "Screen 2", "format": "4DX"}
    ]

    new_shows = []
    for day_idx, d in enumerate(dates):
        # Determine day of week
        d_obj = datetime.strptime(d, "%Y-%m-%d")
        is_weekend = d_obj.weekday() in [5, 6] # Saturday or Sunday
        slots_to_use = weekend_slots if is_weekend else weekday_slots

        for t in theatres:
            for m_idx, m in enumerate(movies[:3]): # top 3 movies
                # Select a subset of slots per movie/theatre combo
                start_slot_offset = (m_idx + day_idx) % len(slots_to_use)
                assigned_slots = slots_to_use[start_slot_offset: start_slot_offset + 3]
                if not assigned_slots:
                    assigned_slots = slots_to_use[:2]

                for s_idx, slot in enumerate(assigned_slots):
                    existing_show = db.shows.find_one({
                        "movie_id": m["_id"],
                        "theatre_id": t["_id"],
                        "date": d,
                        "time": slot["time"]
                    })

                    # Calculate demo available seats & status for testing filling fast / sold out
                    if (day_idx + s_idx) % 9 == 0:
                        available_seats = 8 # filling fast demo
                        status = "filling_fast"
                    elif (day_idx + s_idx) % 13 == 0:
                        available_seats = 0 # sold out demo
                        status = "sold_out"
                    else:
                        available_seats = 95
                        status = "available"

                    if not existing_show:
                        new_shows.append({
                            "movie_id": m["_id"],
                            "theatre_id": t["_id"],
                            "screen_id": slot["screen"],
                            "screen": slot["screen"],
                            "date": d,
                            "time": slot["time"],
                            "start_time": slot["start_time"],
                            "end_time": slot["end_time"],
                            "price": float(slot["price"]),
                            "format": slot["format"],
                            "available_seats": available_seats,
                            "total_seats": 120,
                            "status": status,
                            "active": True,
                            "created_at": datetime.now(timezone.utc)
                        })
                    else:
                        # Update existing show with date, start_time, end_time, price, available_seats, status
                        db.shows.update_one({"_id": existing_show["_id"]}, {"$set": {
                            "start_time": slot["start_time"],
                            "end_time": slot["end_time"],
                            "available_seats": available_seats,
                            "total_seats": 120,
                            "status": status,
                            "format": slot["format"],
                            "price": float(slot["price"])
                        }})

    if new_shows:
        db.shows.insert_many(new_shows)
        shows_count = len(new_shows)
    else:
        shows_count = 0

    print(f"✅ Seeded {shows_count} new showtimes across 7 days for Kerala theatres.")
    print("🚀 Kerala Multi-City & 7-Day Showtime Seeding Complete!")

if __name__ == '__main__':
    seed_kerala_data()
