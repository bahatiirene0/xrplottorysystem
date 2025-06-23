from fastapi import APIRouter, HTTPException
from .models import Draw
from tickets.db import ticket_db
from rng.utils import calculate_winner_index
from datetime import datetime
from xrpl.clients import JsonRpcClient
from xrpl.models.requests.ledger import Ledger
import os

router = APIRouter()

draws = []
current_draw_id = 1
XRPL_RPC_URL = os.environ.get('XRPL_RPC_URL', 'https://s.altnet.rippletest.net:51234/')

def get_latest_ledger_hash():
    client = JsonRpcClient(XRPL_RPC_URL)
    ledger_request = Ledger(ledger_index="validated", transactions=False, expand=False)
    response = client.request(ledger_request)
    return response.result.get('ledger_hash')

def get_current_draw():
    for d in draws:
        if d.status == 'open':
            return d
    new_draw = Draw(
        draw_id=len(draws)+1,
        status='open',
        participants=[t.wallet_address for t in ticket_db],
        timestamp=datetime.utcnow().isoformat()
    )
    draws.append(new_draw)
    return new_draw

@router.get('/current', response_model=Draw)
def get_draw():
    return get_current_draw()

@router.post('/close')
def close_draw():
    draw = get_current_draw()
    draw.status = 'closed'
    ledger_hash = get_latest_ledger_hash()
    if not ledger_hash:
        raise HTTPException(status_code=500, detail='Could not fetch XRPL ledger hash')
    draw.ledger_hash = ledger_hash
    participants = [t.wallet_address for t in ticket_db]
    draw.participants = participants
    if not participants:
        draw.winner = None
        draw.status = 'completed'
        return {'message': 'No participants, draw completed with no winner.'}
    winner_idx = calculate_winner_index(draw.ledger_hash, len(participants))
    draw.winner = participants[winner_idx]
    draw.status = 'completed'
    return {'message': 'Draw completed.', 'winner': draw.winner, 'ledger_hash': draw.ledger_hash}

@router.get('/history', response_model=list[Draw])
def draw_history():
    return draws
