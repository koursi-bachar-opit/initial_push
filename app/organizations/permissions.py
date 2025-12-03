from fastapi import HTTPException, status
from uuid import UUID

class OrgPermission:
    @staticmethod
    def require_admin(membership):
        if membership is None or membership.org_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization admin permission required",
            )
        
    @staticmethod
    def require_member(membership):
        if membership is None or membership.org_role != "member":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization membership required",
            )

#-----------------------------------------------------------------------------------------------
        
# from fastapi import Depends, HTTPException, status
# from app.auth.auth import get_current_user
# from app.organizations.public import OrganizationsPublic, get_organizations_public

# def require_org_member_or_admin(
#     org_id: UUID,
#     current_user=Depends(get_current_user),
#     orgs_public: OrganizationsPublic = Depends(get_organizations_public),
# ):
#     if not orgs_public.is_org_member(current_user.id, org_id):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this organization.",
#         )
#     return True