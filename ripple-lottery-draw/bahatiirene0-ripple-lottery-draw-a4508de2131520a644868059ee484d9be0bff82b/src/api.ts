// API service for XRPL Lottery Backend
const API_BASE = "http://localhost:8000";

export async function getDrawStatus() {
    const res = await fetch(`${API_BASE}/draws/status`);
    if (!res.ok) throw new Error('Failed to fetch draw status');
    return res.json();
}
