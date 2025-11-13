const API_BASE = "https://remote-servers-marketplace-test.onrender.com/api/v1";

export async function getListings() {
  const res = await fetch(`${API_BASE}/listings/`);
  return res.json();
}

export async function createBooking(listingId, buyerName, start, end) {
  const payload = { listing_id: listingId, buyer_name: buyerName, start_time: start, end_time: end };
  const res = await fetch(`${API_BASE}/bookings/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}