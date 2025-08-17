from fastapi import Depends, HTTPException, status
from .security import get_current_user

def require_roles(*allowed):
    def wrapper(user=Depends(get_current_user)):
        names = {r.name for r in user.roles}
        if not names.intersection(set(allowed)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return wrapper
