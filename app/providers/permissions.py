# from fastapi import Depends, HTTPException

# from app.auth.auth import get_current_user
# from app.auth.public import AuthPublic, get_auth_public

# from .public import ProvidersPublic, get_providers_public


# def require_provider_profile(
#     current_user = Depends(get_current_user),
#     providers: ProvidersPublic = Depends(get_providers_public),
# ):
#     profile = providers.get_profile_by_user(current_user.id)
#     if not profile:
#         raise HTTPException(403, "User does not have a provider profile.")
#     return current_user


# def require_verified_provider(
#     current_user = Depends(get_current_user),
#     providers: ProvidersPublic = Depends(get_providers_public),
# ):
#     profile = providers.get_profile_by_user(current_user.id)
#     if not profile:
#         raise HTTPException(403, "User does not have a provider profile.")
#     if profile.verification_status != "verified":
#         raise HTTPException(403, "Provider is not verified.")
#     return current_user


# def require_provider_role(
#     current_user = Depends(get_current_user),
#     auth_public: AuthPublic = Depends(get_auth_public),
# ):
#     auth_public.ensure_provider(current_user.id)
#     return current_user


# def require_admin_for_provider_actions(
#     current_user = Depends(get_current_user),
#     auth_public: AuthPublic = Depends(get_auth_public),
# ):
#     auth_public.ensure_admin(current_user.id)
#     return current_user