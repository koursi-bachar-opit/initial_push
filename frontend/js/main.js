import { getListings, createBooking } from "./api.js";

async function showListings() {
  const listings = await getListings();
  const container = document.getElementById("listings");
  container.innerHTML = listings.map(l => `
    <div class="p-4 border rounded-lg bg-white shadow mb-4">
      <h3 class="font-semibold">${l.title}</h3>
      <p class="text-gray-500">$${l.price}/hr</p>
      <button class="bg-blue-600 text-white px-3 py-1 rounded mt-2"
              onclick="bookServer(${l.id})">
        Book
      </button>
    </div>
  `).join("");
}

window.bookServer = async (listingId) => {
  const now = new Date();
  const end = new Date(now.getTime() + 60 * 60 * 1000);
  await createBooking(listingId, "testuser", now.toISOString(), end.toISOString());
  alert("Booking created!");
};

showListings();