from xrpl.wallet import generate_faucet_wallet
from xrpl.clients import JsonRpcClient
import json

client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
wallets = []
for i in range(10):
    wallet = generate_faucet_wallet(client, debug=True)
    wallets.append({
        'address': wallet.classic_address,
        'seed': wallet.seed,
        'public_key': wallet.public_key,
        'private_key': wallet.private_key
    })
with open('/root/xrpl_lottery_backend/testnet_wallets.json', 'w') as f:
    json.dump(wallets, f, indent=2)
print(json.dumps(wallets, indent=2))
