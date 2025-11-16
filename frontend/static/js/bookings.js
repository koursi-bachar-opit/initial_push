import {
    apiGetBookings,
    apiConfirmBooking,
    apiCancelBooking,
    apiStartSession,
    apiEndSession,
} from "./api.js";

//check bookings
document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("bookings");

    if (!container) {
        console.error("Element #bookings not found.");
        return;
    }

    const role = localStorage.getItem("user_role");

    let bookings = [];
    try {
        bookings = await apiGetBookings();
    } catch (e) {
        container.innerHTML = `<p class="text-red-600">${e.message}</p>`;
        return;
    }

    container.innerHTML = bookings.map(b => bookingCardHTML(b, role)).join("");

    //Attach button, choose bookings actions
    document.querySelectorAll("[data-act]").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = Number(btn.dataset.id);
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
});


//Flowbite card
function bookingCardHTML(b, role) {
    return `
        <div class="border rounded-lg shadow bg-white hover:shadow-md transition overflow-hidden">

            <!-- HEADER -->
            <div class="px-5 py-4 border-b bg-gray-50 flex justify-between items-center">
                <h3 class="text-lg font-semibold">Booking #${b.id}</h3>
                ${statusBadge(b.status)}
            </div>

            <!-- BODY -->
            <div class="px-5 py-4 space-y-4 text-gray-700">

                <div>
                    <div class="text-sm text-gray-500">Listing</div>
                    <div class="font-medium">${b.listing_title || "Listing " + b.listing_id}</div>
                </div>

                <div>
                    <div class="text-sm text-gray-500">Buyer</div>
                    <div class="font-medium">${b.buyer_email || "Unknown"}</div>
                </div>

                <div>
                    <div class="text-sm text-gray-500">Start</div>
                    <div>${formatDate(b.start_time)}</div>
                </div>

                <div>
                    <div class="text-sm text-gray-500">End</div>
                    <div>${formatDate(b.end_time)}</div>
                </div>
            </div>

            <!-- FOOTER (ACTION BUTTONS) -->
            <div class="px-5 py-4 border-t bg-gray-50">
                ${actionHTML(b, role)}
            </div>

        </div>
    `;
}


//Action buttons
function actionHTML(b, role) {
    const id = b.id;

    if (role === "provider") {
        if (b.status === "requested") return btn("confirm", "Confirm", id);
        if (b.status === "confirmed") return btn("start", "Start Session", id);
        if (b.status === "active") return btn("end", "End Session", id);
    }

    if (role === "buyer" && !["active", "completed"].includes(b.status)) {
        return btn("cancel", "Cancel", id);
    }

    return `<span class="text-gray-400 text-sm">No actions</span>`;
}

function btn(act, label, id) {
    return `
        <button data-id="${id}"
                data-act="${act}"
                class="w-full px-4 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-black transition">
            ${label}
        </button>
    `;
}

//Badge and date helpers
function statusBadge(status) {
    const cls = {
        requested: "bg-yellow-100 text-yellow-800",
        confirmed: "bg-blue-100 text-blue-800",
        active:    "bg-green-100 text-green-800",
        completed: "bg-gray-100 text-gray-800",
        cancelled: "bg-red-100 text-red-800",
    }[status] || "bg-gray-100 text-gray-800";

    return `<span class="px-2.5 py-1 rounded text-xs font-medium ${cls}">${status}</span>`;
}

function formatDate(str) {
    return str ? new Date(str).toLocaleString() : "-";
}