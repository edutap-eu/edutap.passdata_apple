from datetime import datetime
from typing import Any
import pydantic
from sqlalchemy import Sequence, UniqueConstraint
import sqlmodel
from edutap.models_apple import models as apple_models
from edutap.models_apple import template
import uuid as uuid_lib


class PassTemplate(sqlmodel.SQLModel, template.PassTemplateBase, table=True):
    id: uuid_lib.UUID = sqlmodel.Field(primary_key=True, default_factory=uuid_lib.uuid4)
    pass_json: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    attachments: dict[str, str] = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON)) # TODO: define attachment structure model for sqlalchemy
    timestamp: datetime = sqlmodel.Field(default_factory=datetime.now)
    issued_passes: list["IssuedPass"] = sqlmodel.Relationship(back_populates="template")
    
    def create_and_store_pass_object(
        self,
        *,
        serial_number: str|None=None,
        source: str|None=None,
        record_identifier: str|None=None,
        passtype_identifier: str|None=None,
        team_identifier: str|None=None,
        pass_patches: list[dict[str, Any]]=[],
        passinfo_patches: list[dict[str, Any]] = [],
    ) -> apple_models.Pass:
        
        pass_ = self.create_pass_object(
            serial_number=serial_number,
            passtype_identifier=passtype_identifier,
            team_identifier=team_identifier,
            # source=source,
            pass_patches=pass_patches,
            passinfo_patches=passinfo_patches,  
        )
        
        res = IssuedPass(
            template_id=self.id,
            template_identifier=self.template_identifier,
            passtype_identifier=pass_.passTypeIdentifier,
            serial_number=pass_.serialNumber,
            backoffice_identifier=self.backoffice_identifier,
            source=source,
            record_identifier=record_identifier,
        )
        
        self.issued_passes.append(res)
        return res


class IssuedPass(sqlmodel.SQLModel, table=True):
    """
    defines information about a pass that has been issued to a user,
    does not contain personal information per se, but references,
    so that the pass can be reissued if necessary
    """
    id: uuid_lib.UUID = sqlmodel.Field(primary_key=True, default_factory=uuid_lib.uuid4)
    template_id: uuid_lib.UUID = sqlmodel.Field(default=None, foreign_key="passtemplate.id")
    """foreign key to the template that was used to create this pass"""
    template_identifier: str
    """human readable identification for the template"""
    passtype_identifier: str = sqlmodel.Field(sa_column=sqlmodel.Column(sqlmodel.String))
    """the passtype identfier as defined in the Apple Developer Portal"""
    serial_number: str
    """
    the serial number of the pass.
    the combination of passtype_identifier and serial_number must be unique
    by default serial numbers will be incremented numerically
    """
    backoffice_identifier: str
    """defines the backoffice, for example 'LMU'"""
    source: str
    """defines the source, for example 'VZD'"""
    record_identifier: str
    """string representation that defines the record in the source, to be interpreted by the client of this API"""
    template: PassTemplate = sqlmodel.Relationship(back_populates="issued_passes")
    __table_args__ = (UniqueConstraint("passtype_identifier", "serial_number"),)


def init_model(engine):
    sqlmodel.SQLModel.metadata.create_all(engine)