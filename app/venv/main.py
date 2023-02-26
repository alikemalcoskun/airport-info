from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user, data



app = FastAPI(title="AirportInfo",
              description="A RestAPI that allows users to get airport data from an open API service by ICAO code and add it to their favorites list.")


origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(user.router, prefix=API_PREFIX)
app.include_router(data.router, prefix=API_PREFIX)