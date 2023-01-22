from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def customer_home():
    return {"message": "Welcome to Grow-Simplee customer API"}