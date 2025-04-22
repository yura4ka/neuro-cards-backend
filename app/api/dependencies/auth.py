from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.services import auth_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login/")


async def require_auth(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        decoded = auth_service.decode_access_token(token=token)
        return decoded.id
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=401,
            detail=[{"msg": "Could not validate token credentials."}],
            headers={"WWW-Authenticate": "Bearer"},
        )


RequireAuthDependency = Annotated[str, Depends(require_auth)]
