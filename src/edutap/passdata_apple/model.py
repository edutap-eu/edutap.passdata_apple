from datetime import datetime
from typing import Any
import pydantic
import sqlmodel
from edutap.models_apple import models as apple_models
from edutap.models_apple import template
import uuid as uuid_lib


class PassTemplate(sqlmodel.SQLModel, template.PassTemplateBase, table=True):
    id: uuid_lib.UUID = sqlmodel.Field(primary_key=True, default_factory=uuid_lib.uuid4)
    pass_json: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    attachments: dict[str, bytes] = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON)) # TODO: define attachment structure model for sqlalchemy
    timestamp: datetime = sqlmodel.Field(default_factory=datetime.now)

    


def init_model(engine):
    sqlmodel.SQLModel.metadata.create_all(engine)