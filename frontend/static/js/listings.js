import { apiGetListings, apiRequestBooking, apiSearchListings, apiSearchListingsWithFilters, apiGetMachineBenchmarks } from "./api.js";

// DOM Elements
const listingsGrid = document.getElementById("listingsGrid");
const myListingsGrid = document.getElementById("myListingsGrid");
const role = localStorage.getItem("user_role");
const userId = localStorage.getItem("user_id");

// Filter Elements
const filterSearch = document.getElementById("filterSearch");
const minPrice = document.getElementById("minPrice");
const maxPrice = document.getElementById("maxPrice");
const minCpuCores = document.getElementById("minCpuCores");
const minRamGb = document.getElementById("minRamGb");
const gpuModel = document.getElementById("gpuModel");
const minGpuCount = document.getElementById("minGpuCount");
const minVramGb = document.getElementById("minVramGb");
const minStorageGb = document.getElementById("minStorageGb");
const minNetworkMbps = document.getElementById("minNetworkMbps");
const locationRegion = document.getElementById("locationRegion");
const cpuModel = document.getElementById("cpuModel");
const sortBy = document.getElementById("sortBy");
const sortOrder = document.getElementById("sortOrder");
const applyFilters = document.getElementById("applyFilters");
const clearFilters = document.getElementById("clearFilters");
const clearActiveFilters = document.getElementById("clearActiveFilters");
const filterResultsInfo = document.getElementById("filterResultsInfo");
const resultsCount = document.getElementById("resultsCount");

// Modal elements
const modalEl = document.getElementById("listingDetailsModal");
const modalTitle = document.getElementById("modalTitle");
const modalDescription = document.getElementById("modalDescription");
const modalPrice = document.getElementById("modalPrice");
const modalMeta = document.getElementById("modalMeta");
const modalBookButton = document.getElementById("modalBookButton");

let allListings = [];
let filteredListings = [];
let selectedListing = null;
let isFiltered = false;
let modal;


document.addEventListener("DOMContentLoaded", async () => {
    modal = new Modal(modalEl);

    // Set up event listeners
    applyFilters.addEventListener("click", performFilteredSearch);
    clearFilters.addEventListener("click", resetAllFilters);
    clearActiveFilters.addEventListener("click", resetAllFilters);
    
    // Enter key in search box
    filterSearch.addEventListener("keypress", (e) => {
        if (e.key === "Enter") performFilteredSearch();
    });

    // Load initial listings with metrics
    try {
        const response = await apiGetListings();
        // Assuming apiGetListings now returns {items: [...]} structure
        allListings = response.items || response; // Support both structures
        filteredListings = [...allListings];
        renderListings();
    } catch (err) {
        showError("Failed to load listings: " + err.message);
    }
});

// Add this function to get benchmarks for a machine
async function getMachineBenchmarks(machineId) {
    try {
        const benchmarks = await apiGetMachineBenchmarks(machineId);
        return benchmarks;
    } catch (err) {
        console.error("Failed to fetch benchmarks:", err);
        return [];
    }
}


async function performFilteredSearch() {
    //Build filters object
    const filters = {
        q: filterSearch.value.trim() || undefined,
        min_price: minPrice.value ? parseFloat(minPrice.value) : undefined,
        max_price: maxPrice.value ? parseFloat(maxPrice.value) : undefined,
        min_cpu_cores: minCpuCores.value ? parseInt(minCpuCores.value) : undefined,
        min_ram_gb: minRamGb.value ? parseInt(minRamGb.value) : undefined,
        gpu_model: gpuModel.value.trim() || undefined,
        min_gpu_count: minGpuCount.value ? parseInt(minGpuCount.value) : undefined,
        min_vram_gb: minVramGb.value ? parseInt(minVramGb.value) : undefined,
        min_storage_gb: minStorageGb.value ? parseInt(minStorageGb.value) : undefined,
        min_network_mbps: minNetworkMbps.value ? parseInt(minNetworkMbps.value) : undefined,
        location_region: locationRegion.value.trim() || undefined,
        cpu_model: cpuModel.value.trim() || undefined,
        sort_by: sortBy.value,
        sort_order: sortOrder.value,
        page: 1,
        per_page: 20
    };

    try {
        const response = await apiSearchListingsWithFilters(filters);
        
        //Extract listings from response - now includes metrics
        filteredListings = response.items; //Keep the full structure with metrics
        isFiltered = true;
        
        //Update UI
        updateResultsInfo(response.total);
        renderListings();
        
    } catch (err) {
        console.error("Filter error:", err);
        showError("Failed to apply filters: " + err.message);
    }
}

function resetAllFilters() {
    // Clear all filter inputs
    filterSearch.value = "";
    minPrice.value = "";
    maxPrice.value = "";
    minCpuCores.value = "";
    minRamGb.value = "";
    gpuModel.value = "";
    minGpuCount.value = "";
    minVramGb.value = "";
    minStorageGb.value = "";
    minNetworkMbps.value = "";
    locationRegion.value = "";
    cpuModel.value = "";
    sortBy.value = "created_at";
    sortOrder.value = "desc";
    
    // Reset to all listings
    filteredListings = [...allListings];
    isFiltered = false;
    filterResultsInfo.classList.add("hidden");
    renderListings();
}

function updateResultsInfo(total) {
    if (total === 0) {
        filterResultsInfo.classList.add("hidden");
    } else {
        resultsCount.textContent = total;
        filterResultsInfo.classList.remove("hidden");
    }
}

function renderListings() {
    // Update all listings tab
    if (filteredListings.length === 0) {
        listingsGrid.innerHTML = "";
        document.getElementById("noResults").classList.remove("hidden");
    } else {
        document.getElementById("noResults").classList.add("hidden");
        listingsGrid.innerHTML = filteredListings
            .map((l) => listingCardHTML(l))
            .join("");
    }

    // Update my listings tab if user is logged in
    if (myListingsGrid && userId) {
        const mine = allListings.filter((l) => {
            return l.provider_id === userId || l.machine?.provider_id === userId;
        });
        
        if (mine.length === 0) {
            document.getElementById("noMyResults").classList.remove("hidden");
            myListingsGrid.innerHTML = "";
        } else {
            document.getElementById("noMyResults").classList.add("hidden");
            myListingsGrid.innerHTML = mine.map((l) => listingCardHTML(l)).join("");
        }
    }

    // Reattach event listeners to the new buttons
    document.querySelectorAll(".btn-view-details").forEach((btn) => {
        btn.addEventListener("click", () => openDetailsModal(btn.dataset.id));
    });
}

// Update the listingCardHTML to show benchmarks badge
function listingCardHTML(item) {
    const listing = item.listing || item;
    const metrics = item.latest_metrics;
    
    const description = listing.machine?.notes || "No description provided.";
    const cpuUtil = metrics?.cpu_util;
    const gpuUtil = metrics?.gpu_util;
    
    return `
        <div class="bg-white dark:bg-gray-800 shadow border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition relative">
            <div class="p-5">
                <h3 class="text-lg font-bold mb-1 text-gray-900 dark:text-white">${listing.title}</h3>
                <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-2 mb-3">
                    ${description}
                </p>
                <p class="text-blue-600 dark:text-blue-400 font-semibold mb-2">$${listing.price}/hr</p>
                
                <!-- Machine specs with metrics -->
                ${listing.machine ? `
                <div class="text-xs text-gray-500 dark:text-gray-400 mb-3 space-y-1">
                    ${listing.machine.cpu_cores ? `<div><span class="font-medium">CPU:</span> ${listing.machine.cpu_cores} cores ${cpuUtil !== undefined ? `<span class="text-green-600 dark:text-green-400">(${cpuUtil}% util)</span>` : ''}</div>` : ''}
                    ${listing.machine.ram_gb ? `<div><span class="font-medium">RAM:</span> ${listing.machine.ram_gb} GB</div>` : ''}
                    ${listing.machine.gpu_model ? `<div><span class="font-medium">GPU:</span> ${listing.machine.gpu_model} x${listing.machine.gpu_count || 1} ${gpuUtil !== undefined ? `<span class="text-green-600 dark:text-green-400">(${gpuUtil}% util)</span>` : ''}</div>` : ''}
                    ${listing.machine.vram_gb ? `<div><span class="font-medium">VRAM:</span> ${listing.machine.vram_gb} GB per GPU</div>` : ''}
                    ${listing.machine.storage_gb ? `<div><span class="font-medium">Storage:</span> ${listing.machine.storage_gb} GB</div>` : ''}
                    ${listing.machine.network_mbps ? `<div><span class="font-medium">Network:</span> ${listing.machine.network_mbps} Mbps</div>` : ''}
                    ${listing.machine.location_region ? `<div><span class="font-medium">Region:</span> ${listing.machine.location_region}</div>` : ''}
                    ${metrics ? `<div class="pt-2 mt-2 border-t border-gray-200 dark:border-gray-700">
                        <div class="flex justify-between">
                            <span class="font-medium">Live Metrics:</span>
                            <span class="text-xs text-gray-400">${new Date(metrics.recorded_at).toLocaleTimeString()}</span>
                        </div>
                        <div>CPU: <span class="${cpuUtil > 80 ? 'text-red-600' : cpuUtil > 50 ? 'text-yellow-600' : 'text-green-600'}">${cpuUtil}%</span></div>
                        <div>GPU: <span class="${gpuUtil > 80 ? 'text-red-600' : gpuUtil > 50 ? 'text-yellow-600' : 'text-green-600'}">${gpuUtil}%</span></div>
                        ${metrics.mem_used_gb ? `<div>Memory: ${metrics.mem_used_gb} GB used</div>` : ''}
                    </div>` : ''}
                </div>
                ` : ''}

                <button 
                    data-id="${listing.id}"
                    class="btn-view-details w-full mt-2 px-4 py-2 bg-gray-900 text-white rounded hover:bg-black dark:hover:bg-gray-700 transition text-sm flex items-center justify-center gap-2"
                    data-modal-target="listingDetailsModal"
                    data-modal-toggle="listingDetailsModal">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                    </svg>
                    View Details
                    <span class="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300 text-xs font-medium px-2 py-0.5 rounded">
                        Benchmarks
                    </span>
                </button>
            </div>
        </div>
    `;
}

async function openDetailsModal(id) {
    // Find the item in filteredListings
    const item = filteredListings.find((item) => {
        const listing = item.listing || item;
        return String(listing.id) === String(id);
    });
    
    if (!item) return;
    
    // Extract the listing from the item
    selectedListing = item.listing || item;
    
    modalTitle.textContent = selectedListing.title;
    
    // Use machine description/notes if available
    const description = selectedListing.machine?.notes || 
                       selectedListing.machine?.description || 
                       "No description provided.";
    modalDescription.textContent = description;
    
    modalPrice.textContent = `$${selectedListing.price}/hr`;
    
    // Build machine details
    let metaHTML = `
        <div class="space-y-3">
            <div><strong>Listing ID:</strong> ${selectedListing.id}</div>
    `;
    
    if (selectedListing.machine) {
        const machine = selectedListing.machine;
        metaHTML += `
            <div><strong>Machine:</strong> ${machine.hostname}</div>
            ${machine.location_region ? `<div><strong>Region:</strong> ${machine.location_region}</div>` : ''}
            <div><strong>Specs:</strong> ${machine.cpu_cores || '?'} CPU cores, ${machine.ram_gb || '?'} GB RAM</div>
        `;
        
        // Fetch benchmarks for this machine
        if (machine.id) {
            try {
                const benchmarks = await getMachineBenchmarks(machine.id);
                if (benchmarks.length > 0) {
                    metaHTML += `
                        <div class="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
                            <h4 class="font-semibold text-gray-900 dark:text-white mb-2">Benchmarks</h4>
                            <div class="space-y-2">
                    `;
                    
                    benchmarks.forEach(benchmark => {
                        metaHTML += `
                            <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                                <div class="flex justify-between items-start">
                                    <div>
                                        <div class="font-medium">${benchmark.name}</div>
                                        <div class="text-lg font-semibold text-purple-600 dark:text-purple-400">${benchmark.score}</div>
                                        ${benchmark.methodology_uri ? `
                                            <div class="text-sm mt-1">
                                                <a href="${benchmark.methodology_uri}" target="_blank" 
                                                   class="text-blue-600 dark:text-blue-400 hover:underline">
                                                    Methodology
                                                </a>
                                            </div>
                                        ` : ''}
                                        ${benchmark.artifact_uri ? `
                                            <div class="text-sm">
                                                <a href="${benchmark.artifact_uri}" target="_blank"
                                                   class="text-blue-600 dark:text-blue-400 hover:underline">
                                                    Artifact
                                                </a>
                                            </div>
                                        ` : ''}
                                    </div>
                                    <div class="text-xs text-gray-500 dark:text-gray-400">
                                        ${new Date(benchmark.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    
                    metaHTML += `
                            </div>
                        </div>
                    `;
                }
            } catch (err) {
                console.error("Failed to load benchmarks:", err);
            }
        }
    }
    
    // Add metrics to modal if available
    if (item.latest_metrics) {
        const metrics = item.latest_metrics;
        metaHTML += `
            <div class="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
                <h4 class="font-semibold text-gray-900 dark:text-white mb-2">Live Metrics</h4>
                <div class="space-y-2">
                    <div><strong>CPU Utilization:</strong> ${metrics.cpu_util}%</div>
                    <div><strong>GPU Utilization:</strong> ${metrics.gpu_util}%</div>
                    ${metrics.mem_used_gb ? `<div><strong>Memory Used:</strong> ${metrics.mem_used_gb} GB</div>` : ''}
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                        Updated: ${new Date(metrics.recorded_at).toLocaleTimeString()}
                    </div>
                </div>
            </div>
        `;
    }
    
    metaHTML += `</div>`; // Close the space-y-3 div
    modalMeta.innerHTML = metaHTML;

    // Check if modalBookButton exists and user is buyer
    if (modalBookButton && role === "buyer") {
        modalBookButton.onclick = handleBookingRequest;
        modalBookButton.style.display = "block";
    } else if (modalBookButton) {
        modalBookButton.style.display = "none";
    }

    // Show the modal using the already initialized modal
    modal.show();
}

// Booking request selection (booking window one hour default for test)
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

function showError(message) {
    // Create error notification
    const errorDiv = document.createElement("div");
    errorDiv.className = "fixed top-4 right-4 z-50 p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400 shadow-lg";
    errorDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
            </svg>
            <span class="font-medium">Error!</span> ${message}
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}