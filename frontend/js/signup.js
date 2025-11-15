console.log("signup.js loaded");

const SUPABASE_URL = "https://vtdfrecfwgqrtiodrlnj.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0ZGZyZWNmd2dxcnRpb2RybG5qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzExNTYsImV4cCI6MjA3ODY0NzE1Nn0.4fiWf5x9ACJdXr6OCLetr1fOKXwv-0ChYZDoY-Bm1kI";

const { createClient } = window.supabase;
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function handleSignup(event) {
  event.preventDefault();
  console.log("Signup form submitted");

  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;
  const passwordConfirm = document.getElementById("signup-password-confirm").value;
  const role = document.querySelector("input[name='role']:checked").value;

  const errorBox = document.getElementById("signup-error");
  errorBox.textContent = "";

  if (password !== passwordConfirm) {
    errorBox.textContent = "Passwords do not match.";
    return;
  }

  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: { role }
    }
  });

  if (error) {
    errorBox.textContent = error.message;
    return;
  }

  const session = data.session;

  // Persist the role locally
  localStorage.setItem("user_role", role);

  // If immediate login is enabled
  if (session?.access_token) {
    localStorage.setItem("access_token", session.access_token);
    window.location.href = "/index.html?signup_success=1";
    return;
  }

  errorBox.textContent =
    "Signup successful! Check your email to confirm your account.";
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("Signup DOM ready");
  const form = document.getElementById("signup-form");
  if (form) form.addEventListener("submit", handleSignup);
});