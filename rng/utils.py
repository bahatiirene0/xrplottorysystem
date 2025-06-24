import hashlib
import hmac # For HMAC-based PRNG for PickN
from typing import List, Dict, Any

def calculate_winner_index(seed: str, num_participants: int) -> int:
    """
    Calculate a winner index based on a seed (e.g., block hash) and the number of participants
    for a raffle-style game.
    """
    if num_participants <= 0:
        # This case should ideally be handled before calling,
        # e.g., draw closes with no winner if no participants.
        raise ValueError("Number of participants must be positive.")

    # Use SHA256 hash of the seed
    hash_bytes = hashlib.sha256(seed.encode('utf-8')).digest()

    # Convert first 8 bytes of the hash to an integer for a wider range before modulo.
    # Using more bytes from the hash can lead to better distribution.
    val = int.from_bytes(hash_bytes[:8], byteorder='big')

    winner_index = val % num_participants
    return winner_index

def generate_winning_picks(seed: str, game_config: Dict[str, Any]) -> List[Any]:
    """
    Generates a list of winning picks for "Pick N" style games based on a seed
    and game configuration. This uses HMAC-SHA256 for a pseudo-random but
    deterministic generation suitable for lotteries.

    Args:
        seed: A string seed (e.g., XRPL ledger hash).
        game_config: A dictionary containing game parameters.
            Expected keys for "pick_n_digits" (example):
                'num_picks': int - Number of items to pick.
                'min_digit': int - Minimum value for each pick (inclusive).
                'max_digit': int - Maximum value for each pick (inclusive).
                'allow_duplicates': bool - Whether duplicate values are allowed.

    Returns:
        A list of winning picks (e.g., list of integers for pick_n_digits).

    Raises:
        ValueError: If game_config is missing required parameters or parameters are invalid.
    """
    num_picks = game_config.get('num_picks')
    min_val = game_config.get('min_digit')
    max_val = game_config.get('max_digit')
    allow_duplicates = game_config.get('allow_duplicates', False) # Default to False if not specified

    # Validate configuration
    if not isinstance(num_picks, int) or num_picks <= 0:
        raise ValueError("'num_picks' must be a positive integer.")
    if not isinstance(min_val, int) or not isinstance(max_val, int):
        raise ValueError("'min_digit' and 'max_digit' must be integers.")
    if not isinstance(allow_duplicates, bool):
        raise ValueError("'allow_duplicates' must be a boolean.")
    if min_val > max_val:
        raise ValueError("'min_val' cannot be greater than 'max_val'.")

    value_range_size = max_val - min_val + 1
    if not allow_duplicates and num_picks > value_range_size:
        raise ValueError("'num_picks' cannot be greater than the range of possible unique values if duplicates are not allowed.")

    picks: List[Any] = []
    # Use HMAC to generate a sequence of pseudo-random bytes.
    # The 'counter' ensures that we can derive multiple distinct numbers.

    # The key for HMAC can be a fixed string or derived from the seed as well.
    # Using a fixed key here for simplicity. For enhanced security, key could be an env variable.
    hmac_key = b"LotteryPickNKey_v1"

    counter = 0
    max_attempts_per_pick = 100 # Safety for non-duplicate generation in tight ranges

    while len(picks) < num_picks:
        # Generate a HMAC digest using the seed and a counter to ensure fresh bytes for each pick attempt.
        # The counter is updated in each iteration of the outer loop for each pick,
        # and also in the inner loop if trying to find a non-duplicate.
        message_to_hash = seed.encode('utf-8') + counter.to_bytes(4, 'big')
        h = hmac.new(hmac_key, message_to_hash, hashlib.sha256)

        random_bytes = h.digest()

        # Iterate through bytes of the hash to derive numbers.
        # This approach is more robust than just taking the first few bytes,
        # especially if num_picks is large or value_range_size is small.
        # We'll try to derive one pick per HMAC round, using enough bytes for good modulo.

        # Use 4 bytes for a 32-bit integer, should be enough for typical lottery number ranges.
        if len(random_bytes) < 4:
            # Should not happen with SHA256, but as a safeguard
            raise ValueError("HMAC digest too short.")

        val_from_hash = int.from_bytes(random_bytes[:4], byteorder='big')
        current_pick = min_val + (val_from_hash % value_range_size)

        if not allow_duplicates:
            attempt = 0
            while current_pick in picks:
                attempt += 1
                if attempt > max_attempts_per_pick:
                    # This indicates a potential issue, either range is too small for num_picks
                    # or an extremely unlikely hash collision sequence.
                    raise ValueError(f"Could not find a unique pick after {max_attempts_per_pick} attempts. Range too small or PRNG issue. Picks so far: {picks}")

                # If pick is already there, try a new value from the same hash or by incrementing counter
                # For simplicity, increment counter and re-hash to get a new pseudo-random value.
                counter += 1
                message_to_hash = seed.encode('utf-8') + counter.to_bytes(4, 'big')
                h_new = hmac.new(hmac_key, message_to_hash, hashlib.sha256)
                new_random_bytes = h_new.digest()
                if len(new_random_bytes) < 4: raise ValueError("HMAC digest too short on retry.")
                val_from_hash = int.from_bytes(new_random_bytes[:4], byteorder='big')
                current_pick = min_val + (val_from_hash % value_range_size)
            picks.append(current_pick)
        else: # Duplicates are allowed
            picks.append(current_pick)

        counter += 1 # Crucial: ensure next primary pick attempt uses a different input to HMAC

    return picks # Will contain num_picks items
