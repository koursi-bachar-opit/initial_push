console.log("login.js loaded");

// Supabase project values (same as signup.js)
const SUPABASE_URL = "https://vtdfrecfwgqrtiodrlnj.supabase.co";
const SUPABASE_ANON_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0ZGZyZWNmd2dxcnRpb2RybG5qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzExNTYsImV4cCI6MjA3ODY0NzE1Nn0.4fiWf5x9ACJdXr6OCLetr1fOKXwv-0ChYZDoY-Bm1kI";

// Make sure Supabase SDK is available
if (!window.supabase) {
  console.error("Supabase SDK did NOT load.");
}

const { createClient } = window.supabase;
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function handleLogin(event) {
  event.preventDefault();
  console.log("Login form submitted");

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errorBox = document.getElementById("login-error");
  errorBox.textContent = "";

  // Perform login
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    errorBox.textContent = error.message;
    return;
  }

  const session = data.session;
  if (!session || !session.access_token) {
    errorBox.textContent = "Login failed — no session returned.";
    return;
  }

  // Store JWT
  localStorage.setItem("access_token", session.access_token);

  // Load user to retrieve metadata (role)
  const { data: userData } = await supabase.auth.getUser();
  const role = userData?.user?.user_metadata?.role;

  if (role) {
    localStorage.setItem("user_role", role);
  }

  // Redirect you to homepage
  window.location.href = "/index.html";
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("Login DOM ready");
  const form = document.getElementById("login-form");
  if (form) {
    form.addEventListener("submit", handleLogin);
  } else {
    console.error("Could not find #login-form!");
  }
});