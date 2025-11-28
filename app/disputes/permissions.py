# from uuid import UUID
# from app.users.models import User, UserRole
# from app.disputes.models import Dispute


"""
This module is intentionally minimal for now. Most dispute logic
is ownership-based and enforced in DisputeService using
BookingsPublic -> booking/listing/machine relationships.
"""

#def is_admin(user: User) -> bool:
#    return user.role == UserRole.ADMIN


# def can_view_dispute(user: User, dispute: Dispute) -> bool:
#     """
#     Currently, viewing enforcement is handled implicitly at service level.

#     This helper exists for:
#     - future admin dashboards
#     - provider/buyer dispute detail restrictions
#     - organization-based escalation view rules
#     """
#     if is_admin(user):
#         return True

#     # Buyer who opened the dispute
#     if dispute.opened_by_user_id == user.id:
#         return True

#     # Provider ownership validation is enforced in the service layer
#     # This helper can be expanded once provider role checks move here.
#     return False

"""
#consider: to add:
- providers_can_respond_to_disputes()
- organization_admin_can_view_disputes()
- compliance_team_can_access_dispute_evidence()
- platform_auditor_can_view_dispute_logs()
"""