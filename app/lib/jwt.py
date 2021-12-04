import jwt
import os
import lib.errors as errors
from typing import Optional

def Encode(id: int, username: str, isAdmin: bool) -> str:
    payload = {
        'id': id,
        'username': username,
        'isAdmin': isAdmin,
    }
    
    try:
        jwt_encoded = jwt.encode(payload, os.getenv('SECRET_KEY_JWT'), algorithm='HS256')
    except:
        raise

    return jwt_encoded

def Decode(jwt_encoded: str) -> dict:
    if jwt_encoded is None or jwt_encoded == '':
        raise errors.InvalidJWT()
    
    try:
        jwt_decoded = jwt.decode(jwt_encoded, os.getenv('SECRET_KEY_JWT'), algorithms='HS256')
    except jwt.exceptions.InvalidTokenError:
        raise errors.InvalidJWT()
    except:
        raise

    return jwt_decoded

def IsValid(jwt_encoded: Optional[str]) -> bool:
    if jwt_encoded is None or jwt_encoded == '':
        return False
    
    try:
        Decode(jwt_encoded)
    except errors.InvalidJWT:
        return False
    
    return True
