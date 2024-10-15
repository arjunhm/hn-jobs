## Installation

Run `pip install -r requirements.txt`.  
Uses [Postgres](https://www.postgresql.org/download/) for backend.

## Configuration

Create `.env` inside `backend/`

```
DB_NAME = "my-db"
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"
SKIP_LOCATIONS = ["berlin", "amsterdam", "london", "europe"] -- list of locations to be skipped
```

## Running the app

`cd backend/`  
For initial setup (optional): `python setup.py`  
To run flask: `python app.py`  
Go to http://127.0.0.1:5000/  


