// Interactive Cinema Seat Selection Engine
let selectedSeats = [];
let totalAmount = 0;
const MAX_SEATS = 8;

document.addEventListener('DOMContentLoaded', () => {
    // Clear old selections on fresh page load if needed
    const seats = document.querySelectorAll('.seat:not(.booked)');
    seats.forEach(seat => {
        seat.addEventListener('click', () => {
            const seatNumber = seat.dataset.seatNumber;
            const price = parseFloat(seat.dataset.price || 220);

            if (seat.classList.contains('selected')) {
                seat.classList.remove('selected');
                selectedSeats = selectedSeats.filter(s => s !== seatNumber);
                totalAmount -= price;
            } else {
                if (selectedSeats.length >= MAX_SEATS) {
                    if (typeof showToast === 'function') {
                        showToast(`Maximum ${MAX_SEATS} seats allowed per booking.`, 'warning');
                    } else {
                        alert(`Maximum ${MAX_SEATS} seats allowed per booking.`);
                    }
                    return;
                }
                seat.classList.add('selected');
                selectedSeats.push(seatNumber);
                totalAmount += price;
            }

            updateSeatSelectionUI();
        });
    });
});

function updateSeatSelectionUI() {
    const displaySeats = document.getElementById('selected-seats-display');
    const displayTotal = document.getElementById('selected-total-display');
    const continueBtn = document.getElementById('continue-to-food-btn');

    if (displaySeats) {
        displaySeats.innerText = selectedSeats.length > 0 ? selectedSeats.join(', ') : 'None';
    }
    if (displayTotal) {
        displayTotal.innerText = `₹${totalAmount.toFixed(2)}`;
    }
    if (continueBtn) {
        continueBtn.disabled = selectedSeats.length === 0;
        continueBtn.style.opacity = selectedSeats.length === 0 ? '0.5' : '1';
    }

    // Save selection to SessionStorage
    sessionStorage.setItem('selected_seats', JSON.stringify(selectedSeats));
    sessionStorage.setItem('ticket_total', totalAmount);
}

function proceedToFoodOrPayment(showId) {
    if (selectedSeats.length === 0) {
        if (typeof showToast === 'function') {
            showToast('Please select at least one seat.', 'warning');
        } else {
            alert('Please select at least one seat.');
        }
        return;
    }
    sessionStorage.setItem('current_show_id', showId);
    window.location.href = `/booking/summary?show_id=${showId}`;
}
