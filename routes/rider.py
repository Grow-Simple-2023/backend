from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def rider_home():
    return {"message": "Welcome to Grow-Simplee Rider API"}