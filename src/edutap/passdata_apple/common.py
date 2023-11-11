
import os
from pathlib import Path

from fastapi import FastAPI
import fastapi_chameleon
from sqlmodel import Session, create_engine

print(os.environ)

env = settings = os.environ


FORCE_HTTPS = settings.get("FORCE_HTTPS", True) 
if FORCE_HTTPS == 'false':
    FORCE_HTTPS = False

root_path = ""

app = FastAPI(
    # root_path=root_path, 
    docs_url=root_path+"/docs", 
    openapi_prefix=root_path,
    version="0.1.6.3",
    # redoc_url=None,
    # root_path_in_servers=False,
    root_path=""
)

app.root_path = root_path

dev_mode=True
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = str(BASE_DIR / "templates")
fastapi_chameleon.global_init(TEMPLATE_DIR, auto_reload=dev_mode)


VAR_DIR = Path(env.get("VAR_DIR", BASE_DIR.parent.parent.parent / "var"))
DATA_DIR = VAR_DIR / "data"
CERTS_DIR = Path(env.get("VAR_DIR", VAR_DIR / "certs"))


@app.get(root_path+"/openapi.json")
def openapi():
    return app.openapi()


database_url = settings.get("DATABASE_URL") % {"data_dir": str(DATA_DIR)}

print(f"database_url: {database_url}")

engine = create_engine(database_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session




