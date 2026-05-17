const BASE_URL = "http://localhost:8000";

async function apiFetch(path) {
  try {
    const res = await fetch(`${BASE_URL}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { data, error: null };
  } catch (err) {
    return { data: null, error: err.message };
  }
}

/**
 * Fetch all registered stores.
 */
export const fetchStores = () => apiFetch("/api/stores");

/**
 * Fetch forecast data for a store.
 */
export const fetchForecast = (storeId) => apiFetch(`/api/forecast?store_id=${storeId}`);

/**
 * Fetch inventory data for a store.
 */
export const fetchInventory = (storeId) => apiFetch(`/api/inventory?store_id=${storeId}`);

/**
 * Fetch overview stats for a store.
 */
export const fetchStats = (storeId) => apiFetch(`/api/stats?store_id=${storeId}`);

/**
 * Fetch recent WhatsApp messages for a store.
 */
export const fetchMessages = (storeId) => apiFetch(`/api/messages?store_id=${storeId}&limit=20`);
