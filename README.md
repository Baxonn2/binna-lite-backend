# Binna backend (Lite)
This is the backend for the Binna Lite project. It is a RESTful API that provides endpoints for the 
frontend to interact with the database.

## Installation
1. Clone the repository
2. Make sure you have Python 3.12 installed.
3. Create a virtual environment using `python -m venv venv`.
4. Activate the virtual environment using `source venv/bin/activate`.
5. Install the dependencies using `pip install -r requirements.txt`.

## Running the server for development
1. Make sure you have the virtual environment activated.
2. Run uvicorn using `uvicorn app:app --reload --port 8000`.  
If you need run the server and access it from another device, use 
`uvicorn app:app --reload --host 0.0.0.0 --port 8000`.

## Init server with default users
1. Run the server using this command `python app.py --run-script=init_default_users`.