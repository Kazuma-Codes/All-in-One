from fastapi import APIRouter
from ...services.registry import get_supported_conversions

router = APIRouter()


@router.get("/")
def list_conversions():
    return get_supported_conversions()