const API_BASE = "/api/v1";

function authHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { "Authorization": `Bearer ${token}` } : {};
}

export async function getListings() {
  const res = await fetch(`${API_BASE}/listings/`, {
    headers: authHeaders(),
  });
  return res.json();
}

export async function createBooking(listingId, buyerName, start, end) {
  const payload = { listing_id: listingId, buyer_name: buyerName, start_time: start, end_time: end };

  const res = await fetch(`${API_BASE}/bookings/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(payload)
  });

  return res.json();
}