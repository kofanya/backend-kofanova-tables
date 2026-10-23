from fastapi import FastAPI, status, HTTPException,Request
from pydantic import Field, BaseModel
from typing import Optional
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()
tables_db = {}
current_id = 0

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

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/tables", status_code=status.HTTP_201_CREATED, response_model=Table)
def create_table(table_in: TableCreate):
    global current_id
    current_id += 1  
    new_table = Table(
        id=current_id,
        number=table_in.number,
        capacity=table_in.capacity,
        zone=table_in.zone
    )
    tables_db[current_id] = new_table
    return new_table

@app.get("/api/tables", response_model=list[Table])
def get_tables(limit: int = 10, offset: int = 0, zone: Optional[str] = None, capacity: Optional[int] = None):
    result = list(tables_db.values())

    if zone is not None:
        result = [t for t in result if t.zone == zone]
    if capacity is not None:
        result = [t for t in result if t.capacity == capacity]
    
    return result[offset : offset + limit]

@app.get("/api/tables/{table_id}", response_model=Table)
def get_table(table_id: int):
    if table_id not in tables_db:
        raise HTTPException(status_code=404, detail="Table not found")
    return tables_db[table_id]

@app.delete("/api/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(table_id: int):
    if table_id not in tables_db:
        raise HTTPException(status_code=404, detail="Table not found")
    del tables_db[table_id]

@app.patch("/api/tables/{table_id}", response_model=Table)
def update_table(table_id: int, table_in: TableUpdate):
    if table_id not in tables_db:
        raise HTTPException(status_code=404, detail="Table not found")
    
    current_table = tables_db[table_id]

    if table_in.number is not None:
        current_table.number = table_in.number
    if table_in.capacity is not None:
        current_table.capacity = table_in.capacity
    if table_in.zone is not None:
        current_table.zone = table_in.zone
        
    return current_table
