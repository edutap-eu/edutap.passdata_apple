from io import BytesIO
import os
import pathlib
import uuid
from fastapi import FastAPI, File, Response, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

vardir = pathlib.Path("var")
certsdir = vardir / "certs"
certfile = certsdir / "certificate.pem"
keyfile = certsdir / "private.key"
wwdrfile = certsdir / "wwdr_certificate.pem"

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}