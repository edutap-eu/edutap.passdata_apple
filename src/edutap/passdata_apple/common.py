
import asyncio
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
import fastapi_chameleon
from sqlmodel import Session, create_engine

from edutap.passdata_apple.model import init_model

print(os.environ)

env = settings = os.environ


FORCE_HTTPS = settings.get("FORCE_HTTPS", True) 
if FORCE_HTTPS == 'false':
    FORCE_HTTPS = False

root_path = ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    application startup and shutdown
    """
    # wait until the database is available
    while True:
        try:
            engine.connect()
            break
        except Exception as e:
            print("Error connecting to database:")
            print(e)
            await asyncio.sleep(1)

    init_model(engine)
    print("startup")
    yield
    print("shutdown")
    
app = FastAPI(
    docs_url=root_path+"/docs", 
    openapi_prefix=root_path,
    version="0.1.6.3",
    root_path="",
    lifespan=lifespan,
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


