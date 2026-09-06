from fastapi import FastAPI,HTTPException,Query,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import date
import os
import shutil
app = FastAPI()
class Booking(BaseModel):
    user_id : int
    event_id : int
    quantity : int
    booking_date : date
    status : str
    
class Event(BaseModel):
    title : str
    description : str
    location : str
    event_date : date 
    price : int
    available_ticket : int
    image : str
    created_by : str
    

conn = sqlite3.connect("event_hub.db")
cursor = conn.cursor()
conn.commit()
conn.close()

# add booking
@app.post("/bookings")
def create_booking(booking:Booking):
    conn = sqlite3.connect("event_hub.db")
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT price, available_ticket FROM events WHERE id =? """,(booking.event_id,)
                   
    )
    event =cursor.fetchone()
    
    if event is None:
        raise HTTPException(status_code=404, detail= "Event Not Found"
        )
    ticket_price = event[0]
    available_ticket = event[1]
    
    if booking.quantity <= 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Quantity Must Be Greater Than Zero"
    )
    if booking.quantity >  available_ticket:
        conn.close()
        raise HTTPException(
            status_code=404, detail="Not enough ticket available"
        )
    if booking.quantity < available_ticket:
        conn.close()
        raise HTTPException (status_code=404, detail=f"Only{available_ticket}tickets remaining")
    
    total_cost = ticket_price * booking.quantity
    
    cursor.execute("""INSERT INTO bookings(user_id,event_id,quantity,booking_date,status)VALUES(?,?,?,?,?)""", (booking.user_id,booking.event_id,booking.quantity,str(booking.booking_date),booking.status))
    
    cursor.execute("""UPDATE events SET available_ticket = available_ticket-? WHERE id = ?""",(booking.quantity,booking.event_id))
    
    conn.commit()
    conn.close()
    return{
        "message":"Booking Created Successfully",
        "user_id": booking.user_id,
        "event_id":booking.event_id,
        "quantity":booking.quantity,
        "total_cost":total_cost,
        "booking_date":booking.booking_date,
        "status" :booking.status
        
        }
    
# view Bookings

@app.get("/bookings")
def get_bookings():
    conn = sqlite3.connect("event_hub.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT events.title,bookings.quantity , events.price * bookings.quantity AS total_cost,bookings.status FROM bookings JOIN events ON bookings.event_id = events.id""")
    bookings = cursor.fetchall()
    conn.close()
    result = []
    
    for booking in bookings:
        result.append(
            {
                "event":booking[0],
                "quantity":booking[1],
                "total_cost":booking[2],
                "status":booking[3]
            }
        )
    return result
# update booking
@app.put("/update_booking/{id}")
def update_booking (id:int,booking:Booking):
    conn = sqlite3.connect("event_hub.db")
    cursor = conn.cursor()
    cursor.execute("""UPDATE bookings SET quantity=?,status=? WHERE id =?""", (booking.quantity,booking.status,id))
    conn.commit()
    conn.close()
    
# cancel Booking

@app.put("/bookings/{id}/cancel")
def cancel_booking(id:int):
    conn = sqlite3.connect("event_hub.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT event_id, quantity,status FROM bookings  WHERE id = ?""",(id,))
    booking = cursor.fetchone()
    if booking is None:
        conn.close()
        raise HTTPException(
            status_code=404, detail="Booking not found"
        )    
    event_id = booking[0]
    quantity = booking[1] 
    current_status = booking[2]
    if current_status.lower() == "cancelled":
        conn.close()
        raise HTTPException(
            status_code=404, detail="Booking is already cancelled"
        ) 
    cursor.execute("""UPDATE bookings SET status = ? WHERE id =? """,("cancelled",id))
    cursor.execute("""UPDATE events SET available_ticket = available_ticket + ? WHERE id = ?""", (quantity,event_id)
    )
    conn.commit()
    conn.close()
    return{
        "message": "Booking cancelled successfully ",
        "booking_id":id,
        "returned_tickets":quantity,
        "status":"Cancelled"
    }

# Bookings details

@app.get("/bookings/details")
def get_booking_details():
    conn = sqlite3.connect("event_hub.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT users.name, events.title, events.location, events.event_date, bookings.quantity,events.price, bookings.status FROM bookings JOIN users ON bookings.user_id = users.id  JOIN events ON bookings.event_id = events.id""")
    bookings = cursor.fetchall()
    conn.close()
    
    result = []
    for booking in bookings:
        result.append(
            {
                "user": booking[0],
                "event": booking[1],
                "location": booking[2],
                "date": booking[3], 
                "quantity": booking[4],
                "price": booking[5],
                "status": booking[6]
            }
        )

    # add event
@app.post("/add_event")
def add_events(event:Event):
    conn=sqlite3.connect("event_hub.db")
    cursor =conn.cursor()
    cursor.execute("""INSERT INTO events(title,description,location,event_date,price,available_ticket,image,created_by)VALUES(?,?,?,?,?,?,?,?)""",(event.title,event.description,event.location,event.event_date,event.price,event.available_ticket,event.image,event.created_by))
    conn.commit()
    conn.close()
    return {
        "message":"Added successfully"
    }
    
# retrive events
@app.get("/events")
def get_events(
    limit : int = Query(default=10),
    offset : int = Query(default=0)
):
    
    conn=sqlite3.connect("event_hub.db")
    cursor =conn.cursor()
    query =(f"""
        SELECT * FROM events  LIMIT ? OFFSET ?
        """)
    cursor.execute(query, (limit, offset))
    events = cursor.fetchall()
    conn.close()
    return events


# retrive one event

@app.get("/event/{id}")
def get_event(id:int):
    conn=sqlite3.connect("event_hub.db")
    cursor =conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id =?",id)
    event = cursor.fetchone()
    conn.commit()
    conn.close()
    if event is None:
        raise Exception(status_code = 404 , detail = "event do not exist")
    return event
    
    
# update_event
@app.put("/event_update/{id}")
def update_events(id:int, event:Event):
    conn=sqlite3.connect("event_hub.db")
    cursor =conn.cursor()
    cursor.execute("""UPDATE events SET title =?,description =?,location=?,event_date =?,price=?,available_ticket=?,image=?,created_by=? WHERE id = ?""",(event.title,event.description,event.location,event.event_date,event.price,event.available_ticket,event.image,event.created_by,id))
    conn.commit()
    conn.close()
    return{
        "message":"updated successfully"
    }

# DELET EVENT
@app.delete("/event_delete/{id}")
def delete_events(id:int):
    conn=sqlite3.connect("event_hub.db")
    cursor =conn.cursor()
    cursor.execute("DELETE FROM events WHERE id =?",(id,))
    conn.commit()
    conn.close()
    
# SEARCH FOR EVENT

@app.get("/event_search/search")
def search_event(title:str):
    conn=sqlite3.connect("event_hub.db")
    cursor =conn.cursor()
    cursor.execute("SELECT * FROM events WHERE title LIKE ?",(F"%{title}%",))
    events=cursor.fetchall()
    conn.commit()
    conn.close()
    return events
    
    # events filter
@app.get("/events/filter")
def filtering(max_price:int = None, location :str = None):
    conn=sqlite3.connect("event_hub.db")
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM events WHERE(? IS NULL OR price <= ?)AND(? IS NULL  OR location = ? )""",(max_price,max_price,location,location)) 
    events = cursor.fetchall()
    conn.commit()
    conn.close() 
    return events

# upload
@app.post("/{id}/image")
def upload_event(id: int, image: UploadFile = File(...)):
    allowed_extensions = [".jpg",".jpeg",".png",".webp"]
    extension = os.path.splitext(image.filename)[1].lower()
    
    if extension not in allowed_extensions:
        return{"message":"File type not allowed"}
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{image.filename}"
    with open (file_path, "wb") as buffer:
        shutil.copyfileobj(image, buffer)
        
        
    