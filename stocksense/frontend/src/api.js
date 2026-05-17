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

export const fetchStores = () => apiFetch("/api/stores");
export const fetchForecast = (storeId) => apiFetch(`/api/forecast?store_id=${storeId}`);
export const fetchInventory = (storeId) => apiFetch(`/api/inventory?store_id=${storeId}`);
export const fetchStats = (storeId) => apiFetch(`/api/stats?store_id=${storeId}`);
export const fetchMessages = (storeId) => apiFetch(`/api/messages?store_id=${storeId}&limit=20`);
