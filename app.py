import uvicorn
from fastapi import FastAPI

app = FastAPI()

# Initializing database
from src.database.database import Database
Database().migrate()

# Configuring cors
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://open.binna.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importing routes
from src.domains.auth.routes import router as auth_router
from src.domains.chat.routes import router as chat_router
from src.domains.customer.routes import router as customer_router

# Including routes
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(customer_router)

def process_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="Run the FastAPI server"
    )
    parser.add_argument(
        "--run-script",
        type=str,
        help="Run the script with the given name"
    )
    args = parser.parse_args()
    if args.run_script:
        run_script(args.run_script)

def run_script(script_name: str):
    import importlib
    importlib.import_module(f"src.scripts.{script_name}")

if __name__ == "__main__":
    process_args()

    # uvicorn.run(
    #     app,
    #     host="0.0.0.0",
    #     port=8000,
    #     log_level="debug"
    # )

