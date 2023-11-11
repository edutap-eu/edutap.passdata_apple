from typing import Generator
import pytest
import httpx
import pytest_asyncio

from edutap.passdata_apple.main import app
from edutap.passdata_apple.common import VAR_DIR, DATA_DIR, CERTS_DIR, BASE_DIR, engine
import dbconfig
from edutap.passdata_apple.model import init_model

PORT = 4780
HOST = "localhost"
PASSES_DIR = DATA_DIR / "passes"


@pytest_asyncio.fixture
async def async_webclient() -> Generator:
    # have to call init_model here because via httpx.AsyncClient, the lifecycle of the app is not called
    init_model(engine)
    async with httpx.AsyncClient(app=app, base_url="http://0.0.0.0") as client:
        yield client


@pytest.mark.asyncio
async def test_test(async_webclient):
    response = await async_webclient.get("")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


@pytest.mark.asyncio
async def test_protected(async_webclient):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer akljnv13bvi2vfo0b0bw",
    }

    response = await async_webclient.post(
        "/protected",
        params=dict(name="xxx"),
        headers=headers,
    )
    assert response.status_code == 200
        # assert xresponse.json() == {"data": "You used a valid API key."}


@pytest.mark.asyncio
async def test_fileupload(async_webclient):
    headers = {
        "Authorization": "Bearer akljnv13bvi2vfo0b0bw",
    }

    storecard_file = dbconfig.passes / "StoreCard.pkpass"
    with open(storecard_file, "rb") as storecard:
        response = await async_webclient.post(
            "/upload_pass_template",
            headers=headers,
            params=dict(template_identifier="t1"),
            files=dict(pkpass=storecard),
        )
        assert response.status_code == 200
        # assert xresponse.json() == {"data": "You used a valid API key."}
