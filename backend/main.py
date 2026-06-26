import os
import socket

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database.db import engine, Base, SessionLocal
from models.book import Book
import models
from seed import seed_db

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-seed the database if it's empty (specifically for SQLite on Render)
db = SessionLocal()
try:
    if db.query(Book).count() == 0:
        print("Database is empty. Auto-seeding...")
        seed_db()
except Exception as e:
    print(f"Error during auto-seed: {e}")
finally:
    db.close()

# Import routers
from routes import auth, books, requests, loans, members, analytics, reports, notifications, chatbot, settings

app = FastAPI(title="LibraryAI Pro API", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(requests.router)
app.include_router(loans.router)
app.include_router(members.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(notifications.router)
app.include_router(chatbot.router)
app.include_router(settings.router)


def find_available_port(start_port: int = 8001) -> int:
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1


# Mount Frontend directory at the root /
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

if not os.path.exists(frontend_path):
    frontend_path = "./frontend"

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"message": "LibraryAI Pro Backend running successfully. Frontend files not found."}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
