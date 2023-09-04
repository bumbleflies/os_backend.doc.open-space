from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.route.image import image_router
from api.route.image_details import image_details_router
from api.route.os import os_router
from api.route.session import session_router

app = FastAPI()

origins = [
    "http://open-space-app.servyy.duckdns.org",
    "https://open-space-app.servyy.duckdns.org",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex='^http://localhost:[0-9]*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(os_router)
app.include_router(image_router)
app.include_router(image_details_router)
app.include_router(session_router)


@app.get('/health')
def health():
    return {'success': True}
