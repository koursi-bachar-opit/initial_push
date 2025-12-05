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
        let errorDetail = "Request failed";
        try {
            const errorData = await resp.json();
            errorDetail = errorData.detail || JSON.stringify(errorData) || resp.statusText;
        } catch {
            errorDetail = resp.statusText;
        }
        throw new Error(`${resp.status}: ${errorDetail}`);
    }

    //for 204 no content responses, return null
    if (resp.status === 204) {
        return null;
    }

    return resp.json();
}


//Listings
export function apiGetListings() {
    return request("/listings");
}

export function apiCreateListing(payload) {
    return request("/listings", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}


//Bookings
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

//Machines
export function apiGetMachines() {
    return request("/machines");
}

export function apiCreateMachine(payload) {
    return request("/machines", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

//Admin provider endpoints
export async function apiGetProviders() {
    return request("/providers/admin/providers");
}

export async function apiGetProviderStats() {
    return request("/providers/admin/stats");
}

export async function apiVerifyProvider(providerId, status, notes = "") {
    //First get the verification ID for this provider
    const verifications = await request(`/providers/admin/providers/${providerId}/verifications`);
    const latestVerification = verifications[0]; //Get the most recent verification
    
    if (!latestVerification) {
        throw new Error("No verification request found for this provider");
    }
    
    return request(`/providers/verification/${latestVerification.id}/review`, {
        method: "POST",
        body: JSON.stringify({ status, notes }),
    });
}

export async function apiGetProviderVerifications(providerId) {
    return request(`/providers/admin/providers/${providerId}/verifications`);
}

export function apiSearchListings(searchTerm) {
    return request(`/listings/search?name=${encodeURIComponent(searchTerm)}`);
}

//Advanced Listings Search with Filters
export function apiSearchListingsWithFilters(filters = {}) {
    const params = new URLSearchParams();
    
    // Add all filter parameters
    Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
            params.append(key, value);
        }
    });
    
    return request(`/listings/search/filter?${params}`);
}