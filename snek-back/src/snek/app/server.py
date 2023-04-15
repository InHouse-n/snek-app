from typing import List
import logger_provider
import dataclasses

from api import router
from api.home import home_router
from core.config import config
from core.exceptions.base import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (  # SQLAlchemyMiddleware,
    AuthBackend,
    AuthenticationMiddleware,
    ResponseLogMiddleware,
)
from fastapi import Depends, FastAPI, Request, WebSocket
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# from core.helpers.cache import Cache, RedisBackend, CustomKeyMaker


def init_routers(app_: FastAPI) -> None:
    app_.include_router(home_router)
    app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
        # Middleware(SQLAlchemyMiddleware),
        Middleware(ResponseLogMiddleware),
    ]
    return middleware


# def init_cache() -> None:
#     Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Hide",
        description="Hide API",
        version="1.0.0",
        docs_url=None if config.ENV == "production" else "/docs",
        redoc_url=None if config.ENV == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    # init_cache()
    return app_


log = logger_provider.get_logger(__name__)
app = create_app()

@app.websocket("/")
async def websocket_test(websocket: WebSocket):
    await websocket.accept()
    log.info("accepting websocket connection")
    await websocket.send_json("you connected!")
    while True:
        data = await websocket.receive_json()
        log.info(f"got data: {data}")
        await websocket.send_json(f"Yow broer, ge stuurde my dit: {data}")

@dataclasses.dataclass
class Point:
    x: int
    y: int

def consult_model(snake: List[Point], candy: Point) -> Direction:
    pass