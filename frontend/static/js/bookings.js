import {
    apiGetBookings,
    apiConfirmBooking,
    apiCancelBooking,
    apiStartSession,
    apiEndSession,
} from "./api.js";

// check bookings
document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("bookings");
    const emptyState = document.getElementById("empty-state");

    if (!container) {
        console.error("Element #bookings not found.");
        return;
    }

    const role = localStorage.getItem("user_role");

    let bookings = [];
    try {
        bookings = await apiGetBookings();
    } catch (e) {
        container.innerHTML = `
            <div class="col-span-full">
                <div class="p-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
                    <div class="flex items-center">
                        <svg class="flex-shrink-0 w-4 h-4 me-2" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z"/>
                        </svg>
                        <span class="font-medium">Error loading bookings:</span> ${e.message}
                    </div>
                </div>
            </div>
        `;
        return;
    }

    // Show empty state if no bookings
    if (bookings.length === 0) {
        container.classList.add("hidden");
        if (emptyState) emptyState.classList.remove("hidden");
    } else {
        container.classList.remove("hidden");
        if (emptyState) emptyState.classList.add("hidden");
        container.innerHTML = bookings.map(b => bookingCardHTML(b, role)).join("");

        // Attach button handlers
        document.querySelectorAll("[data-act]").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                const act = btn.dataset.act;

                if (act === "cancel") {
                    const ok = confirm("Are you sure you want to cancel this booking?");
                    if (!ok) return;
                }            

                try {
                    if (act === "confirm") await apiConfirmBooking(id);
                    if (act === "cancel") await apiCancelBooking(id);
                    if (act === "start") await apiStartSession(id);
                    if (act === "end") await apiEndSession(id);

                    location.reload();
                } catch (e) {
                    alert("Error: " + e.message);
                }
            });
        });
    }
});


// Modern card design
function bookingCardHTML(b, role) {
    return `
        <div class="group relative bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all duration-200 overflow-hidden">
            
            <div class="absolute top-0 left-0 w-1.5 h-full ${getStatusColor(b.status)}"></div>

            <div class="p-5">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                            Booking #${b.id}
                        </h3>
                        <div class="flex items-center mt-1">
                            ${statusBadge(b.status)}
                        </div>
                    </div>
                    <div class="text-gray-400 dark:text-gray-500">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                </div>

                <div class="space-y-4">
                    <div class="flex items-start">
                        <div class="flex-shrink-0 mt-0.5">
                            <svg class="w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Listing</p>
                            <p class="text-sm font-semibold text-gray-900 dark:text-white">${b.listing_title || "Listing " + b.listing_id}</p>
                        </div>
                    </div>

                    <div class="flex items-start">
                        <div class="flex-shrink-0 mt-0.5">
                            <svg class="w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Buyer</p>
                            <p class="text-sm font-semibold text-gray-900 dark:text-white">${b.buyer_email || "Unknown"}</p>
                        </div>
                    </div>

                    <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Start</span>
                            <span class="text-sm font-semibold text-gray-900 dark:text-white">${formatDate(b.start_time)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">End</span>
                            <span class="text-sm font-semibold text-gray-900 dark:text-white">${formatDate(b.end_time)}</span>
                        </div>
                    </div>
                </div>

                <div class="mt-6 pt-5 border-t border-gray-200 dark:border-gray-700">
                    ${actionHTML(b, role)}
                </div>
            </div>
        </div>
    `;
}


// Action buttons with updated logic
function actionHTML(b, role) {
    const id = b.id;

    if (role === "provider") {
        if (b.status === "requested") return btn("confirm", "Confirm Booking", id, "blue");
        if (b.status === "confirmed") return btn("start", "Start Session", id, "green");
        if (b.status === "active") return btn("end", "End Session", id, "red");
    }

    // Updated: Only show cancel for buyer if status is requested or pending_payment
    if (role === "buyer" && (b.status === "requested" || b.status === "pending_payment")) {
        return btn("cancel", "Cancel Booking", id, "red");
    }

    return `
        <div class="text-center py-2">
            <span class="text-sm text-gray-400 dark:text-gray-500">No actions available</span>
        </div>
    `;
}

function btn(act, label, id, color = "blue") {
    const colorClasses = {
        blue: "bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-400",
        green: "bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-400",
        red: "bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-400",
        gray: "bg-gray-600 hover:bg-gray-700 dark:bg-gray-500 dark:hover:bg-gray-400"
    };

    return `
        <button data-id="${id}"
                data-act="${act}"
                class="w-full px-4 py-3 text-sm font-medium text-white 
                       ${colorClasses[color]}
                       rounded-lg transition-all duration-200 
                       hover:shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-${color}-500">
            ${label}
        </button>
    `;
}

// Status color for indicator bar
function getStatusColor(status) {
    const colors = {
        requested: "bg-yellow-400",
        pending_payment: "bg-yellow-400",
        confirmed: "bg-blue-400",
        active: "bg-green-400",
        completed: "bg-gray-400",
        cancelled: "bg-red-400",
    };
    return colors[status] || "bg-gray-400";
}

// Enhanced status badge
function statusBadge(status) {
    const config = {
        requested: {
            text: "Requested",
            class: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
        },
        pending_payment: {
            text: "Payment Pending",
            class: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
        },
        confirmed: {
            text: "Confirmed",
            class: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
        },
        active: {
            text: "Active",
            class: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
        },
        completed: {
            text: "Completed",
            class: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
        },
        cancelled: {
            text: "Cancelled",
            class: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
        }
    };

    const cfg = config[status] || {
        text: status,
        class: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
    };

    return `
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cfg.class}">
            ${cfg.text}
        </span>
    `;
}

function formatDate(str) {
    if (!str) return "-";
    const date = new Date(str);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}