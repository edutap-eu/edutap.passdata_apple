import os

from sqlalchemy.exc import IntegrityError
from edutap.models_apple.models import Pass
import pytest
from dbconfig import (
    db_session,
    db_engine,
    open_db_uri,
    passes,
    passtype_identifier,
    team_identifier,
    certfile,
    keyfile,
    wwdrfile,
    keyfile,
    certfile,
)

from edutap.passdata_apple.model import PassTemplate, IssuedPass
from edutap.models_apple import template


def test_template(db_session):
    template = PassTemplate(
        template_identifier="test",
        backoffice_identifier="test",
        title="Test",
        description="Test template",
        creator="Test",
        email="donald@duck.com",
        pass_type="storeCard",
        pass_json={"test": "test"},
    )

    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    assert template.id is not None


@pytest.fixture
def imported_template(db_session):
    """
    fixture to prepare a template from a passfile.
    it is a storeCard passfile, so the pass_type should be "storeCard"
    """
    with open(passes / "StoreCard.pkpass", "rb") as f:
        t = PassTemplate.from_passfile(f, template_identifier="test", backoffice_identifier="test")
        db_session.add(t)
        db_session.commit()
        db_session.refresh(t)
        id0 = t.id
        _id = id(t)
        del t

        # check if template is stored in db

        t1 = db_session.get(PassTemplate, id0)
        assert t1 is not None
        assert id(t1) != _id

        return t1


def test_imported_template(imported_template):
    assert imported_template is not None
    assert imported_template.pass_type == "storeCard"

    assert imported_template.attachments is not None
    assert imported_template.get_attachment("icon.png").__class__ == bytes

    names = set(["icon.png", "icon@2x.png", "logo.png", "strip.png", "strip@2x.png"])

    assert set(imported_template.attachment_filenames) == names


# @pytest.mark.integration


@pytest.fixture
def created_pass_object(imported_template: PassTemplate):
    pass_ = imported_template.create_pass_object(
        passtype_identifier=passtype_identifier,
        team_identifier=team_identifier,
        # paths in the first param are relative to the root of the pass.json
        pass_patches=[
            {
                "path": "/barcodes/0/message",
                "op": "replace",
                "value": "new barcode message",
            },

        ],
        # the path below is relative to the "storeCard" object in the pass.json
        passinfo_patches=[
            {
                "path": "/primaryFields/0/changeMessage",
                "op": "replace",
                "value": "new msg",
            }
        ],
    )
    
    return pass_, imported_template


@pytest.mark.integration
def test_show_pass(created_pass_object, tmp_path):
    pass_, template = created_pass_object
    filename = tmp_path / "test.pkpass"

    pkpass = pass_.create(
        certfile,
        keyfile,
        wwdrfile,
        "",
    )

    with open(filename, "wb") as f:
        f.write(pkpass.getvalue())

    assert filename.exists()
    os.system("open " + str(filename))
    
    
def test_create_pass_object_and_store_lowlevel(created_pass_object: Pass, db_session):
    """
    creates an issued pass object for the given pass object and stores it in the database.
    doing it by hand, without using the relation
    """
    pass_, template = created_pass_object
    issued_pass = IssuedPass(
        passtype_identifier=pass_.passTypeIdentifier,
        template_id=template.id,
        template_identifier=template.template_identifier,
        serial_number=pass_.serialNumber,
        backoffice_identifier="test",
        source="test",
        record_identifier="test",
    )
    
    db_session.add(issued_pass)
    db_session.commit()
    db_session.refresh(issued_pass)
    
    del issued_pass
    
    # check that the pass is stored in the database
    issued_pass = db_session.query(IssuedPass).filter(
        IssuedPass.serial_number == pass_.serialNumber,
        IssuedPass.passtype_identifier == pass_.passTypeIdentifier,
    ).one()
    
    assert issued_pass.template_id == template.id
    assert issued_pass in template.issued_passes
    
    # check that the unique constraint for (passtype_identifier, serial_number) is enforced
    issued_pass1 = IssuedPass(
        passtype_identifier=pass_.passTypeIdentifier,
        serial_number=pass_.serialNumber,
        backoffice_id="test",
        source="test",
        record_id="test",
    )
    with pytest.raises(IntegrityError) as ex:
        # passtype_identifier and serial_number must be unique
        db_session.add(issued_pass1)
        db_session.commit()

        
    return issued_pass


def test_create_pass_object_and_store_via_relation(created_pass_object: tuple[Pass, PassTemplate], db_session):
    pass_, template = created_pass_object
    issued_pass = IssuedPass(
        template_id=template.id,
        template_identifier=template.template_identifier,
        passtype_identifier=pass_.passTypeIdentifier,
        serial_number=pass_.serialNumber,
        backoffice_identifier="test",
        source="test",
        record_identifier="test",
    )
    template.issued_passes.append(issued_pass)
    
    db_session.commit()
    del issued_pass
    
    # check that the pass is stored in the database
    issued_pass = db_session.query(IssuedPass).filter(
        IssuedPass.serial_number == pass_.serialNumber,
        IssuedPass.passtype_identifier == pass_.passTypeIdentifier,
    ).one()
    
    assert issued_pass.template_id == template.id
    assert issued_pass in template.issued_passes
    
    return issued_pass


def test_create_pass_object_and_store(imported_template: PassTemplate, db_session):
    pass_ = imported_template.create_and_store_pass_object(
        passtype_identifier=passtype_identifier,
        source="VZD",
        record_identifier="123",
    )
    sn = pass_.serial_number
    template_identifier = imported_template.template_identifier
    
    db_session.commit()
    
    # now search for the issued pass
    
    issued_pass = db_session.query(IssuedPass)\
        .filter(
            IssuedPass.serial_number == sn, 
            IssuedPass.template_identifier==template_identifier
        ).one()
        
    print(issued_pass.serial_number)
    
        