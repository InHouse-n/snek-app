import dataclasses
import enum
from typing import List

import logger_provider
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
from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch

from src.snek.app.model import Linear_QNet

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

def load_snek_model():
    model = Linear_QNet(11, 256, 3)
    model.load_state_dict(torch.load("src/snek/app/base-model-300.pth"))
    model.eval()
    return model


log = logger_provider.get_logger(__name__)
app = create_app()
model = load_snek_model()


@app.websocket("/")
async def websocket_test(websocket: WebSocket):
    await websocket.accept()
    log.info("New Snek consultation initiated!")
    try:
        while True:
            state = await websocket.receive_json()
            move = consult_model(state)
            log.info(f"will move {move.name}")
            await websocket.send_json(move.value)
    except WebSocketDisconnect:
        log.info("Snek consultation terminated.")
        pass


class Direction(enum.Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

@dataclasses.dataclass
class Input:
    danger_straight: bool = False
    danger_right: bool = False
    danger_left: bool = False

    moving_left: bool = False
    moving_right: bool = False
    moving_up: bool = False
    moving_down: bool = False

    food_left: bool  = False
    food_right: bool = False
    food_up: bool = False
    food_down: bool = False

    def as_tensor(self) -> torch.tensor:        
        return torch.FloatTensor(list(map(as_int, [
            self.danger_straight, 
            self.danger_right, 
            self.danger_left, 

            self.moving_left,
            self.moving_right, 
            self.moving_up, 
            self.moving_down, 

            self.food_left, 
            self.food_right, 
            self.food_up, 
            self.food_down,
        ])))
    
    
    

def as_int(f):
    return 1 if f else 0


def next_pos(x, y, direction: Direction):    
    if direction == Direction.RIGHT:
        return x+1, y    
    if direction == Direction.LEFT:
        return x-1, y
    if direction == Direction.UP:
        return x, y-1
    if direction == Direction.DOWN:
        return x, y+1
    
def rotate_right(dir):
    if dir == Direction.RIGHT:
        return Direction.DOWN
    if dir == Direction.DOWN:
        return Direction.LEFT
    if dir == Direction.LEFT:
        return Direction.UP
    if dir == Direction.UP:
        return Direction.RIGHT


def rotate_left(dir):
    if dir == Direction.RIGHT:
        return Direction.UP
    if dir == Direction.UP:
        return Direction.LEFT
    if dir == Direction.LEFT:
        return Direction.DOWN
    if dir == Direction.DOWN:
        return Direction.RIGHT
    

def get_cell_value(grid, x, y):
    try:
        return grid[x][y]
    except IndexError:
        log.error(f"Index out of bounds: {x}, {y}")
        return "wall"

dangerous_places = {
    "wall",
    "tail",
    "body",
}

def print_grid(g):
    grid = "\n"
    for row in g:
        for cell in row:
            if cell == "free":
                grid += "."
            elif cell == "head":
                grid += "H"
            elif cell == "body":
                grid += "B"
            elif cell == "tail":
                grid += "T"
            elif cell == "wall":
                grid += "W"
            elif cell == "food":
                grid += "F"
            else:
                grid += "?"
        grid += "\n"
    log.info(grid)


def consult_model(state) -> Direction:
    input = Input()
    grid = state["grid"]
    print_grid(grid)
    direction = Direction(state["direction"])

    if direction == Direction.LEFT:
        input.moving_left = True
    if direction == Direction.RIGHT:
        input.moving_right = True
    if direction == Direction.UP:
        input.moving_up = True
    if direction == Direction.DOWN:
        input.moving_down = True

    food_pos = None
    head_pos = None
    for yind, row in enumerate(grid):
        for xind, cell in enumerate(row):
            if cell == "food":
                food_pos = (xind, yind)
            if cell == "head":
                head_pos = (xind, yind)

    
    next_pos_straight = next_pos(*head_pos, direction)
    next_pos_left = next_pos(*head_pos, rotate_left(direction))
    next_pos_right = next_pos(*head_pos, rotate_right(direction))

    log.info(f"direction {direction}")
    log.info(f"straight {get_cell_value(grid, *next_pos_straight)}")
    log.info(f"left {get_cell_value(grid, *next_pos_left)}")
    log.info(f"right {get_cell_value(grid, *next_pos_right)}")

    input.danger_straight = get_cell_value(grid, *next_pos_straight) in dangerous_places
    input.danger_left = get_cell_value(grid, *next_pos_left) in dangerous_places
    input.danger_right = get_cell_value(grid, *next_pos_right) in dangerous_places   

    if food_pos:
        if food_pos[0] < head_pos[0]:
            input.food_left = True
        if food_pos[0] > head_pos[0]:
            input.food_right = True
        if food_pos[1] < head_pos[1]:
            input.food_up = True
        if food_pos[1] > head_pos[1]:
            input.food_down = True

    model_input = input.as_tensor()
    log.info(input)
    prediction = model(model_input)
    log.info(prediction)
    move = torch.argmax(prediction).item()

    if move == 0:
        return direction
    if move == 1:
        return rotate_right(direction)
    if move == 2:
        return rotate_left(direction)
    
    