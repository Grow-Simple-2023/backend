import uvicorn
from fastapi import FastAPI
from routes import manager, rider, customer, generic
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generic.router, tags=["General"])
app.include_router(manager.router, prefix="/manager", tags=["Manager"])
app.include_router(rider.router, prefix="/rider", tags=["Rider"])
app.include_router(customer.router, prefix="/customer", tags=["Customer"])
