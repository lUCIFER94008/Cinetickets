// CineTickets Food Cart & Booking Payment Engine
let foodCart = {};

function updateFoodQuantity(name, price, change) {
    if (!foodCart[name]) {
        foodCart[name] = { name: name, price: price, qty: 0 };
    }
    foodCart[name].qty += change;
    if (foodCart[name].qty <= 0) {
        delete foodCart[name];
    }

    const qtyEl = document.getElementById(`qty-${name.replace(/\s+/g, '-')}`);
    if (qtyEl) {
        qtyEl.innerText = foodCart[name] ? foodCart[name].qty : 0;
    }

    renderFoodSummary();
}

function renderFoodSummary() {
    let foodTotal = 0;
    const foodListEl = document.getElementById('food-cart-items');
    if (foodListEl) {
        foodListEl.innerHTML = '';
        Object.values(foodCart).forEach(item => {
            foodTotal += item.price * item.qty;
            const li = document.createElement('li');
            li.style.display = 'flex';
            li.style.justifyContent = 'space-between';
            li.style.marginBottom = '0.4rem';
            li.innerText = `${item.name} x${item.qty} - ₹${(item.price * item.qty).toFixed(2)}`;
            foodListEl.appendChild(li);
        });
    }

    const foodTotalEl = document.getElementById('food-total-display');
    if (foodTotalEl) {
        foodTotalEl.innerText = `₹${foodTotal.toFixed(2)}`;
    }

    sessionStorage.setItem('food_cart', JSON.stringify(Object.values(foodCart)));
    sessionStorage.setItem('food_total', foodTotal);
}

async function submitFinalBooking(paymentMethod) {
    const showId = sessionStorage.getItem('current_show_id');
    const selectedSeats = JSON.parse(sessionStorage.getItem('selected_seats') || '[]');
    const foodItems = JSON.parse(sessionStorage.getItem('food_cart') || '[]');

    if (!showId || selectedSeats.length === 0) {
        showToast('Session expired or no seats selected. Please select seats again.', 'warning');
        window.location.href = '/movies';
        return;
    }

    const payBtn = document.getElementById('pay-submit-btn');
    if (payBtn) {
        payBtn.disabled = true;
        payBtn.innerText = 'Processing Payment...';
    }

    try {
        const response = await fetch('/api/bookings/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                show_id: showId,
                seats: selectedSeats,
                food_items: foodItems,
                payment_method: paymentMethod
            })
        });

        const data = await response.json();
        if (data.success) {
            sessionStorage.removeItem('selected_seats');
            sessionStorage.removeItem('food_cart');
            window.location.href = `/booking/success/${data.booking.id || data.booking._id}`;
        } else {
            showToast(data.message || 'Booking failed.', 'danger');
            if (payBtn) {
                payBtn.disabled = false;
                payBtn.innerText = 'Try Again';
            }
        }
    } catch (err) {
        showToast('Network or server error during payment.', 'danger');
        if (payBtn) {
            payBtn.disabled = false;
            payBtn.innerText = 'Try Again';
        }
    }
}
