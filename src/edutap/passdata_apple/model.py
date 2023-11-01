import pydantic
import sqlmodel
# from edutap.models_apple import models as apple_models
# from edutap.models_apple import template
import uuid as uuid_lib

class PassTemplate(sqlmodel.SQLModel, table=True):
    id: uuid_lib.UUID = sqlmodel.Field(primary_key=True, default_factory=uuid_lib.uuid4)


def init_model(engine):
    sqlmodel.SQLModel.metadata.create_all(engine)