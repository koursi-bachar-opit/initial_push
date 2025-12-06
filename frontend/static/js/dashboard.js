import {
    apiGetBookings,
    apiCreateListing,
    apiGetMachines,
    apiCreateMachine,
    apiGetProviders,
    apiVerifyProvider,
    apiGetProviderVerifications,
    apiGetProviderStats,
    apiGetMachineBenchmarks,
    apiAddMachineBenchmark,
    apiGetBookingCredentials,
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

//admin elements
const providersContainer = document.getElementById("providers-container");

//internal machine cache
let machines = [];
let allProviders = [];

document.addEventListener("DOMContentLoaded", async () => {
    // Load role-specific content
    if (document.body.contains(providersContainer)) {
        // This is an admin dashboard
        await loadAdminDashboard();
    } else {
        // This is a buyer/provider dashboard
        await loadUserDashboard();
    }
});

async function loadUserDashboard() {
    //Load machines first (for providers)
    if (machineSelect) {
        await loadMachines();
    }

    setupBenchmarkForm();

    //Load bookings
    await loadBookings();

    //Listing creation handler
    if (createListingForm) {
        createListingForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const fd = new FormData(createListingForm);
            const payload = {
                machine_id: fd.get("machine_id"),
                title: fd.get("title"),
                price: Number(fd.get("price")),
            };

            console.log("Creating listing with payload:", payload); //debug logging

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

    // Machine creation handler
    if (createMachineForm) {
        createMachineForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const fd = new FormData(createMachineForm);
            
            // Basic validation
            const gpuCount = parseInt(fd.get("gpu_count"));
            const vramGb = parseInt(fd.get("vram_gb"));
            const cpuCores = parseInt(fd.get("cpu_cores"));
            const ramGb = parseInt(fd.get("ram_gb"));
            const storageGb = parseInt(fd.get("storage_gb"));
            const networkMbps = parseInt(fd.get("network_mbps"));
            
            if (gpuCount < 0) {
                alert("GPU count cannot be negative");
                return;
            }
            if (vramGb < 0) {
                alert("VRAM cannot be negative");
                return;
            }
            if (cpuCores < 1) {
                alert("CPU cores must be at least 1");
                return;
            }
            if (ramGb < 1) {
                alert("RAM must be at least 1 GB");
                return;
            }
            if (storageGb < 1) {
                alert("Storage must be at least 1 GB");
                return;
            }
            if (networkMbps < 1) {
                alert("Network bandwidth must be at least 1 Mbps");
                return;
            }

            const payload = {
                hostname: fd.get("hostname"),
                location_region: fd.get("location_region"),
                gpu_model: fd.get("gpu_model"),
                gpu_count: gpuCount,
                vram_gb: vramGb,
                cpu_model: fd.get("cpu_model"),
                cpu_cores: cpuCores,
                ram_gb: ramGb,
                storage_gb: storageGb,
                network_mbps: networkMbps,
                notes: fd.get("notes") || null,
            };

            try {
                await apiCreateMachine(payload);
                alert("Machine added successfully!");

                //Close modal
                document
                    .querySelector('[data-modal-hide="createMachineModal"]')
                    ?.click();

                createMachineForm.reset();

                //Refresh machines list and repopulate dropdown
                await loadMachines();
            } catch (err) {
                alert("Error creating machine: " + err.message);
            }
        });
    }
}

async function loadAdminDashboard() {
    await loadProviders();
    await loadStats();
}

//Load machines and update UI state
async function loadMachines() {
    if (!machineSelect) return; // buyer dashboard

    try {
        machines = await apiGetMachines();
    } catch (err) {
        console.error("Failed to load machines:", err);
        machines = [];
    }

    // Machines UI state
    if (machines.length === 0) {
        openCreateListingBtn.disabled = true;
        noMachinesWarning.classList.remove("hidden");
        machineSelect.innerHTML = "";
        
        // Also update benchmarks dropdown
        const benchmarkMachineSelect = document.getElementById("benchmarkMachineSelect");
        if (benchmarkMachineSelect) {
            benchmarkMachineSelect.innerHTML = '<option value="">No machines available</option>';
        }
        return;
    }

    openCreateListingBtn.disabled = false;
    noMachinesWarning.classList.add("hidden");

    // Update listing dropdown
    machineSelect.innerHTML = machines
        .map(
            (m) =>
                `<option value="${m.id}">
                    ${m.hostname || "Machine #" + m.id}
                 </option>`
        )
        .join("");

    // Update benchmarks dropdown
    const benchmarkMachineSelect = document.getElementById("benchmarkMachineSelect");
    const openAddBenchmarkBtn = document.getElementById("openAddBenchmarkModal");
    
    if (benchmarkMachineSelect) {
        benchmarkMachineSelect.innerHTML = '<option value="">Choose a machine...</option>' +
            machines.map(m => 
                `<option value="${m.id}" data-hostname="${m.hostname || 'Unnamed'}">
                    ${m.hostname || "Machine #" + m.id}
                </option>`
            ).join("");

        // When machine is selected for benchmarks
        benchmarkMachineSelect.addEventListener("change", async function() {
            const machineId = this.value;
            const selectedOption = this.options[this.selectedIndex];
            const machineName = selectedOption.getAttribute("data-hostname");
            
            if (machineId) {
                // Enable add benchmark button
                openAddBenchmarkBtn.disabled = false;
                
                // Set hidden field in modal
                document.getElementById("benchmarkMachineId").value = machineId;
                
                // Show benchmarks list
                document.getElementById("benchmarksList").classList.remove("hidden");
                document.getElementById("selectedMachineName").textContent = machineName;
                
                // Load benchmarks for this machine
                await loadMachineBenchmarks(machineId);
            } else {
                // Disable add benchmark button
                openAddBenchmarkBtn.disabled = true;
                document.getElementById("benchmarksList").classList.add("hidden");
            }
        });
    }
}

// Load benchmarks for a specific machine
async function loadMachineBenchmarks(machineId) {
    const benchmarksContainer = document.getElementById("benchmarksContainer");
    if (!benchmarksContainer) return;

    try {
        const benchmarks = await apiGetMachineBenchmarks(machineId);
        renderBenchmarks(benchmarks);
    } catch (err) {
        benchmarksContainer.innerHTML = `
            <div class="text-red-600 dark:text-red-400">
                Failed to load benchmarks: ${err.message}
            </div>
        `;
    }
}

// Render benchmarks list
function renderBenchmarks(benchmarks) {
    const container = document.getElementById("benchmarksContainer");
    if (!container) return;

    if (benchmarks.length === 0) {
        container.innerHTML = `
            <div class="text-gray-500 dark:text-gray-400 italic">
                No benchmarks yet. Add one to showcase this machine's performance.
            </div>
        `;
        return;
    }

    container.innerHTML = benchmarks.map(benchmark => `
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-medium text-gray-900 dark:text-white">${benchmark.name}</h4>
                    <p class="text-lg font-semibold text-purple-600 dark:text-purple-400 mt-1">${benchmark.score}</p>
                    ${benchmark.methodology_uri ? `
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            <a href="${benchmark.methodology_uri}" target="_blank" 
                               class="text-blue-600 dark:text-blue-400 hover:underline">
                                Methodology
                            </a>
                        </p>
                    ` : ''}
                    ${benchmark.artifact_uri ? `
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            <a href="${benchmark.artifact_uri}" target="_blank"
                               class="text-blue-600 dark:text-blue-400 hover:underline">
                                Artifact
                            </a>
                        </p>
                    ` : ''}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                    ${new Date(benchmark.created_at).toLocaleDateString()}
                </div>
            </div>
        </div>
    `).join("");
}

// Handle benchmark form submission
function setupBenchmarkForm() {
    const form = document.getElementById("add-benchmark-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const fd = new FormData(form);
        const machineId = fd.get("machine_id");
        
        const payload = {
            name: fd.get("name"),
            score: fd.get("score"),
            methodology_uri: fd.get("methodology_uri") || undefined,
            artifact_uri: fd.get("artifact_uri") || undefined,
        };

        try {
            await apiAddMachineBenchmark(machineId, payload);
            alert("Benchmark added successfully!");

            // Close modal
            document.querySelector('[data-modal-hide="addBenchmarkModal"]')?.click();
            
            // Reset form
            form.reset();
            
            // Reload benchmarks for the selected machine
            const selectedMachineId = document.getElementById("benchmarkMachineSelect").value;
            if (selectedMachineId) {
                await loadMachineBenchmarks(selectedMachineId);
            }
        } catch (err) {
            alert("Error adding benchmark: " + err.message);
        }
    });
}

//Load bookings
async function loadBookings() {
    let bookings = [];

    try {
        bookings = await apiGetBookings();
    } catch (err) {
        if (pendingBody) pendingBody.innerHTML = errorRow(err.message);
        if (pastBody) pastBody.innerHTML = errorRow(err.message);
        return;
    }

    const pending = bookings.filter((b) =>
        ["requested", "confirmed", "active"].includes(b.status)
    );

    const past = bookings.filter((b) =>
        ["cancelled", "completed"].includes(b.status)
    );

    if (statTotal) statTotal.textContent = bookings.length;
    if (statPending) statPending.textContent = pending.length;
    if (statActive) statActive.textContent = bookings.filter((b) => b.status === "active").length;
    if (statPast) statPast.textContent = past.length;

    if (pendingBody) {
        pendingBody.innerHTML = pending.length
            ? pending.map(rowHTML).join("")
            : emptyRow(5, "No pending bookings.");
        
        // Add event listeners for credentials buttons
        setTimeout(() => {
            document.querySelectorAll('.view-credentials-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const bookingId = btn.dataset.bookingId;
                    showCredentialsModal(bookingId);
                });
            });
        }, 100);
    }

    if (pastBody) {
        pastBody.innerHTML = past.length
            ? past.map(rowHTML).join("")
            : emptyRow(5, "No past bookings.");
    }
}

// Credentials functionality
async function loadCredentials(bookingId) {
    return await apiGetBookingCredentials(bookingId);
}

// show bookings credentials
function showCredentialsModal(bookingId) {
    console.log("Fetching credentials for booking:", bookingId); // Debug log
    
    loadCredentials(bookingId)
        .then(data => {
            console.log("Credentials response:", data); // Debug log
            
            const credentials = data.credentials;
            
            // Debug: Check what we received
            console.log("Credentials data:", credentials);
            console.log("VPN URI:", credentials?.vpn_config_uri);
            console.log("SSH Fingerprint:", credentials?.ssh_public_key_fingerprint);
            
            // Set VPN download link
            const vpnLink = document.getElementById('vpnDownloadLink');
            if (credentials && credentials.vpn_config_uri) {
                vpnLink.href = credentials.vpn_config_uri;
                vpnLink.classList.remove('hidden');
                console.log("VPN link set to:", credentials.vpn_config_uri);
            } else {
                vpnLink.classList.add('hidden');
                console.log("No VPN URI available");
            }
            
            // Set SSH fingerprint
            const sshFingerprint = document.getElementById('sshFingerprint');
            if (credentials && credentials.ssh_public_key_fingerprint) {
                sshFingerprint.textContent = credentials.ssh_public_key_fingerprint;
                console.log("SSH fingerprint set:", credentials.ssh_public_key_fingerprint);
            } else {
                sshFingerprint.textContent = 'Not available';
                console.log("No SSH fingerprint available");
            }
            
            // Copy button functionality
            const copyBtn = document.getElementById('copySshFingerprintBtn');
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(credentials?.ssh_public_key_fingerprint || '')
                    .then(() => {
                        const originalText = copyBtn.textContent;
                        copyBtn.textContent = 'Copied!';
                        setTimeout(() => {
                            copyBtn.textContent = originalText;
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Failed to copy:', err);
                    });
            };
            
            // Show the modal (let Flowbite handle it if using Option A)
            // If using Option B, keep your custom modal show logic
        })
        .catch(err => {
            console.error("Error loading credentials:", err); // Debug log
            alert('Failed to load credentials: ' + err.message);
        });
}

// Admin functions
async function loadProviders() {
    try {
        allProviders = await apiGetProviders();
        renderProviders();
    } catch (err) {
        console.error("Failed to load providers:", err);
        if (providersContainer) {
            providersContainer.innerHTML = `
                <div class="text-center py-8 text-red-600 dark:text-red-400">
                    Failed to load providers: ${err.message}
                </div>
            `;
        }
    }
}

async function loadStats() {
    try {
        const stats = await apiGetProviderStats();
        updateStats(stats);
    } catch (err) {
        console.error("Failed to load stats:", err);
    }
}

function renderProviders() {
    if (!providersContainer) return;
    
    const template = document.getElementById("provider-card-template");
    
    if (allProviders.length === 0) {
        providersContainer.innerHTML = `
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                No providers found.
            </div>
        `;
        return;
    }

    providersContainer.innerHTML = '';
    
    allProviders.forEach(provider => {
        const clone = template.content.cloneNode(true);
        const card = clone.firstElementChild;
        
        // Fill provider data
        card.querySelector('.provider-email').textContent = provider.user_email || 'No email';
        card.querySelector('.provider-id').textContent = `ID: ${provider.id}`;
        card.querySelector('.provider-created').textContent = `Created: ${new Date(provider.created_at).toLocaleDateString()}`;
        
        const statusBadge = card.querySelector('.provider-status-badge');
        statusBadge.textContent = provider.verification_status;
        
        // Set status badge color
        switch(provider.verification_status) {
            case 'verified':
                statusBadge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900', 'dark:text-green-300');
                break;
            case 'rejected':
                statusBadge.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-900', 'dark:text-red-300');
                break;
            default:
                statusBadge.classList.add('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-300');
        }
        
        // Set up verify/reject buttons
        const verifyBtn = card.querySelector('.verify-btn');
        const rejectBtn = card.querySelector('.reject-btn');
        
        verifyBtn.addEventListener('click', () => verifyProvider(provider.id, 'verified'));
        rejectBtn.addEventListener('click', () => verifyProvider(provider.id, 'rejected'));
        
        // Hide buttons if already verified/rejected
        if (provider.verification_status === 'verified' || provider.verification_status === 'rejected') {
            verifyBtn.style.display = 'none';
            rejectBtn.style.display = 'none';
        }
        
        // Load verification history
        loadVerificationHistory(provider.id, card.querySelector('.verification-history'));
        
        providersContainer.appendChild(card);
    });
}

async function loadVerificationHistory(providerId, container) {
    try {
        const verifications = await apiGetProviderVerifications(providerId);
        if (verifications.length === 0) {
            container.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No verification history</p>';
            return;
        }
        
        container.innerHTML = verifications.map(verification => `
            <div class="text-sm">
                <span class="font-medium">${verification.status}</span> 
                <span class="text-gray-500 dark:text-gray-400">on ${new Date(verification.created_at).toLocaleDateString()}</span>
                ${verification.notes ? `<p class="text-gray-600 dark:text-gray-400 mt-1">${verification.notes}</p>` : ''}
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = '<p class="text-sm text-red-600 dark:text-red-400">Failed to load history</p>';
    }
}

async function verifyProvider(providerId, status) {
    if (!confirm(`Are you sure you want to ${status} this provider?`)) {
        return;
    }
    
    const notes = prompt(`Enter notes for ${status} action (optional):`) || '';
    
    try {
        await apiVerifyProvider(providerId, status, notes);
        alert(`Provider ${status} successfully!`);
        await loadProviders(); // Reload the list
        await loadStats(); // Reload stats
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

function updateStats(stats) {
    const totalEl = document.getElementById('stat-total-providers');
    const pendingEl = document.getElementById('stat-pending-verification');
    const verifiedEl = document.getElementById('stat-verified-providers');
    const rejectedEl = document.getElementById('stat-rejected-providers');
    
    if (totalEl) totalEl.textContent = stats.total_providers;
    if (pendingEl) pendingEl.textContent = stats.pending_verification;
    if (verifiedEl) verifiedEl.textContent = stats.verified_providers;
    if (rejectedEl) rejectedEl.textContent = stats.rejected_providers;
}

//Helper fxns
//Helper fxns
function rowHTML(b) {
    const credentialsButton = b.status === 'active' ? `
        <button class="view-credentials-btn inline-flex items-center gap-1 text-white bg-purple-600 hover:bg-purple-700 font-medium rounded-lg text-xs px-3 py-1.5 transition"
                data-booking-id="${b.id}"
                data-modal-target="credentialsModal"
                data-modal-toggle="credentialsModal"
                title="View access credentials for this booking">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
            </svg>
            Credentials
        </button>
    ` : '';
    
    return `
        <tr class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
            <td class="px-6 py-4">
                <div class="font-medium text-gray-900 dark:text-white">#${b.id.substring(0, 8)}...</div>
                <div class="mt-1">${credentialsButton}</div>
            </td>
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