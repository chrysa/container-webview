import axios from 'axios';
import { setupInterceptors } from './interceptors';

// VITE_API_URL must be set in .env.local for local dev (e.g. http://localhost:8000).
// In production, it is set at build time.
const BASE = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000') + '/api';

export const http = axios.create({
  baseURL: BASE,
  timeout: 10000,
});

setupInterceptors(http);
