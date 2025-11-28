import {
    apiGetBookings,
    apiCreateListing,
    apiGetMachines,
    apiCreateMachine,
} from "./api.js";

//body targets
const pendingBody = document.getElementById("pendingBody");
const pastBody = document.getElementById("pastBody");

//dashboard stats
const statTotal = document.getElementById("stat-total");
const statPending = document.getElementById("stat-pending");
const statActive = document.getElementById("stat-active");
const statPast = document.getElementById("stat-past");

//listing form (provider access only)
const createListingForm = document.getElementById("create-listing-form");
const machineSelect = document.getElementById("machineSelect");
const openCreateListingBtn = document.getElementById("openCreateListingModal");
const noMachinesWarning = document.getElementById("no-machines-warning");

//machine form
const createMachineForm = document.getElementById("create-machine-form");

//internal machine cache
let machines = [];

document.addEventListener("DOMContentLoaded", async () => {
    //Load machines first
    await loadMachines();

    //Load bookings
    await loadBookings();

    //Listing creation handler
    if (createListingForm) {
        createListingForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const fd = new FormData(createListingForm);
            const payload = {
                machine_id: Number(fd.get("machine_id")),
                title: fd.get("title"),
                price: Number(fd.get("price")),
            };

            try {
                await apiCreateListing(payload);
                alert("Listing created!");

                //Close modal
                document
                    .querySelector('[data-modal-hide="createListingModal"]')
                    ?.click();

                createListingForm.reset();
                location.reload(); //reload to update tables
            } catch (err) {
                alert("Error: " + err.message);
            }
        });
    }

    //Machine creation handler
    if (createMachineForm) {
        createMachineForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const fd = new FormData(createMachineForm);
            const payload = {
                hostname: fd.get("hostname"),
            };

            try {
                await apiCreateMachine(payload);
                alert("Machine added!");

                //Close modal
                document
                    .querySelector('[data-modal-hide="createMachineModal"]')
                    ?.click();

                createMachineForm.reset();

                //Refresh machines list and repopulate dropdown
                await loadMachines();
            } catch (err) {
                alert("Error: " + err.message);
            }
        });
    }
});


//Load machines and update UI state
async function loadMachines() {
    if (!machineSelect) return; //buyer dashboard

    try {
        machines = await apiGetMachines();
    } catch (err) {
        console.error("Failed to load machines:", err);
        machines = [];
    }

    //Machines UI state
    if (machines.length === 0) {
        openCreateListingBtn.disabled = true;
        noMachinesWarning.classList.remove("hidden");
        machineSelect.innerHTML = "";
        return;
    }

    openCreateListingBtn.disabled = false;
    noMachinesWarning.classList.add("hidden");

    //dropdown
    machineSelect.innerHTML = machines
        .map(
            (m) =>
                `<option value="${m.id}">
                    ${m.hostname || "Machine #" + m.id}
                 </option>`
        )
        .join("");
}


//Load bookings
async function loadBookings() {
    let bookings = [];

    try {
        bookings = await apiGetBookings();
    } catch (err) {
        pendingBody.innerHTML = errorRow(err.message);
        pastBody.innerHTML = errorRow(err.message);
        return;
    }

    const pending = bookings.filter((b) =>
        ["requested", "confirmed", "active"].includes(b.status)
    );

    const past = bookings.filter((b) =>
        ["cancelled", "completed"].includes(b.status)
    );

    statTotal.textContent = bookings.length;
    statPending.textContent = pending.length;
    statActive.textContent = bookings.filter((b) => b.status === "active").length;
    statPast.textContent = past.length;

    pendingBody.innerHTML = pending.length
        ? pending.map(rowHTML).join("")
        : emptyRow(5, "No pending bookings.");

    pastBody.innerHTML = past.length
        ? past.map(rowHTML).join("")
        : emptyRow(5, "No past bookings.");
}


//Helper fxns
function rowHTML(b) {
    return `
        <tr class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
            <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">#${b.id}</td>
            <td class="px-6 py-4 text-gray-900 dark:text-white">${b.listing_title || "Listing " + b.listing_id}</td>
            <td class="px-6 py-4 text-gray-900 dark:text-white">${b.buyer_email || "Unknown"}</td>
            <td class="px-6 py-4 text-gray-900 dark:text-white">${scheduleHTML(b)}</td>
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
        requested: "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300",
        confirmed: "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300",
        active: "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300",
        completed: "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300",
        cancelled: "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300",
    };
    return `<span class="px-2.5 py-0.5 text-xs rounded ${colors[status]}">${status}</span>`;
}

function emptyRow(colspan, text) {
    return `<tr><td colspan="${colspan}" class="px-6 py-6 text-center text-gray-500 dark:text-gray-400">${text}</td></tr>`;
}

function errorRow(msg) {
    return `<tr><td colspan="5" class="px-6 py-6 text-center text-red-600 dark:text-red-400">${msg}</td></tr>`;
}

function formatDate(str) {
    return str ? new Date(str).toLocaleString() : "-";
}