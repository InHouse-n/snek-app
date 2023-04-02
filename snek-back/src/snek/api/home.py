from core.fastapi.dependencies import AllowAll, PermissionDependency
from fastapi import APIRouter, Depends, Response

home_router = APIRouter()


@home_router.get("/home", dependencies=[Depends(PermissionDependency([AllowAll]))])
async def home():
    return Response(status_code=200)
