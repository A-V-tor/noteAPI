from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.tools import check_token


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(
                    status_code=403, detail='Invalid authentication scheme.'
                )
            payload = check_token(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=403, detail='Invalid token or expired token.'
                )
            request.state.payload = payload
            return payload
        else:
            raise HTTPException(
                status_code=403, detail='Invalid authorization code.'
            )
