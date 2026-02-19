from collections.abc import Callable

from fastapi import Depends

from app.core.constants import UserRole
from app.core.exceptions import ForbiddenError


def require_role(*roles: UserRole) -> Callable:
    """Dependency factory that checks the current user has one of the given roles."""

    async def _check_role(current_user=Depends(lambda: None)):
        # This will be wired up properly in dependencies.py once we have get_current_user
        if current_user.role not in [r.value for r in roles]:
            raise ForbiddenError(f"Role must be one of: {', '.join(r.value for r in roles)}")
        return current_user

    return _check_role
