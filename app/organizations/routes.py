from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.auth.auth import get_current_user
from app.users.models import User  #until users domain migration

from .service import OrganizationService, get_organization_service
from .schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationRead,
    MembershipCreate,
    MembershipRead,
    MembershipUpdateRole,
)

router = APIRouter()


#Organization CRUD
@router.post("/", response_model=OrganizationRead, status_code=201)
def create_organization(
    payload: OrganizationCreate,
    user: User = Depends(get_current_user),
    service: OrganizationService = Depends(get_organization_service),
):
    """
    Any authenticated user may create an organization.
    They automatically become the first admin.
    """
    return service.create_organization(user.id, payload)


@router.get("/mine", response_model=list[OrganizationRead])
def list_my_organizations(
    user: User = Depends(get_current_user),
    service: OrganizationService = Depends(get_organization_service),
):
    """
    List all organizations the authenticated user belongs to.
    """
    return service.list_user_organizations(user.id)


@router.patch("/{org_id:uuid}", response_model=OrganizationRead)
def update_organization(
    org_id: UUID,
    payload: OrganizationUpdate,
    user: User = Depends(get_current_user),
    service: OrganizationService = Depends(get_organization_service),
):
    """
    Only organization admins may update the org.
    """
    try:
        return service.update_organization(org_id, user.id, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


#Membership management
@router.get("/{org_id:uuid}/members", response_model=list[MembershipRead])
def list_members(
    org_id: UUID,
    user: User = Depends(get_current_user),
    service: OrganizationService = Depends(get_organization_service),
):
    """
    Only organization members may view membership lists.
    """
    try:
        return service.list_members(org_id, user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post("/{org_id:uuid}/members", response_model=MembershipRead, status_code=201)
def add_member(
    org_id: UUID,
    payload: MembershipCreate,
    user: User = Depends(get_current_user),
    service: OrganizationService = Depends(get_organization_service),
):
    """
    Only organization admins may add new members.
    """
    try:
        return service.add_member(org_id, user.id, payload.user_id, payload.role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.patch("/{org_id:uuid}/members/{user_id:uuid}", response_model=MembershipRead)
def update_member_role(
    org_id: UUID,
    user_id: UUID,
    payload: MembershipUpdateRole,
    user: User = Depends(get_current_user),
    service: OrganizationService = Depends(get_organization_service),
):
    """
    Only admins may change roles.
    """
    try:
        return service.change_member_role(org_id, user.id, user_id, payload.role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.delete("/{org_id:uuid}/members/{user_id:uuid}", status_code=204)
def remove_member(
    org_id: UUID,
    user_id: UUID,
    user: User = Depends(get_current_user),
    service: OrganizationService = Depends(get_organization_service),
):
    """
    Only admin can remove a member.
    """
    try:
        service.remove_member(org_id, user.id, user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return None