from factories.users import create_user_by_role, auth_headers_by_role
from test_config import TestConfig

def machine_payload(**overrides):
    #Removed provider_user_id from base (comes from auth context)
    base = {
        "name": TestConfig.DEFAULT_MACHINE_NAME,
        "cpu": "4 vCPU",
        "ram": "16 GB", 
        "storage": "200 GB",
    }
    base.update(overrides)
    return base


# def create_machine(client, db_session, provider_role="provider", **overrides):
#     #Create provider user using config
#     provider = create_user_by_role(db_session, provider_role)
    
#     payload = machine_payload(**overrides)

#     resp = client.post(
#         "/api/v1/machines/",
#         json=payload,
#         headers=auth_headers_by_role(provider_role),  #Use config-based headers
#     )
#     assert resp.status_code == 201
#     return resp.json()


def machine_payload(provider_id, **overrides):
    base = {
        "hostname": TestConfig.DEFAULT_MACHINE_HOSTNAME,  # ACTUAL VALUE, not string
        "location_region": TestConfig.DEFAULT_MACHINE_REGION,  # ACTUAL VALUE
        "gpu_model": TestConfig.DEFAULT_MACHINE_GPU_MODEL,  # ACTUAL VALUE
        "gpu_count": TestConfig.DEFAULT_MACHINE_GPU_COUNT,  # ACTUAL VALUE
        "cpu_model": TestConfig.DEFAULT_MACHINE_CPU_MODEL,  # ACTUAL VALUE
        "cpu_cores": TestConfig.DEFAULT_MACHINE_CPU_CORES,  # ACTUAL VALUE
        "ram_gb": TestConfig.DEFAULT_MACHINE_RAM_GB,  # ACTUAL VALUE
        "storage_gb": TestConfig.DEFAULT_MACHINE_STORAGE_GB,  # ACTUAL VALUE
        "network_mbps": TestConfig.DEFAULT_MACHINE_NETWORK_MBPS,  # ACTUAL VALUE
        "provider_id": str(provider_id),
    }
    base.update(overrides)
    return base


def create_machine(client, db_session, provider_role="provider", **overrides):
    """
    Create machine using config-based provider
    """
    provider_user = create_user_by_role(db_session, provider_role)
    
    # Ensure provider has a verified profile
    from app.providers.models import ProviderProfile, ProviderVerificationStatus
    profile = db_session.query(ProviderProfile).filter(ProviderProfile.user_id == provider_user.id).first()
    if not profile:
        profile = ProviderProfile(
            user_id=provider_user.id,
            verification_status=ProviderVerificationStatus.VERIFIED,
            payout_account_ref="test_payout_ref"
        )
        db_session.add(profile)
    else:
        profile.verification_status = ProviderVerificationStatus.VERIFIED
    db_session.commit()
    
    # The provider_id will be converted to string in machine_payload
    payload = machine_payload(provider_id=provider_user.id, **overrides)
    
    # Debug: print the final payload to verify all UUIDs are strings
    print(f"Machine payload: {payload}")
    
    resp = client.post(
        "/api/v1/machines/",
        json=payload,
        headers=auth_headers_by_role(provider_role),
    )
    assert resp.status_code == 201
    return resp.json()


def valid_machine_payload(**overrides):
    """Return a valid machine payload for testing."""
    return machine_payload(**overrides)