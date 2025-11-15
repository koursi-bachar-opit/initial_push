const API_BASE = "/api/v1";
const tbody = document.getElementById("bookings-body");
let cancelId = null;

async function loadBookings() {
  const res = await fetch(`${API_BASE}/bookings/`);
  const rows = await res.json();

  tbody.innerHTML = rows.map(b => `
    <tr class="border-t">
      <td class="px-6 py-4">${b.listing_title ?? ("Listing #" + b.listing_id)}</td>
      <td class="px-6 py-4">${b.buyer_name}</td>
      <td class="px-6 py-4">${new Date(b.start_time).toLocaleString()}</td>
      <td class="px-6 py-4">${b.end_time ? new Date(b.end_time).toLocaleString() : "-"}</td>
      <td class="px-6 py-4">
        <span class="rounded-full px-2.5 py-0.5 text-xs font-medium
          ${b.status === "ACTIVE" ? "bg-green-100 text-green-700"
            : b.status === "PENDING" ? "bg-yellow-100 text-yellow-800"
            : b.status === "CANCELLED" ? "bg-red-100 text-red-700"
            : "bg-gray-100 text-gray-700"}">${b.status}</span>
      </td>
      <td class="px-6 py-4 text-right">
        <button class="rounded border px-2.5 py-1.5 text-sm cancel-btn"
                data-id="${b.id}"
                data-modal-target="cancel-modal" 
                data-modal-toggle="cancel-modal">
          Cancel
        </button>
      </td>
    </tr>
  `).join("");

  document.querySelectorAll(".cancel-btn").forEach(btn =>
    btn.addEventListener("click", () => cancelId = btn.dataset.id)
  );
}

document.getElementById("confirm-cancel").addEventListener("click", async () => {
  if (!cancelId) return;
  await fetch(`${API_BASE}/bookings/${cancelId}/cancel`, { method: "PUT" });

  cancelId = null;
  document.querySelector('[data-modal-hide="cancel-modal"]').click();
  await loadBookings();
});

loadBookings();