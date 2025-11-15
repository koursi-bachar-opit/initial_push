import { apiGetListings, apiRequestBooking } from "./api.js";

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("listings");
    const role = localStorage.getItem("user_role");

    let listings = [];
    try {
        listings = await apiGetListings();
    } catch (e) {
        container.innerHTML = `<p class="text-red-600">${e.message}</p>`;
        return;
    }

    container.innerHTML = listings
        .map(
            (l) => `
        <div class="p-4 bg-white border rounded-lg shadow">
            <h3 class="font-semibold">${l.title}</h3>
            <p class="text-gray-600">$${l.price}/hr</p>

            ${
                role === "buyer"
                    ? `<button class="mt-2 bg-blue-600 text-white px-3 py-1 rounded book-btn" data-id="${l.id}">
                        Request Booking
                    </button>`
                    : ""
            }
        </div>
    `
        )
        .join("");

    document.querySelectorAll(".book-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;

            const now = new Date();
            const end = new Date(now.getTime() + 60 * 60 * 1000);

            try {
                await apiRequestBooking({
                    listing_id: Number(id),
                    start_time: now.toISOString(),
                    end_time: end.toISOString(),
                });

                alert("Booking request sent!");
            } catch (e) {
                alert("Error: " + e.message);
            }
        });
    });
});