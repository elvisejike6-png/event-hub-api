# Events Hub API

A FastAPI backend for managing events and ticket bookings.

## Features

- Create, view, update and delete events
- Search events by title
- Filter events by location and maximum price
- Pagination for event listings
- Create and update ticket bookings
- Calculate total booking cost
- Cancel bookings and return tickets
- View booking details using SQL JOIN
- Upload event images

## Technologies

- Python
- FastAPI
- SQLite
- Pydantic

## How to Run

Install the required packages:

```bash
pip install -r requirements.txt
```

Create the database tables:

```bash
python init_db.py
```

Start the API:

```bash
uvicorn main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```