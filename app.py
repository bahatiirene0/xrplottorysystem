from fastapi import FastAPI
from tickets.router import router as tickets_router
from draws.router import router as draws_router
from lottery_categories.router import router as categories_router
from winners.router import router as winners_router
from referrals.router import router as referrals_router # Import the referrals router
from users.router import router as users_router # Import the users router
from auth.router import router as auth_router # Import the auth router
from syndicates.router import router as syndicates_router # Import the syndicates router
from gamification.router import router as gamification_router # Import the gamification router
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
app.include_router(users_router, prefix="/api/users", tags=["Users"]) # Add the users router
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"]) # Add the auth router
app.include_router(syndicates_router, prefix="/api/syndicates", tags=["Syndicates"]) # Add the syndicates router
app.include_router(gamification_router, prefix="/api/gamification", tags=["Gamification"]) # Add the gamification router
