from factories.machines import create_machine, machine_payload
from factories.users import auth_headers_by_role
from assertions import assert_status_code

def test_get_machine_failure(client, db_session):
    """
    Tests machine endpoint failures for future provider/admin access needs
    """
    machine = create_machine(client, db_session, "provider")
    machine_id = 42
    resp = client.get(f"/api/v1/machines/{machine_id}/")
    assert_status_code(resp, 404)