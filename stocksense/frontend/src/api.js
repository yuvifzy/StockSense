const BASE_URL = "http://localhost:8000";

async function request(path) {
  try {
    const response = await fetch(`${BASE_URL}${path}`);
    if (!response.ok) {
      return {
        data: null,
        error: `Request failed (${response.status})`,
      };
    }
    const data = await response.json();
    return { data, error: null };
  } catch (err) {
    return {
      data: null,
      error: err instanceof Error ? err.message : "Unknown error",
    };
  }
}

export async function fetchStores() {
  return request("/api/stores");
}

export async function fetchForecast(storeId) {
  return request(`/api/forecast?store_id=${storeId}`);
}

export async function fetchInventory(storeId) {
  return request(`/api/inventory?store_id=${storeId}`);
}

export async function fetchStats(storeId) {
  return request(`/api/stats?store_id=${storeId}`);
}

export async function fetchMessages(storeId) {
  return request(`/api/messages?store_id=${storeId}&limit=20`);
}
