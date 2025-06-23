from fastapi import FastAPI
from tickets.router import router as tickets_router
from draws.router import router as draws_router

app = FastAPI()

app.include_router(tickets_router, prefix="/api/tickets", tags=["tickets"])
app.include_router(draws_router, prefix="/api/draws", tags=["draws"])
