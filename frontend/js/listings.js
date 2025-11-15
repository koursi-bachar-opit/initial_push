import { getListings, createBooking } from "./api.js";

async function showListings() {
  const listings = await getListings();
  const container = document.getElementById("listings");

  const role = localStorage.getItem("user_role");

  container.innerHTML = listings
    .map(
      (l) => `
    <div class="p-4 border rounded-lg bg-white shadow mb-4">
      <h3 class="font-semibold">${l.title}</h3>
      <p class="text-gray-500">$${l.price}/hr</p>

      ${
        role === "buyer"
          ? `<button class="bg-blue-600 text-white px-3 py-1 rounded mt-2" data-id="${l.id}">
              Book
            </button>`
          : ``
      }
    </div>
  `
    )
    .join("");

  document.querySelectorAll("[data-id]").forEach((btn) => {
    btn.addEventListener("click", () => bookServer(btn.dataset.id));
  });
}

async function bookServer(listingId) {
  const now = new Date();
  const end = new Date(now.getTime() + 60 * 60 * 1000);

  await createBooking(
    listingId,
    "buyer",
    now.toISOString(),
    end.toISOString()
  );

  alert("Booking created!");
}

showListings();