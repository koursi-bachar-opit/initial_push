import {
    apiGetBookings,
    apiConfirmBooking,
    apiCancelBooking,
    apiStartSession,
    apiEndSession,
} from "./api.js";

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("bookings");
    const role = localStorage.getItem("user_role");

    let bookings = [];
    try {
        bookings = await apiGetBookings();
    } catch (e) {
        container.innerHTML = `<p class="text-red-600">${e.message}</p>`;
        return;
    }

    container.innerHTML = bookings
        .map((b) => {
            let action = "";

            if (role === "provider") {
                if (b.status === "PENDING") {
                    action = `<button data-id="${b.id}" data-act="confirm" class="btn">Confirm</button>`;
                } else if (b.status === "CONFIRMED") {
                    action = `<button data-id="${b.id}" data-act="start" class="btn">Start Session</button>`;
                } else if (b.status === "ACTIVE") {
                    action = `<button data-id="${b.id}" data-act="end" class="btn">End Session</button>`;
                }
            }

            if (role === "buyer" && b.status !== "ACTIVE" && b.status !== "COMPLETED") {
                action = `<button data-id="${b.id}" data-act="cancel" class="btn">Cancel</button>`;
            }

            return `
            <div class="p-4 bg-white border rounded-lg shadow">
                <h3 class="font-semibold">Booking #${b.id}</h3>
                <p class="text-gray-600">Status: ${b.status}</p>
                <p class="text-gray-600">Listing: ${b.listing_id}</p>
                <p class="text-gray-600">Buyer: ${b.buyer_name}</p>

                <div class="mt-3">${action}</div>
            </div>`;
        })
        .join("");

    document.querySelectorAll("[data-act]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const id = Number(btn.dataset.id);
            const act = btn.dataset.act;

            try {
                if (act === "confirm") await apiConfirmBooking(id);
                if (act === "cancel") await apiCancelBooking(id);
                if (act === "start") await apiStartSession(id);
                if (act === "end") await apiEndSession(id);
                location.reload();
            } catch (e) {
                alert("Error: " + e.message);
            }
        });
    });
});