import axios from "axios";
import { setupInterceptors } from "./interceptors";

// En dev, Vite proxifie /api → api:8000 (voir vite.config.ts).
// En prod avec serve (sans proxy), VITE_API_URL est bakée au build.
const BASE = (import.meta.env.VITE_API_URL ?? "") + "/api";

export const http = axios.create({
  baseURL: BASE,
  timeout: 10000,
});

setupInterceptors(http);
