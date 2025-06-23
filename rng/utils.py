def calculate_winner_index(ledger_hash: str, num_participants: int) -> int:
    hash_bigint = int(ledger_hash, 16)
    return hash_bigint % num_participants if num_participants > 0 else -1
