import { apiGetListings, apiRequestBooking, apiSearchListings } from "./api.js";

const listingsGrid = document.getElementById("listingsGrid");
const myListingsGrid = document.getElementById("myListingsGrid");
const role = localStorage.getItem("user_role");
const userId = localStorage.getItem("user_id");

// Search elements
const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const clearSearch = document.getElementById("clearSearch");
const searchResultsInfo = document.getElementById("searchResultsInfo");
const resultsCount = document.getElementById("resultsCount");
const noResults = document.getElementById("noResults");
const noMyResults = document.getElementById("noMyResults");

let allListings = [];
let filteredListings = [];
let selectedListing = null;

//modal DOM references (Flowbite)
const modalEl = document.getElementById("listingDetailsModal");
const modalTitle = document.getElementById("modalTitle");
const modalDescription = document.getElementById("modalDescription");
const modalPrice = document.getElementById("modalPrice");
const modalMeta = document.getElementById("modalMeta");
const modalBookButton = document.getElementById("modalBookButton");

//Flowbite modal instance is constructed after Flowbite loads
let modal;

document.addEventListener("DOMContentLoaded", async () => {
    //create modal instance safely
    modal = new Modal(modalEl);

    // Set up search event listeners
    searchButton.addEventListener("click", performSearch);
    clearSearch.addEventListener("click", clearSearchResults);
    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            performSearch();
        }
    });

    try {
        allListings = await apiGetListings();
        filteredListings = [...allListings];
        renderListings();
    } catch (err) {
        listingsGrid.innerHTML = `<p class="text-red-600">${err.message}</p>`;
        return;
    }
});

// Perform search
async function performSearch() {
    const searchTerm = searchInput.value.trim();
    
    if (!searchTerm) {
        clearSearchResults();
        return;
    }

    try {
        const searchResults = await apiSearchListings(searchTerm);
        
        // Extract listings from the search results structure
        filteredListings = searchResults.map(result => result.listing);
        
        // Update UI
        updateSearchUI(searchTerm, filteredListings.length);
        renderListings();
        
    } catch (err) {
        console.error("Search error:", err);
        showError("Search failed. Please try again.");
    }
}

// Clear search results
function clearSearchResults() {
    searchInput.value = "";
    filteredListings = [...allListings];
    searchResultsInfo.classList.add("hidden");
    noResults.classList.add("hidden");
    renderListings();
}

// Update search UI
function updateSearchUI(searchTerm, count) {
    resultsCount.textContent = count;
    searchResultsInfo.classList.remove("hidden");
    
    if (count === 0) {
        noResults.classList.remove("hidden");
    } else {
        noResults.classList.add("hidden");
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement("div");
    errorDiv.className = "p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400";
    errorDiv.innerHTML = `<span class="font-medium">Error!</span> ${message}`;
    
    // Insert after search box
    const searchBox = document.querySelector(".mb-8");
    searchBox.parentNode.insertBefore(errorDiv, searchBox.nextSibling);
    
    // Remove after 5 seconds
    setTimeout(() => errorDiv.remove(), 5000);
}

//render listings
function renderListings() {
    // Update all listings tab
    if (filteredListings.length === 0) {
        listingsGrid.innerHTML = "";
    } else {
        listingsGrid.innerHTML = filteredListings
            .map((l) => listingCardHTML(l))
            .join("");
    }

    // Update my listings tab if user is logged in
    if (myListingsGrid && userId) {
        const mine = allListings.filter((l) => {
            // Check if listing belongs to current user
            // This assumes provider_id is accessible somehow
            return l.provider_id === userId || l.machine?.provider_id === userId;
        });
        
        if (mine.length === 0) {
            noMyResults.classList.remove("hidden");
            myListingsGrid.innerHTML = "";
        } else {
            noMyResults.classList.add("hidden");
            myListingsGrid.innerHTML = mine.map((l) => listingCardHTML(l)).join("");
        }
    }

    // Reattach event listeners to the new buttons
    document.querySelectorAll(".btn-view-details").forEach((btn) => {
        btn.addEventListener("click", () => openDetailsModal(btn.dataset.id));
    });
}

//Card UI to format listing boxes
function listingCardHTML(l) {
    // Get description from machine if available
    const description = l.machine?.notes || l.machine?.description || "No description provided.";
    
    return `
        <div class="bg-white dark:bg-gray-800 shadow border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition">
            <div class="p-5">
                <h3 class="text-lg font-bold mb-1 text-gray-900 dark:text-white">${l.title}</h3>
                <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-2 mb-3">
                    ${description}
                </p>
                <p class="text-blue-600 dark:text-blue-400 font-semibold mb-2">$${l.price}/hr</p>
                
                <!-- Machine specs if available -->
                ${l.machine ? `
                <div class="text-xs text-gray-500 dark:text-gray-400 mb-3 space-y-1">
                    ${l.machine.cpu_cores ? `<div><span class="font-medium">CPU:</span> ${l.machine.cpu_cores} cores</div>` : ''}
                    ${l.machine.ram_gb ? `<div><span class="font-medium">RAM:</span> ${l.machine.ram_gb} GB</div>` : ''}
                    ${l.machine.gpu_model ? `<div><span class="font-medium">GPU:</span> ${l.machine.gpu_model}</div>` : ''}
                    ${l.machine.location_region ? `<div><span class="font-medium">Region:</span> ${l.machine.location_region}</div>` : ''}
                </div>
                ` : ''}

                <button 
                    data-id="${l.id}"
                    class="btn-view-details w-full mt-2 px-4 py-2 bg-gray-900 text-white rounded hover:bg-black dark:hover:bg-gray-700 transition text-sm"
                    data-modal-target="listingDetailsModal"
                    data-modal-toggle="listingDetailsModal">
                    View Details
                </button>
            </div>
        </div>
    `;
}

//Open modal (check listing description)
function openDetailsModal(id) {
    selectedListing = filteredListings.find((l) => String(l.id) === String(id));
    if (!selectedListing) return;

    modalTitle.textContent = selectedListing.title;
    
    // Use machine description/notes if available
    const description = selectedListing.machine?.notes || 
                       selectedListing.machine?.description || 
                       "No description provided.";
    modalDescription.textContent = description;
    
    modalPrice.textContent = `$${selectedListing.price}/hr`;
    
    // Build machine details
    let metaHTML = `Listing ID: ${selectedListing.id}`;
    if (selectedListing.machine) {
        const machine = selectedListing.machine;
        metaHTML += `<br>Machine: ${machine.hostname}`;
        if (machine.location_region) {
            metaHTML += `<br>Region: ${machine.location_region}`;
        }
        if (machine.cpu_cores || machine.ram_gb) {
            metaHTML += `<br>Specs: ${machine.cpu_cores || '?'} CPU cores, ${machine.ram_gb || '?'} GB RAM`;
        }
    }
    modalMeta.innerHTML = metaHTML;

    if (modalBookButton) {
        modalBookButton.onclick = handleBookingRequest;
    }

    modal.show();
}

//Booking request selection (booking window one hour default for test)
async function handleBookingRequest() {
    if (!selectedListing) return;

    const now = new Date();
    const end = new Date(now.getTime() + 60 * 60 * 1000);

    try {
        await apiRequestBooking({
            listing_id: selectedListing.id,
            start_time: now.toISOString(),
            end_time: end.toISOString(),
        });

        alert("Booking request sent!");
        modal.hide();
    } catch (err) {
        alert("Error: " + err.message);
    }
}

// import { apiGetListings, apiRequestBooking } from "./api.js";

// const listingsGrid = document.getElementById("listingsGrid");
// const myListingsGrid = document.getElementById("myListingsGrid");
// const role = localStorage.getItem("user_role");
// const userId = localStorage.getItem("user_id");

// let listings = [];
// let selectedListing = null;

// //modal DOM references (Flowbite)
// const modalEl = document.getElementById("listingDetailsModal");
// const modalTitle = document.getElementById("modalTitle");
// const modalDescription = document.getElementById("modalDescription");
// const modalPrice = document.getElementById("modalPrice");
// const modalMeta = document.getElementById("modalMeta");
// const modalBookButton = document.getElementById("modalBookButton");

// //Flowbite modal instance is constructed after Flowbite loads
// let modal;

// document.addEventListener("DOMContentLoaded", async () => {
//     //create modal instance safely
//     modal = new Modal(modalEl);

//     try {
//         listings = await apiGetListings();
//     } catch (err) {
//         listingsGrid.innerHTML = `<p class="text-red-600">${err.message}</p>`;
//         return;
//     }

//     renderListings();
// });


// //render listings
// function renderListings() {
//     listingsGrid.innerHTML = listings
//         .map((l) => listingCardHTML(l))
//         .join("");

//     if (myListingsGrid) {
//         const mine = listings.filter((l) => String(l.provider_user_id) === userId);
//         myListingsGrid.innerHTML = mine.map((l) => listingCardHTML(l)).join("");
//     }

//     document.querySelectorAll(".btn-view-details").forEach((btn) => {
//         btn.addEventListener("click", () => openDetailsModal(btn.dataset.id));
//     });
// }


// //Card UI to format listing boxes
// function listingCardHTML(l) {
//     return `
//         <div class="bg-white dark:bg-gray-800 shadow border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition">
//             <div class="p-5">
//                 <h3 class="text-lg font-bold mb-1 text-gray-900 dark:text-white">${l.title}</h3>
//                 <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-2 mb-3">
//                     ${l.description || "No description provided."}
//                 </p>
//                 <p class="text-blue-600 dark:text-blue-400 font-semibold mb-2">$${l.price}/hr</p>

//                 <button 
//                     data-id="${l.id}"
//                     class="btn-view-details w-full mt-2 px-4 py-2 bg-gray-900 text-white rounded hover:bg-black dark:hover:bg-gray-700 transition text-sm"
//                     data-modal-target="listingDetailsModal"
//                     data-modal-toggle="listingDetailsModal">
//                     View Details
//                 </button>
//             </div>
//         </div>
//     `;
// }

// //Open modal (check listing description)
// function openDetailsModal(id) {
//     selectedListing = listings.find((l) => String(l.id) === String(id));
//     if (!selectedListing) return;

//     modalTitle.textContent = selectedListing.title;
//     modalDescription.textContent = selectedListing.description || "No description.";
//     modalPrice.textContent = `$${selectedListing.price}/hr`;
//     modalMeta.textContent = `Listing ID: ${selectedListing.id}`;

//     if (modalBookButton) {
//         modalBookButton.onclick = handleBookingRequest;
//     }

//     modal.show();
// }


// //Booking request selection (booking window one hour default for test)
// async function handleBookingRequest() {
//     if (!selectedListing) return;

//     const now = new Date();
//     const end = new Date(now.getTime() + 60 * 60 * 1000);

//     try {
//         await apiRequestBooking({
//             listing_id: selectedListing.id,
//             start_time: now.toISOString(),
//             end_time: end.toISOString(),
//         });

//         alert("Booking request sent!");
//         modal.hide();
//     } catch (err) {
//         alert("Error: " + err.message);
//     }
// }