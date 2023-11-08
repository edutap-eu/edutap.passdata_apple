import os
import pathlib
import pytest

import sqlmodel

from edutap.passdata_apple.model import init_model

vardir = pathlib.Path("var")
certsdir = vardir / "certs"
keyfile = certsdir / "private.key"
wwdrfile = certsdir / "wwdr_certificate.pem"

rootdir = pathlib.Path(__file__)
datadir = rootdir.parent / "data"
dbfile = datadir / "test.db"
certfile = certsdir / "certificate.pem"

passes = datadir / "passes"


databases = os.environ.get("TEST_DATABASES", "sqlite").split(",")
passtype_identifier = os.environ.get("APPLE_PASSTYPE_IDENTIFIER")
team_identifier = os.environ.get("APPLE_TEAM_IDENTIFIER")


def open_db_uri(dialect):
    if dialect == 'sqlite':
        # delete the database file if it exists
        if dbfile.exists():
            dbfile.unlink()
            
        return f"sqlite:///{dbfile}"
    elif dialect == 'postgresql':
        os.system("dropdb edutaptest; createdb edutaptest")
        return 'postgresql:///edutaptest'


@pytest.fixture(scope='function', params=databases)
def db_engine(request):
    print(f"request.param: {request.param}")
    url = open_db_uri(request.param)
    engine = sqlmodel.create_engine(url, echo=True)
    init_model(engine)
    yield engine
    engine.dispose()
    
    

@pytest.fixture
def db_session(db_engine):
    with sqlmodel.Session(db_engine) as session:
        yield session
        session.close()
        
        
