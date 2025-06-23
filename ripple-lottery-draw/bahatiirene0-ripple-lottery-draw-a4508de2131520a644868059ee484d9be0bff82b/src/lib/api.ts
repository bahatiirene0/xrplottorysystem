export const API_BASE = 'http://localhost:8000/api';

export async function buyTicket(wallet_address: string, num_tickets: number = 1) {
  const res = await fetch(`/tickets/buy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address, num_tickets })
  });
  return res.json();
}

export async function listTickets(wallet_address: string) {
  const res = await fetch(`/tickets/list/`);
  return res.json();
}

export async function getCurrentDraw() {
  const res = await fetch(`/draws/current`);
  return res.json();
}

export async function closeDraw() {
  const res = await fetch(`/draws/close`, { method: 'POST' });
  return res.json();
}

export async function getDrawHistory() {
  const res = await fetch(`/draws/history`);
  return res.json();
}
