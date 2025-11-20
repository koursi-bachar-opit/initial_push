from factories.users import auth_headers_by_role
from assertions import assert_status_code

def test_get_nonexistent_machine_returns_404(client, db_session):
    """
    Getting a non-existent machine returns a 404 error.
    """
    resp = client.get(
        "/api/v1/machines/999999/",  #This machine ID doesn't exist
        headers=auth_headers_by_role("provider")
    )
    assert_status_code(resp, 404)