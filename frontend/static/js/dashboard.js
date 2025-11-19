import { apiGetBookings } from "./api.js";

//body targets
const pendingBody = document.getElementById("pendingBody");
const pastBody = document.getElementById("pastBody");

//dashboard stats
const statTotal = document.getElementById("stat-total");
const statPending = document.getElementById("stat-pending");
const statActive = document.getElementById("stat-active");
const statPast = document.getElementById("stat-past");

//Check booking history type (pending or past)
document.addEventListener("DOMContentLoaded", async () => {
    let bookings = [];

    try {
        bookings = await apiGetBookings();
    } catch (err) {
        pendingBody.innerHTML = errorRow(err.message);
        pastBody.innerHTML = errorRow(err.message);
        return;
    }

    const pending = bookings.filter(b =>
        ["requested", "confirmed", "active"].includes(b.status)
    );

    const past = bookings.filter(b =>
        ["cancelled", "completed"].includes(b.status)
    );

    //stats
    statTotal.textContent = bookings.length;
    statPending.textContent = pending.length;
    statActive.textContent = bookings.filter(b => b.status === "active").length;
    statPast.textContent = past.length;

    pendingBody.innerHTML = pending.length
        ? pending.map(rowHTML).join("")
        : emptyRow(5, "No pending bookings.");

    pastBody.innerHTML = past.length
        ? past.map(rowHTML).join("")
        : emptyRow(5, "No past bookings.");
});

//Helpers
function rowHTML(b) {
    return `
        <tr class="bg-white border-b hover:bg-gray-50">
            <td class="px-6 py-4 font-medium">#${b.id}</td>
            <td class="px-6 py-4">${b.listing_title || "Listing " + b.listing_id}</td>
            <td class="px-6 py-4">${b.buyer_email || "Unknown"}</td>
            <td class="px-6 py-4">${scheduleHTML(b)}</td>
            <td class="px-6 py-4">${statusBadge(b.status)}</td>
        </tr>
    `;
}

function scheduleHTML(b) {
    return `
        <div>
            <div><span class="font-medium">Start:</span> ${formatDate(b.start_time)}</div>
            <div><span class="font-medium">End:</span> ${formatDate(b.end_time)}</div>
        </div>
    `;
}

function statusBadge(status) {
    const colors = {
        requested: "bg-yellow-100 text-yellow-800",
        confirmed: "bg-blue-100 text-blue-800",
        active: "bg-green-100 text-green-800",
        completed: "bg-gray-100 text-gray-800",
        cancelled: "bg-red-100 text-red-800",
    };
    return `<span class="px-2.5 py-0.5 text-xs rounded ${colors[status]}">${status}</span>`;
}

function emptyRow(colspan, text) {
    return `<tr><td colspan="${colspan}" class="px-6 py-6 text-center text-gray-500">${text}</td></tr>`;
}

function errorRow(msg) {
    return `<tr><td colspan="5" class="px-6 py-6 text-center text-red-600">${msg}</td></tr>`;
}

function formatDate(str) {
    return str ? new Date(str).toLocaleString() : "-";
}