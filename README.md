# CineTickets - Modern Movie Ticket Booking System

A full-stack movie ticket booking web application built with Python Flask, Jinja2, HTML5/CSS3/JavaScript, and Cloud MongoDB Atlas.

## Features
- **Cinematic Dark Theme UI**: Premium modern dark mode with cinema red accents (`#E51E2A`).
- **User Authentication**: Registration, Login, Logout, Profile update & Password Change with Werkzeug password hashing.
- **Movies & Showtimes**: Now Showing & Coming Soon carousels, genre/language filter, location picker (`Kochi`).
- **Interactive Seat Selection**: Real-time cinema seat grid (Rows A-K, 1-10) with atomic MongoDB concurrency protection.
- **Food & Drinks**: Movie snack combos, popcorn, beverages, nachos with quantity cart.
- **DEMO Payment System**: Instant payment simulation supporting UPI, Cards, Net Banking, and Wallets.
- **Booking Confirmation & Ticket Download**: Printable PDF/HTML ticket with unique booking ID (`CTK...`).
- **My Bookings History**: User booking overview.

## Setup & Running Locally

1. **Activate Virtual Environment**:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```powershell
   python -m pip install -r requirements.txt
   ```

3. **Verify Database Connection**:
   ```powershell
   python test_mongodb.py
   ```

4. **Seed Sample Data**:
   ```powershell
   python seed_database.py
   ```

5. **Start Flask Server**:
   ```powershell
   python app.py
   ```
   Open browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Credentials
- **User**: `user@cinetickets.com` / `user123`
- **Admin**: `admin@cinetickets.com` / `Admin@123`
