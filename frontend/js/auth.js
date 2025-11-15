import { supabase } from "./api.js";

export async function login(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) return { error };

  const token = data.session?.access_token;
  if (!token) return { error: { message: "No token returned" } };

  localStorage.setItem("access_token", token);
  return { success: true };
}

export function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/login.html";
}

export function requireAuth() {
  const token = localStorage.getItem("access_token");
  if (!token) window.location.href = "/login.html";
}