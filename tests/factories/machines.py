from factories.users import create_user_by_role, auth_headers_by_role
from test_config import TestConfig

def machine_payload(**overrides):
    #Removed provider_user_id from base (it comes from auth context)
    base = {
        "name": TestConfig.DEFAULT_MACHINE_NAME,
        "cpu": "4 vCPU",
        "ram": "16 GB", 
        "storage": "200 GB",
    }
    base.update(overrides)
    return base


def create_machine(client, db_session, provider_role="provider", **overrides):
    #Create provider user using config
    provider = create_user_by_role(db_session, provider_role)
    
    payload = machine_payload(**overrides)

    resp = client.post(
        "/api/v1/machines/",
        json=payload,
        headers=auth_headers_by_role(provider_role),  #Use config-based headers
    )
    assert resp.status_code == 201
    return resp.json()


def valid_machine_payload(**overrides):
    """Return a valid machine payload for testing."""
    return machine_payload(**overrides)