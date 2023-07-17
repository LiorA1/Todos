from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_company():
    return {"company_name": "Example Company, LLc"}


@router.get("/employees")
async def get_employees():
    return 162
