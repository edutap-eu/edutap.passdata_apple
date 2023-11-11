from io import BytesIO
import os
import pathlib
from typing import Annotated, Any
import uuid
from fastapi import FastAPI, File, HTTPException, Response, UploadFile, Depends, status
from fastapi.responses import FileResponse, StreamingResponse

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from edutap.passdata_apple.model import PassTemplate

from .common import app, engine, get_session

# auth stuff
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from edutap.passdata_apple.main import engine, get_session

SECRET_KEY = os.environ.get("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# /auth stuff


api_keys = [
    "akljnv13bvi2vfo0b0bw"
]  # This is encrypted in the database


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


# @app.get("/protected", dependencies=[Depends(api_key_auth)])
# def add_post() -> dict:
#     return {
#         "data": "You used a valid API key."
#     }
    

# /api key auth

@app.get("/")
def read_root(db_session: Session = Depends(get_session)):
    return {"msg": "Hello World"}


# @app.get("/save_url")
# def save_url(
#     template_identifier: str, 
#     record_identifier: str, 
#     pass_patches: list[dict[str, Any]]=[],
#     Depends(oauth2_scheme)
# ) -> str:
#     """
#     just creates the jwt that contains the full information, but no apple-signing yet
#     https://pyjwt.readthedocs.io/en/latest/usage.html#encoding-decoding-tokens-with-rs256-rsa
#     """
    
#     return the_jwt
   
   
# @app.post("/download_pass")
# def download_pass(jwt: str):
#     """
#     download the pass from the given jwt which is self-contained.
#     - pass will be signed
#     - issued_pass will be stored in the db
#     """
#     # pass_object = apple_models.Pass.load(jwt)
#     # pkpass = pass_object.create(
#     #     certfile,
#     #     keyfile,
#     #     wwdrfile,
#     #     "",
#     # )
    
#     return StreamingResponse(BytesIO(pkpass.getvalue()), media_type="application/vnd.apple.pkpass")

@app.post("/protected")
def protected(api_key: str = Annotated[str, Depends(oauth2_scheme)], name: str = ""):
    return {"message": "protected", "name": name}

@app.post("/fileupload")
def fileupload(api_key: str = Depends(oauth2_scheme), name: str = "", passfile: UploadFile =     File(...)):
    print(passfile)
    return {"message": "fileupload protected", "name": name}



@app.post("/upload_pass_template")
async def upload_pass_template(
    api_key = Depends(oauth2_scheme),
    template_identifier: str="", 
    pkpass: UploadFile = File(...),
    db_session: Session = Depends(get_session)
) -> str:
    """
    upload a pkpass file that contains a template
    """
    data = await pkpass.read()
    template = PassTemplate.from_passfile(data, template_identifier=template_identifier, backoffice_identifier="test")
    db_session.add(template)
    db_session.commit()
    return "ok"
    
    
# TODO: CRUD stuff for pass templates