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
    apiGetWipeVerification,
    apiGetAllAttestations,
    apiGetMachineAttestations,
    apiReviewAttestation,
    apiGetProviderBookingAttestation,
    apiGetAdminBookingAttestation,
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

    if (document.getElementById('wipeHistoryMachineSelect')) {
        setupWipeHistory();
    }

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
    await loadWipeAttestations();
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
        
        // In loadBookings() function, after table population:
        setTimeout(() => {
            // Credentials buttons (for active bookings)
            document.querySelectorAll('.view-credentials-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const bookingId = btn.dataset.bookingId;
                    showCredentialsModal(bookingId);
                });
            });

            // Wipe verification buttons (for buyers only)
            document.querySelectorAll('.view-wipe-verification-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const bookingId = btn.dataset.bookingId;
                    showWipeVerificationModal(bookingId);
                });
            });

            // Provider attestation buttons (for providers only)
            document.querySelectorAll('.view-provider-attestation-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const bookingId = btn.dataset.bookingId;
                    // Call the actual function to show provider attestation modal
                    showProviderAttestationModal(bookingId);
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

// Show credentials for a booking
function showCredentialsModal(bookingId) {
    console.log("Fetching credentials for booking:", bookingId);
    
    loadCredentials(bookingId)
        .then(data => {
            console.log("Credentials response:", data);
            
            const credentialsArray = data.credentials;
            
            // Check if we have credentials
            if (!credentialsArray || credentialsArray.length === 0) {
                console.log("No credentials found for this booking");
                alert("No access credentials available for this booking.");
                return;
            }
            
            // Get the first (or most recent) credential
            const credential = credentialsArray[0];
            
            console.log("Credential data:", credential);
            console.log("VPN URI:", credential.vpn_config_uri);
            console.log("SSH Fingerprint:", credential.ssh_public_key_fingerprint);
            
            // Set VPN download link - FIX for S3 scheme
            const vpnLink = document.getElementById('vpnDownloadLink');
            if (credential.vpn_config_uri) {
                // Convert s3:// to https:// for browser compatibility
                // Or show it as text if it's a mock URI
                if (credential.vpn_config_uri.startsWith('s3://')) {
                    // Option 1: Show as text (mock)
                    vpnLink.href = '#';
                    vpnLink.onclick = (e) => {
                        e.preventDefault();
                        alert('Mock VPN Configuration: ' + credential.vpn_config_uri + '\n\nIn a real system, this would download the VPN config file.');
                        return false;
                    };
                    vpnLink.textContent = 'Download VPN Configuration (Mock)';
                } else {
                    // Option 2: Use as-is for real URLs
                    vpnLink.href = credential.vpn_config_uri;
                    vpnLink.onclick = null;
                    vpnLink.textContent = 'Download VPN Configuration';
                }
                vpnLink.classList.remove('hidden');
                console.log("VPN link set to:", credential.vpn_config_uri);
            } else {
                vpnLink.classList.add('hidden');
                console.log("No VPN URI available");
            }
            
            // Set SSH fingerprint
            const sshFingerprint = document.getElementById('sshFingerprint');
            if (credential.ssh_public_key_fingerprint) {
                sshFingerprint.textContent = credential.ssh_public_key_fingerprint;
                console.log("SSH fingerprint set:", credential.ssh_public_key_fingerprint);
            } else {
                sshFingerprint.textContent = 'Not available';
                console.log("No SSH fingerprint available");
            }
            
            // Copy button functionality
            const copyBtn = document.getElementById('copySshFingerprintBtn');
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(credential.ssh_public_key_fingerprint || '')
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
            
            // MANUALLY SHOW THE MODAL (since Flowbite auto-init isn't working)
            const modal = document.getElementById('credentialsModal');
            modal.classList.remove('hidden');
            modal.style.display = 'flex';
            modal.setAttribute('aria-hidden', 'false');
            
            // Add close functionality
            const closeBtn = modal.querySelector('[data-modal-hide="credentialsModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
            
            // Close when clicking outside
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                }
            };
            
            // Close with Escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
        })
        .catch(err => {
            console.error("Error loading credentials:", err);
            alert('Failed to load credentials: ' + err.message);
        });
}


// Wipe Verification functionality
async function loadWipeVerification(bookingId) {
    return await apiGetWipeVerification(bookingId);
}

// Show wipe verification for a completed booking
function showWipeVerificationModal(bookingId) {
    console.log("Fetching wipe verification for booking:", bookingId);
    
    const modal = document.getElementById('wipeVerificationModal');
    const content = document.getElementById('wipeVerificationContent');
    
    // Check if modal elements exist
    if (!modal || !content) {
        console.error('Wipe verification modal elements not found');
        return;
    }
    
    // Show loading state
    content.innerHTML = `
        <div class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-2 text-gray-500 dark:text-gray-400">Loading verification details...</p>
        </div>
    `;
    
    // Show modal immediately - MANUALLY
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    
    loadWipeVerification(bookingId)
        .then(data => {
            console.log("Wipe verification response:", data);
            
            if (data.is_verified) {
                // Verified wipe
                content.innerHTML = `
                    <div class="text-center">
                        <div class="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full mb-4">
                            <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold text-green-600 dark:text-green-400 mb-2">Server Wiped & Verified</h3>
                        <p class="text-gray-600 dark:text-gray-400 mb-4">This server has been securely wiped and verified.</p>
                    </div>
                    
                    <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Method</p>
                                <p class="font-medium">${data.method_summary}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Status</p>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                                    ${data.status}
                                </span>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Verified At</p>
                                <p class="font-medium">${new Date(data.verified_at).toLocaleString()}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Your Data</p>
                                <p class="font-medium text-green-600 dark:text-green-400">Securely Erased</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Data Security Assurance</h4>
                        <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                            <li class="flex items-center">
                                <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                                All user data permanently removed
                            </li>
                            <li class="flex items-center">
                                <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                                Storage media securely overwritten
                            </li>
                            <li class="flex items-center">
                                <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                                Verification logged for compliance
                            </li>
                        </ul>
                    </div>
                `;
            } else {
                // Not verified or pending
                content.innerHTML = `
                    <div class="text-center">
                        <div class="inline-flex items-center justify-center w-16 h-16 ${
                            data.status === 'pending' ? 'bg-yellow-100 dark:bg-yellow-900' : 'bg-gray-100 dark:bg-gray-900'
                        } rounded-full mb-4">
                            <svg class="w-8 h-8 ${
                                data.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-400'
                            }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold ${
                            data.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-400'
                        } mb-2">
                            ${data.status === 'pending' ? 'Wipe Verification Pending' : 'Wipe Not Verified'}
                        </h3>
                        <p class="text-gray-600 dark:text-gray-400 mb-4">
                            ${data.status === 'pending' 
                                ? 'Server wipe is being processed and verified.' 
                                : 'Server wipe verification is not available.'}
                        </p>
                    </div>
                    
                    <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Status</p>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    data.status === 'pending' 
                                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                                        : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
                                }">
                                    ${data.status || 'Not Available'}
                                </span>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Method</p>
                                <p class="font-medium">${data.method_summary || 'Not Specified'}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">What This Means</h4>
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            ${data.status === 'pending'
                                ? 'The server wipe process has been initiated. Once completed and verified by our compliance team, the verification status will be updated here.'
                                : 'This booking does not have a wipe verification record. Contact support if you have concerns about data security.'}
                        </p>
                    </div>
                `;
            }
            
            // Add close functionality - MANUAL
            const closeBtn = modal.querySelector('[data-modal-hide="wipeVerificationModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
            
            // Close when clicking outside - MANUAL
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                }
            };
            
            // Close with Escape key - MANUAL
            const escapeHandler = (e) => {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
        })
        .catch(err => {
            console.error("Error loading wipe verification:", err);
            content.innerHTML = `
                <div class="text-center text-red-600 dark:text-red-400">
                    <svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <h3 class="text-lg font-semibold mb-2">Error Loading Verification</h3>
                    <p>${err.message || 'Failed to load wipe verification details.'}</p>
                </div>
            `;
            
            // Re-add close functionality for error state
            const closeBtn = modal.querySelector('[data-modal-hide="wipeVerificationModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
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
function rowHTML(b) {
    const userRole = localStorage.getItem('user_role');
    
    let actionButtons = '';
    
    // Common: Credentials button for ACTIVE bookings (both buyers and providers can see)
    if (b.status === 'active') {
        actionButtons += `
            <button class="view-credentials-btn inline-flex items-center gap-1 text-white bg-purple-600 hover:bg-purple-700 font-medium rounded-lg text-xs px-3 py-1.5 transition"
                    data-booking-id="${b.id}"
                    type="button"
                    title="View access credentials for this booking">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                </svg>
                Credentials
            </button>
        `;
    }
    
    // Role-specific buttons for COMPLETED bookings
    if (b.status === 'completed') {
        if (userRole === 'buyer') {
            // Buyer sees wipe verification
            actionButtons += `
                <button class="view-wipe-verification-btn inline-flex items-center gap-1 text-white bg-green-600 hover:bg-green-700 font-medium rounded-lg text-xs px-3 py-1.5 transition ml-2"
                        data-booking-id="${b.id}"
                        type="button"
                        title="View server wipe verification">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Wipe Verify
                </button>
            `;
        } else if (userRole === 'provider') {
            // Provider sees attestation details
            actionButtons += `
                <button class="view-provider-attestation-btn inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium rounded-lg text-xs px-3 py-1.5 transition ml-2 border border-blue-600 dark:border-blue-400"
                        data-booking-id="${b.id}"
                        type="button"
                        title="View wipe attestation details for this booking">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Attestation
                </button>
            `;
        }

    }
    
    return `
        <tr class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
            <td class="px-6 py-4">
                <div class="font-medium text-gray-900 dark:text-white">#${b.id.substring(0, 8)}...</div>
                <div class="mt-1 flex flex-wrap gap-1">
                    ${actionButtons}
                </div>
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

// Admin: Load all wipe attestations
async function loadWipeAttestations() {
    const container = document.getElementById('attestations-container');
    if (!container) return;
    
    try {
        const attestations = await apiGetAllAttestations();
        renderWipeAttestations(attestations);
    } catch (err) {
        container.innerHTML = `
            <div class="text-center py-8 text-red-600 dark:text-red-400">
                Failed to load wipe attestations: ${err.message}
            </div>
        `;
    }
}

// Admin: Render wipe attestations
function renderWipeAttestations(attestations) {
    const container = document.getElementById('attestations-container');
    if (!container) return;
    
    if (attestations.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                No wipe attestations found.
            </div>
        `;
        return;
    }
    
    const template = document.getElementById('attestation-row-template');
    container.innerHTML = '';
    
    attestations.forEach(attestation => {
        const clone = template.content.cloneNode(true);
        const row = clone.firstElementChild;
        
        // Fill attestation data
        row.querySelector('.booking-id').textContent = `#${attestation.booking_id.substring(0, 8)}...`;
        row.querySelector('.machine-info').textContent = `#${attestation.machine_id.substring(0, 8)}...`;
        row.querySelector('.wipe-method').textContent = attestation.method;
        row.querySelector('.attested-date').textContent = new Date(attestation.attested_at).toLocaleString();
        
        // Status badge
        const statusBadge = row.querySelector('.status-badge');
        statusBadge.textContent = attestation.status;
        
        switch(attestation.status) {
            case 'verified':
                statusBadge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900', 'dark:text-green-300');
                break;
            case 'rejected':
                statusBadge.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-900', 'dark:text-red-300');
                break;
            default:
                statusBadge.classList.add('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-300');
        }
        
        // Evidence link
        const evidenceLink = row.querySelector('.evidence-link');
        if (attestation.evidence_uri) {
            evidenceLink.href = attestation.evidence_uri;
            evidenceLink.textContent = 'View Evidence';
        } else {
            evidenceLink.parentElement.style.display = 'none';
        }
        
        // Notes
        const notesContent = row.querySelector('.notes-content');
        notesContent.textContent = attestation.notes || 'No notes provided';
        
        // Buttons
        const verifyBtn = row.querySelector('.verify-attestation-btn');
        const rejectBtn = row.querySelector('.reject-attestation-btn');
        const detailsBtn = row.querySelector('.view-details-btn');
        
        if (attestation.status === 'verified' || attestation.status === 'rejected') {
            verifyBtn.style.display = 'none';
            rejectBtn.style.display = 'none';
        } else {
            verifyBtn.addEventListener('click', () => reviewAttestation(attestation.id, 'verified'));
            rejectBtn.addEventListener('click', () => reviewAttestation(attestation.id, 'rejected'));
        }
        
        detailsBtn.addEventListener('click', () => showAttestationDetails(attestation.id, true));
        
        container.appendChild(row);
    });
}

// Admin: Review attestation
async function reviewAttestation(attestationId, status) {
    if (!confirm(`Are you sure you want to ${status} this wipe attestation?`)) {
        return;
    }
    
    try {
        await apiReviewAttestation(attestationId, status);
        alert(`Attestation ${status} successfully!`);
        await loadWipeAttestations(); // Reload the list
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

// Admin/Provider: Show attestation details
async function showAttestationDetails(attestationId, isAdmin = false) {
    const modal = document.getElementById('attestationDetailsModal');
    const content = document.getElementById('attestationDetailsContent');
    
    try {
        // For admin, get full admin view; for provider, get provider view
        let attestation;
        if (isAdmin) {
            // We need booking ID first, then get admin view
            const allAttestations = await apiGetAllAttestations();
            const target = allAttestations.find(a => a.id === attestationId);
            if (target) {
                attestation = await apiGetAdminBookingAttestation(target.booking_id);
            }
        } else {
            // Since we have attestationId directly, we can use machine attestations endpoint
            // to find the specific attestation, then get provider view
            const machineSelect = document.getElementById('wipeHistoryMachineSelect');
            const machineId = machineSelect.value;
            if (machineId) {
                const machineAttestations = await apiGetMachineAttestations(machineId);
                const target = machineAttestations.find(a => a.id === attestationId);
                if (target) {
                    attestation = await apiGetProviderBookingAttestation(target.booking_id);
                }
            }
        }
        
        if (!attestation) {
            throw new Error('Attestation not found');
        }
        
        content.innerHTML = `
            <div class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <div>
                            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Booking Information</h4>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <div class="space-y-2">
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-500 dark:text-gray-400">Booking ID:</span>
                                        <span class="font-mono text-sm">${attestation.booking_id}</span>
                                    </div>
                                    ${isAdmin && attestation.booking ? `
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Buyer:</span>
                                            <span class="text-sm">${attestation.booking.buyer_email || 'Unknown'}</span>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        
                        <div>
                            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Machine Information</h4>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <div class="space-y-2">
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-500 dark:text-gray-400">Machine ID:</span>
                                        <span class="font-mono text-sm">${attestation.machine_id}</span>
                                    </div>
                                    ${attestation.machine ? `
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Hostname:</span>
                                            <span class="text-sm">${attestation.machine.hostname || 'Unknown'}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Location:</span>
                                            <span class="text-sm">${attestation.machine.location_region || 'Unknown'}</span>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="space-y-4">
                        <div>
                            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Wipe Details</h4>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <div class="space-y-3">
                                    <div>
                                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Method</p>
                                        <p class="font-medium">${attestation.method}</p>
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Status</p>
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                            attestation.status === 'verified' 
                                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                                                : attestation.status === 'rejected'
                                                ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                                : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                                        }">
                                            ${attestation.status}
                                        </span>
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Attested At</p>
                                        <p class="font-medium">${new Date(attestation.attested_at).toLocaleString()}</p>
                                    </div>
                                    ${attestation.evidence_uri ? `
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Evidence</p>
                                            <a href="${attestation.evidence_uri}" 
                                               target="_blank"
                                               class="text-blue-600 dark:text-blue-400 hover:underline text-sm">
                                                ${attestation.evidence_uri}
                                            </a>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Notes</h4>
                    <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <p class="text-gray-700 dark:text-gray-300">${attestation.notes || 'No notes provided.'}</p>
                    </div>
                </div>
                
                ${isAdmin && attestation.status === 'pending' ? `
                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">Admin Actions</h4>
                        <div class="flex space-x-3">
                            <button onclick="reviewAttestation('${attestation.id}', 'verified')"
                                    class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                                Verify Attestation
                            </button>
                            <button onclick="reviewAttestation('${attestation.id}', 'rejected')"
                                    class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                                Reject Attestation
                            </button>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Show modal
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        
        // Add close functionality
        const closeBtn = modal.querySelector('[data-modal-hide="attestationDetailsModal"]');
        if (closeBtn) {
            closeBtn.onclick = () => {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            };
        }
        
        // Close when clicking outside
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            }
        };
        
        // Close with Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
    } catch (err) {
        content.innerHTML = `
            <div class="text-center text-red-600 dark:text-red-400">
                <svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <h3 class="text-lg font-semibold mb-2">Error Loading Details</h3>
                <p>${err.message || 'Failed to load attestation details.'}</p>
            </div>
        `;
    }
}

// Provider: Setup wipe history
function setupWipeHistory() {
    const machineSelect = document.getElementById('wipeHistoryMachineSelect');
    const container = document.getElementById('wipeHistoryContainer');
    const listContainer = document.getElementById('wipeHistoryList');
    
    if (!machineSelect || !container) return;
    
    // Populate machine dropdown
    if (machines.length > 0) {
        machineSelect.innerHTML = '<option value="">Choose a machine...</option>' +
            machines.map(m => 
                `<option value="${m.id}" data-hostname="${m.hostname || 'Unnamed'}">
                    ${m.hostname || "Machine #" + m.id}
                </option>`
            ).join("");
    }
    
    // Handle machine selection
    machineSelect.addEventListener('change', async function() {
        const machineId = this.value;
        const selectedOption = this.options[this.selectedIndex];
        const machineName = selectedOption.getAttribute('data-hostname');
        
        if (machineId) {
            // Show wipe history list
            listContainer.classList.remove('hidden');
            document.getElementById('selectedWipeMachineName').textContent = machineName;
            
            // Load wipe history
            await loadWipeHistory(machineId);
        } else {
            // Hide wipe history list
            listContainer.classList.add('hidden');
        }
    });
}

// Provider: Load wipe history for a machine
async function loadWipeHistory(machineId) {
    const container = document.getElementById('wipeHistoryContainer');
    if (!container) return;
    
    try {
        const attestations = await apiGetMachineAttestations(machineId);
        renderWipeHistory(attestations);
    } catch (err) {
        container.innerHTML = `
            <div class="text-red-600 dark:text-red-400">
                Failed to load wipe history: ${err.message}
            </div>
        `;
    }
}

// Provider: Render wipe history
function renderWipeHistory(attestations) {
    const container = document.getElementById('wipeHistoryContainer');
    if (!container) return;
    
    if (attestations.length === 0) {
        container.innerHTML = `
            <div class="text-gray-500 dark:text-gray-400 italic">
                No wipe history for this machine yet.
            </div>
        `;
        return;
    }
    
    const template = document.getElementById('wipe-history-template');
    container.innerHTML = '';
    
    attestations.forEach(attestation => {
        const clone = template.content.cloneNode(true);
        const row = clone.firstElementChild;
        
        // Fill attestation data
        row.querySelector('.booking-id').textContent = attestation.booking_id.substring(0, 8) + '...';
        row.querySelector('.wipe-method').textContent = attestation.method;
        row.querySelector('.attested-date').textContent = new Date(attestation.attested_at).toLocaleDateString();
        
        // Status badge
        const statusBadge = row.querySelector('.status-badge');
        statusBadge.textContent = attestation.status;
        
        switch(attestation.status) {
            case 'verified':
                statusBadge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900', 'dark:text-green-300');
                break;
            case 'rejected':
                statusBadge.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-900', 'dark:text-red-300');
                break;
            default:
                statusBadge.classList.add('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-300');
        }
        
        // Evidence link (only show if available)
        const evidenceContainer = row.querySelector('.evidence-link-container');
        const evidenceLink = row.querySelector('.evidence-link');
        if (attestation.evidence_uri) {
            evidenceContainer.classList.remove('hidden');
            evidenceLink.href = attestation.evidence_uri;
            evidenceLink.textContent = 'View Evidence';
        }
        
        // Notes
        const notesContent = row.querySelector('.notes-content');
        notesContent.textContent = attestation.notes || 'No notes provided';
        
        // Details button - store attestation ID, not booking ID
        const detailsBtn = row.querySelector('.view-attestation-details-btn');
        detailsBtn.setAttribute('data-attestation-id', attestation.id);
        detailsBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const attestationId = detailsBtn.getAttribute('data-attestation-id');
            showAttestationDetails(attestationId, false);
        });
        
        container.appendChild(row);
    });
}

// Provider: Load attestation for a booking
async function loadProviderAttestation(bookingId) {
    return await apiGetProviderBookingAttestation(bookingId);
}

// Show provider attestation details for a booking
// Show provider attestation details for a booking
function showProviderAttestationModal(bookingId) {
    console.log("Fetching provider attestation for booking:", bookingId);
    
    // Use wipeVerificationModal instead (available to all users)
    const modal = document.getElementById('wipeVerificationModal');
    const content = document.getElementById('wipeVerificationContent');
    
    // Check if modal elements exist
    if (!modal || !content) {
        console.error('Modal elements not found');
        alert('Error: Could not open attestation details. Please refresh the page.');
        return;
    }
    
    // Show loading state
    content.innerHTML = `
        <div class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-2 text-gray-500 dark:text-gray-400">Loading attestation details...</p>
        </div>
    `;
    
    // Update modal title
    const modalTitle = modal.querySelector('h3');
    if (modalTitle) {
        modalTitle.textContent = 'Wipe Attestation Details';
    }
    
    // Show modal immediately - MANUALLY since Flowbite might not be initialized
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    
    // Load attestation data
    loadProviderAttestation(bookingId)
        .then(data => {
            console.log("Provider attestation response:", data);
            
            // Create provider-specific content
            content.innerHTML = `
                <div class="space-y-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="space-y-4">
                            <div>
                                <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Booking Information</h4>
                                <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                    <div class="space-y-2">
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Booking ID:</span>
                                            <span class="font-mono text-sm">${data.booking_id}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Status:</span>
                                            <span class="text-sm font-medium ${data.status === 'verified' ? 'text-green-600' : data.status === 'rejected' ? 'text-red-600' : 'text-yellow-600'}">
                                                ${data.status}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div>
                                <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Wipe Details</h4>
                                <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                    <div class="space-y-3">
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Method</p>
                                            <p class="font-medium">${data.method}</p>
                                        </div>
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Attested At</p>
                                            <p class="font-medium">${new Date(data.attested_at).toLocaleString()}</p>
                                        </div>
                                        ${data.evidence_uri ? `
                                            <div>
                                                <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Evidence</p>
                                                <a href="${data.evidence_uri}" 
                                                   target="_blank"
                                                   class="text-blue-600 dark:text-blue-400 hover:underline text-sm break-all">
                                                    ${data.evidence_uri}
                                                </a>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="space-y-4">
                            <div>
                                <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Status & Review</h4>
                                <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                    <div class="space-y-3">
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Current Status</p>
                                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                data.status === 'verified' 
                                                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                                                    : data.status === 'rejected'
                                                    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                                            }">
                                                ${data.status.toUpperCase()}
                                            </span>
                                        </div>
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Review Progress</p>
                                            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                                                <div class="h-2.5 rounded-full ${
                                                    data.status === 'verified' ? 'bg-green-600 w-full' :
                                                    data.status === 'rejected' ? 'bg-red-600 w-full' :
                                                    data.status === 'pending' ? 'bg-yellow-600 w-1/2' : 'bg-gray-600 w-1/4'
                                                }"></div>
                                            </div>
                                            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                                                <span>Submitted</span>
                                                <span>${data.status === 'pending' ? 'Under Review' : data.status === 'verified' ? 'Verified' : 'Rejected'}</span>
                                            </div>
                                        </div>
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Next Steps</p>
                                            <p class="text-sm ${
                                                data.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' :
                                                data.status === 'verified' ? 'text-green-600 dark:text-green-400' :
                                                'text-red-600 dark:text-red-400'
                                            }">
                                                ${
                                                    data.status === 'pending' 
                                                        ? 'Your wipe attestation is being reviewed by our compliance team.' 
                                                        : data.status === 'verified'
                                                        ? 'Your wipe attestation has been verified and approved.'
                                                        : 'Your wipe attestation was rejected. Please check the notes and resubmit if needed.'
                                                }
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Notes & Additional Information</h4>
                        <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <p class="text-gray-700 dark:text-gray-300">${data.notes || 'No additional notes provided.'}</p>
                        </div>
                    </div>
                    
                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Compliance Information</h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <h5 class="text-sm font-medium text-gray-900 dark:text-white mb-2">For Your Records</h5>
                                <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                                    <li class="flex items-center">
                                        <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        Booking ID: ${data.booking_id}
                                    </li>
                                    <li class="flex items-center">
                                        <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        Machine ID: ${data.machine_id}
                                    </li>
                                    <li class="flex items-center">
                                        <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        Attestation ID: ${data.id}
                                    </li>
                                </ul>
                            </div>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <h5 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Support</h5>
                                <p class="text-sm text-gray-600 dark:text-gray-400">
                                    If you have questions about your wipe attestation status or need to update information, please contact our compliance team.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Add close functionality manually
            const closeBtn = modal.querySelector('[data-modal-hide="wipeVerificationModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
            
            // Close when clicking outside
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                }
            };
            
            // Close with Escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
        })
        .catch(err => {
            console.error("Error loading provider attestation:", err);
            
            content.innerHTML = `
                <div class="text-center">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full mb-4">
                        <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold text-red-600 dark:text-red-400 mb-2">No Attestation Found</h3>
                    <p class="text-gray-600 dark:text-gray-400 mb-4">
                        ${err.message || 'No wipe attestation found for this booking.'}
                    </p>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                        Wipe attestations are created after bookings complete. If this booking has recently ended, please wait a few moments for the attestation to be generated.
                    </p>
                </div>
            `;
            
            // Re-add close functionality for error state
            const closeBtn = modal.querySelector('[data-modal-hide="wipeVerificationModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
        });
}

window.reviewAttestation = reviewAttestation;