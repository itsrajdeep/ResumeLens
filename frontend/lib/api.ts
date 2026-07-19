/**
 * Central API configuration.
 * Uses NEXT_PUBLIC_API_URL env var in production (set in Vercel).
 * Falls back to localhost:8000 for local development.
 */
const raw = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const BACKEND = raw.endsWith("/") ? raw.slice(0, -1) : raw;

export default BACKEND;
