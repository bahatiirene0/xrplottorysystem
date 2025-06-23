from mnemonic import Mnemonic
import bip32utils
from xrpl.core.keypairs import derive_classic_address, generate_seed, derive_keypair
from xrpl.clients import JsonRpcClient
from xrpl.models.requests.account_info import AccountInfo

mnemonic_phrase = "dream squeeze seven saddle valid occur coral salad tobacco bamboo oil zebra"
m = Mnemonic("english")
seed = m.to_seed(mnemonic_phrase)
bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
# BIP44 path for XRPL: m/44'/144'/0'/0/0
child_key_obj = bip32_root_key_obj.ChildKey(44 + bip32utils.BIP32_HARDEN).ChildKey(144 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0).ChildKey(0)
private_key = child_key_obj.WalletImportFormat()
# Generate XRPL seed and keypair
xrpl_seed = generate_seed()
public_key, private_key_hex = derive_keypair(xrpl_seed)
address = derive_classic_address(public_key)
print(f"XRPL Address: {address}")

client = JsonRpcClient("https://s1.ripple.com:51234/")
try:
    acct_info = AccountInfo(account=address, ledger_index="validated", strict=True)
    response = client.request(acct_info)
    print(f"Account info: {response.result}")
except Exception as e:
    print(f"Error fetching account info: {e}")
