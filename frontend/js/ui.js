// Loads templates
async function loadTemplate(name, target) {
  const base = await fetch("/base.html").then((r) => r.text());
  const dom = new DOMParser().parseFromString(base, "text/html");
  const tpl = dom.getElementById(name);

  if (!tpl) {
    console.error(`Template "${name}" not found in base.html`);
    return;
  }

  target.outerHTML = tpl.innerHTML.trim();
}

document.querySelectorAll("[data-template]").forEach((el) => {
  const name = el.getAttribute("data-template");
  loadTemplate(`tpl-${name}`, el);
});

// after templates load, build navbar and enforce route rules
document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    applyRoleBasedNav();
    enforceRouteProtection();
  }, 50); // wait for templates
});


//Role-based navigation
function applyRoleBasedNav() {
  const nav = document.getElementById("dynamic-nav");
  if (!nav) return;

  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("user_role"); // "buyer" | "provider"

  nav.innerHTML = ""; // clear

  // Always visible
  nav.innerHTML += `
    <a class="hover:text-gray-900 text-gray-700" href="/listings.html">Listings</a>
  `;

  // Default (not logged in)
  if (!token) {
    nav.innerHTML += `
      <a class="hover:text-gray-900 text-gray-700" href="/login.html">Log in</a>
      <a class="rounded-lg bg-blue-600 px-3 py-1 text-white hover:bg-blue-700" href="/signup.html">
        Sign up
      </a>
    `;
    return;
  }

  // Buyer nav
  if (role === "buyer") {
    nav.innerHTML += `
      <a class="hover:text-gray-900 text-gray-700" href="/bookings.html">Bookings</a>
      <a class="hover:text-gray-900 text-gray-700" href="/dashboard.html">Dashboard</a>
      <button id="logout-btn" class="text-red-600 hover:underline">Log out</button>
    `;
  }

  // Provider nav
  if (role === "provider") {
    nav.innerHTML += `
      <a class="hover:text-gray-900 text-gray-700" href="/bookings.html">Bookings</a>
      <a class="hover:text-gray-900 text-gray-700" href="/dashboard.html">Dashboard</a>
      <button id="logout-btn" class="text-red-600 hover:underline">Log out</button>
    `;
  }

  // Attach logout
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_role");
      window.location.href = "/index.html";
    });
  }
}


// Route protection
function enforceRouteProtection() {
  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("user_role");

  const path = window.location.pathname;

  const mustBeLoggedIn = ["/bookings.html", "/dashboard.html"];
  if (mustBeLoggedIn.includes(path) && !token) {
    window.location.href = "/login.html";
    return;
  }
}