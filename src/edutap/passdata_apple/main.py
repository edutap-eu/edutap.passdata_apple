from io import BytesIO
import os
import pathlib
import uuid
from fastapi import FastAPI, File, Response, UploadFile
from fastapi.responses import FileResponse, StreamingResponse


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}