import datetime
from fastapi import Depends, FastAPI, status, HTTPException,Request
from pydantic import Field, BaseModel
from typing import Optional
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import time

from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db
from models import Table as DBTable, Reservation as DBReservation

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time_ms = (time.time() - start_time) * 1000
    print(f"{request.method} {request.url.path} {response.status_code} {process_time_ms:.1f}ms")
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    field_name = error["loc"][-1] if error["loc"] else "body"
    return JSONResponse(
        status_code=400,
        content={"error": error["msg"], "field": str(field_name)}
    )

class TableCreate(BaseModel):
    number: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)
    zone: str = Field(..., min_length=1)

class TableUpdate(BaseModel):
    number: Optional[str] = Field(None, min_length=1)
    capacity: Optional[int] = Field(None, gt=0)
    zone: Optional[str] = Field(None, min_length=1)

class Table(TableCreate):
    id: int

class ReservationCreate(BaseModel):
    guest_name: str = Field(..., min_length=1)
    date_time: datetime 
    guests_count: int = Field(..., gt=0)

class ReservationResponse(ReservationCreate):
    id: int
    table_id: int

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/tables", status_code=status.HTTP_201_CREATED, response_model=Table)
def create_table(table_in: TableCreate, db: Session = Depends(get_db)):
    new_table = DBTable(
        number=table_in.number,
        capacity=table_in.capacity,
        zone=table_in.zone
    )
    db.add(new_table)
    db.commit()
    db.refresh(new_table) 
    return new_table

@app.get("/api/tables", response_model=list[Table])
def get_tables(
    limit: int = 10, 
    offset: int = 0, 
    zone: Optional[str] = None, 
    capacity: Optional[int] = None, 
    q: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    stmt = select(DBTable)

    if zone is not None:
        stmt = stmt.where(DBTable.zone == zone)
    if capacity is not None:
        stmt = stmt.where(DBTable.capacity == capacity)
    if q is not None:
        stmt = stmt.where(DBTable.number.ilike(f"%{q}%"))

    stmt = stmt.offset(offset).limit(limit)
    result = db.execute(stmt).scalars().all()
    return result

@app.get("/api/tables/{table_id}", response_model=Table)
def get_table(table_id: int, db: Session = Depends(get_db)):
    db_table = db.get(DBTable, table_id)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table

@app.delete("/api/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(table_id: int, db: Session = Depends(get_db)):
    db_table = db.get(DBTable, table_id)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    db.delete(db_table)
    db.commit()

@app.patch("/api/tables/{table_id}", response_model=Table)
def update_table(table_id: int, table_in: TableUpdate, db: Session = Depends(get_db)):
    db_table = db.get(DBTable, table_id)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    update_data = table_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_table, key, value)
        
    db.commit()
    db.refresh(db_table)
    return db_table

@app.get("/api/tables/{table_id}/reservations", response_model=list[ReservationResponse])
def get_table_reservations(table_id: int, db: Session = Depends(get_db)):
    db_table = db.get(DBTable, table_id)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    stmt = select(DBReservation).where(DBReservation.table_id == table_id)
    result = db.execute(stmt).scalars().all()
    
    return result