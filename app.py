from fastapi import FastAPI
from tickets.router import router as tickets_router
from draws.router import router as draws_router
from lottery_categories.router import router as categories_router
from winners.router import router as winners_router
from referrals.router import router as referrals_router # Import the referrals router
from database import close_db_connection, connect_db, get_db

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    try:
        connect_db()
        get_db()
        print("MongoDB connected successfully for FastAPI startup.")
    except Exception as e:
        print(f"Failed to connect to MongoDB on startup: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    close_db_connection()
    print("MongoDB connection closed for FastAPI shutdown.")


app.include_router(tickets_router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(draws_router, prefix="/api/draws", tags=["Draws"])
app.include_router(categories_router, prefix="/api/lottery_categories", tags=["Lottery Categories"])
app.include_router(winners_router, prefix="/api/winners", tags=["Winners"])
app.include_router(referrals_router, prefix="/api/referrals", tags=["Referrals"]) # Add the referrals router
