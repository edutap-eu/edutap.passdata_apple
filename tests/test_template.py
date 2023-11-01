
from dbconfig import db_session, db_engine, open_db_uri
from edutap.passdata_apple.model import PassTemplate

def test_template(db_session):
    
    template = PassTemplate(
        template_id="test",
        backoffice_id="test",
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