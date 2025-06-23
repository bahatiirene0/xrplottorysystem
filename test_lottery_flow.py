import json
import requests
from time import sleep

with open('/root/xrpl_lottery_backend/testnet_wallets.json') as f:
    wallets = json.load(f)

for w in wallets:
    resp = requests.post('http://localhost:8000/api/tickets/buy', json={
        'wallet_address': w['address'],
        'num_tickets': 1
    })
    print(f"Ticket purchase for {w['address']}: {resp.status_code} {resp.json()}")
    sleep(0.5)

resp = requests.post('http://localhost:8000/api/draws/close')
print(f"Draw close: {resp.status_code} {resp.json()}")

resp = requests.get('http://localhost:8000/api/draws/history')
print(f"Draw history: {resp.status_code} {resp.json()}")
