import { apiGetListings, apiRequestBooking } from "./api.js";

const listingsGrid = document.getElementById("listingsGrid");
const myListingsGrid = document.getElementById("myListingsGrid");
const role = localStorage.getItem("user_role");
const userId = localStorage.getItem("user_id");

let listings = [];
let selectedListing = null;

//modal DOM references (Flowbite)
const modalEl = document.getElementById("listingDetailsModal");
const modalTitle = document.getElementById("modalTitle");
const modalDescription = document.getElementById("modalDescription");
const modalPrice = document.getElementById("modalPrice");
const modalMeta = document.getElementById("modalMeta");
const modalBookButton = document.getElementById("modalBookButton");

//Flowbite modal instance is constructed after Flowbite loads
let modal;

document.addEventListener("DOMContentLoaded", async () => {
    //create modal instance safely
    modal = new Modal(modalEl);

    try {
        listings = await apiGetListings();
    } catch (err) {
        listingsGrid.innerHTML = `<p class="text-red-600">${err.message}</p>`;
        return;
    }

    renderListings();
});


//render listings
function renderListings() {
    listingsGrid.innerHTML = listings
        .map((l) => listingCardHTML(l))
        .join("");

    if (myListingsGrid) {
        const mine = listings.filter((l) => String(l.provider_user_id) === userId);
        myListingsGrid.innerHTML = mine.map((l) => listingCardHTML(l)).join("");
    }

    document.querySelectorAll(".btn-view-details").forEach((btn) => {
        btn.addEventListener("click", () => openDetailsModal(btn.dataset.id));
    });
}


//Card UI to format listing boxes
function listingCardHTML(l) {
    return `
        <div class="bg-white dark:bg-gray-800 shadow border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition">
            <div class="p-5">
                <h3 class="text-lg font-bold mb-1 text-gray-900 dark:text-white">${l.title}</h3>
                <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-2 mb-3">
                    ${l.description || "No description provided."}
                </p>
                <p class="text-blue-600 dark:text-blue-400 font-semibold mb-2">$${l.price}/hr</p>

                <button 
                    data-id="${l.id}"
                    class="btn-view-details w-full mt-2 px-4 py-2 bg-gray-900 text-white rounded hover:bg-black dark:hover:bg-gray-700 transition text-sm"
                    data-modal-target="listingDetailsModal"
                    data-modal-toggle="listingDetailsModal">
                    View Details
                </button>
            </div>
        </div>
    `;
}

//Open modal (check listing description)
function openDetailsModal(id) {
    selectedListing = listings.find((l) => String(l.id) === String(id));
    if (!selectedListing) return;

    modalTitle.textContent = selectedListing.title;
    modalDescription.textContent = selectedListing.description || "No description.";
    modalPrice.textContent = `$${selectedListing.price}/hr`;
    modalMeta.textContent = `Listing ID: ${selectedListing.id}`;

    if (modalBookButton) {
        modalBookButton.onclick = handleBookingRequest;
    }

    modal.show();
}


//Booking request selection (booking window one hour default for test)
async function handleBookingRequest() {
    if (!selectedListing) return;

    const now = new Date();
    const end = new Date(now.getTime() + 60 * 60 * 1000);

    try {
        await apiRequestBooking({
            listing_id: selectedListing.id,
            start_time: now.toISOString(),
            end_time: end.toISOString(),
        });

        alert("Booking request sent!");
        modal.hide();
    } catch (err) {
        alert("Error: " + err.message);
    }
}