from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.auth import decode_access_token

security = HTTPBearer()

async def verify_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = decode_access_token(credentials.credentials)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    request.state.user_id = payload["user_id"]
    request.state.role = payload.get("role")
    return payload


async def verify_student(payload: dict = Depends(verify_token)):
    if payload.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students only")
    return payload


async def verify_professor(payload: dict = Depends(verify_token)):
    if payload.get("role") != "professor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Professors only")
    return payload