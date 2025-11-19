from app.repositories import user_repository
from app import models


def test_user_repository_get_or_create(db_session):
    sub = "supabase-123"
    email = "user@example.com"

    #initial: should create
    user1 = user_repository.get_or_create_user_by_supabase_id(
        db=db_session,
        sub=sub,
        email=email,
        role="buyer",
    )
    assert user1.id is not None
    assert user1.supabase_id == sub
    assert user1.email == email
    assert user1.role == models.UserRole.BUYER

    #second call: should reuse existing
    user2 = user_repository.get_or_create_user_by_supabase_id(
        db=db_session,
        sub=sub,
        email=email,
        role="admin",  #should be ignored because the user already exists
    )
    assert user2.id == user1.id
    assert user2.role == models.UserRole.BUYER