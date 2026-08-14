from fastapi import APIRouter
from . import auth, files, jobs, users, conversions, health, ws, batch, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(conversions.router, prefix="/conversions", tags=["conversions"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

api_router.include_router(ws.router, tags=["websocket"])