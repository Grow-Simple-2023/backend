import uvicorn
from fastapi import FastAPI
from routes import admin, rider, customer, generic

app = FastAPI()

app.include_router(generic.router, tags=["General"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(rider.router, prefix="/rider", tags=["Rider"])
app.include_router(customer.router, prefix="/customer", tags=["Customer"])
