import { getToken } from "./auth.js";

const API_BASE = "/api/v1";

async function request(path, options = {}) {
    const token = getToken();

    options.headers = options.headers || {};
    options.headers["Content-Type"] = "application/json";

    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    const resp = await fetch(API_BASE + path, options);

    if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || "Request failed");
    }

    return resp.json();
}

// Listings
export function apiGetListings() {
    return request("/listings");
}

export function apiCreateListing(payload) {
    return request("/listings", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

// Bookings
export function apiGetBookings() {
    return request("/bookings");
}

export function apiRequestBooking(payload) {
    return request("/bookings/request", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function apiConfirmBooking(id) {
    return request(`/bookings/${id}/confirm`, { method: "PUT" });
}

export function apiCancelBooking(id) {
    return request(`/bookings/${id}/cancel`, { method: "PUT" });
}

export function apiStartSession(id) {
    return request(`/bookings/${id}/start`, { method: "PUT" });
}

export function apiEndSession(id) {
    return request(`/bookings/${id}/end`, { method: "PUT" });
}