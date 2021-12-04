import lib.jwt as jwt
import lib.errors as errors

admins = {
    1: True
}

def IsAdminByUserID(user_id: int) -> bool:
    if user_id in admins:
        return True

    return False

def IsAdminByCookie(cookie: str) -> bool:
    try:
        jwt_decoded = jwt.Decode(cookie)
    except errors.InvalidJWT:
        return False
    except:
        raise

    if jwt_decoded['isAdmin'] and jwt_decoded['id'] in admins:
        return True

    return False