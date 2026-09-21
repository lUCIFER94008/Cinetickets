// CineTickets Main JavaScript Helpers & Location Manager
document.addEventListener('DOMContentLoaded', () => {
    // Graceful fallback for broken image URLs
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', () => {
            img.src = 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=800&auto=format&fit=crop';
        });
    });

    // Auto-dismiss alert flashes
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });

    // Initialize Kerala City Location System
    initCityLocationSystem();
});

function initCityLocationSystem() {
    const modalOverlay = document.getElementById('cityModalOverlay');
    const openBtn = document.getElementById('openLocationModalBtn');
    const closeBtn = document.getElementById('closeCityModalBtn');
    const searchInput = document.getElementById('citySearchInput');
    const cityButtons = document.querySelectorAll('.city-item-btn');
    const locationText = document.getElementById('current-location-text');

    // Get current URL city param or stored city
    const urlParams = new URLSearchParams(window.location.search);
    const urlCity = urlParams.get('city');

    let currentCity = urlCity || localStorage.getItem('selectedCity') || getCookie('selected_city') || 'Kochi';

    // Persist current city
    localStorage.setItem('selectedCity', currentCity);
    setCookie('selected_city', currentCity, 30);

    if (locationText && locationText.innerText !== currentCity) {
        locationText.innerText = currentCity;
    }

    // Highlight selected city button
    cityButtons.forEach(btn => {
        const btnCity = btn.dataset.city;
        if (btnCity && btnCity.toLowerCase() === currentCity.toLowerCase()) {
            btn.classList.add('selected');
        } else {
            btn.classList.remove('selected');
        }
    });

    // Modal open/close controls
    if (openBtn && modalOverlay) {
        openBtn.addEventListener('click', () => {
            modalOverlay.classList.add('active');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 150);
            }
        });
    }

    if (closeBtn && modalOverlay) {
        closeBtn.addEventListener('click', () => {
            modalOverlay.classList.remove('active');
        });
    }

    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                modalOverlay.classList.remove('active');
            }
        });
    }

    // Live search filtering
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            cityButtons.forEach(btn => {
                const cityName = btn.dataset.city ? btn.dataset.city.toLowerCase() : '';
                if (cityName.includes(query)) {
                    btn.style.display = 'flex';
                } else {
                    btn.style.display = 'none';
                }
            });
        });
    }

    // City Selection Handler
    cityButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const chosenCity = btn.dataset.city;
            if (!chosenCity) return;

            localStorage.setItem('selectedCity', chosenCity);
            setCookie('selected_city', chosenCity, 30);

            if (locationText) {
                locationText.innerText = chosenCity;
            }

            modalOverlay.classList.remove('active');

            // Refresh or update page with selected city query param
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('city', chosenCity);
            window.location.href = currentUrl.toString();
        });
    });
}

function setCookie(name, value, days = 30) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "; expires=" + date.toUTCString();
    document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.boxShadow = '0 8px 24px rgba(0,0,0,0.5)';
    toast.style.marginBottom = '0.5rem';
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}
