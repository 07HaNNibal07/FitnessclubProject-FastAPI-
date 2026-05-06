from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from .routers import client,trainer,admin
from .core.utils import router as login
from .core.redis import redis
import logging
import time
import uuid


logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s:  %(asctime)s - %(name)s -  %(message)s')

logger = logging.getLogger('api')
    

app = FastAPI()

@app.middleware('/http')
async def get_coockies(request:Request,call_next):
    response = await call_next(request)
    
    if not request.cookies.get("device_id"):
        response.set_cookie(
            key="device_id",
            value=str(uuid.uuid4()),
            httponly=True
        )

    return response


@app.middleware("http")
async def log_all(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        duration = int((time.time() - start) * 1000)

        if response.status_code>=500:
            log_func = logger.error
        elif response.status_code>=400:
            log_func = logger.warning
        else:
            log_func = logger.info
                
        log_func(f"{request.client.host} - {request.method} {request.url.path} - {response.status_code} - {duration}ms")
        
        return response

    except Exception as e:
        duration = int((time.time() - start) * 1000)
        logger.error(
            f"{request.client.host} - {request.method} {request.url.path} - CRASH - {duration}ms - {e}"
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Server error"}
        )


app.include_router(router=client)
app.include_router(router=trainer)
app.include_router(router=admin)
app.include_router(router=login)

@app.get('/')
async def get_hello():
    return {'message': 'ok'}


if __name__ == "__main__":
    uvicorn.run("MyProjectFastApi.app.main:app", reload=True)
