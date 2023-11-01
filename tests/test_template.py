
from dbconfig import db_session, db_engine, open_db_uri
from edutap.passdata_apple.model import PassTemplate

def test_template(db_session):
    
    template = PassTemplate(
        # id=2
        # template_id="test",
    #     backoffice_id="test",
    #     title="Test",
    #     description="Test template",
    #     creator="Test",
    #     email="donald@duck.com",
    )
        

    db_session.add(template)
    db_session.commit()
    # db_session.refresh(template)
    # assert template.id is not None