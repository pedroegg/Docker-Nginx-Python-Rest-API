from typing import List, Optional

from lib.mysql import MySQL
from model.user import User

import lib.errors as errors

def GetAll() -> List[User]:
    query = "SELECT * FROM sushi2go.user"

    try:
        result, _ = MySQL().execute(query)
    except:
        raise

    users: List[User] = []

    for row in result:
        users.append(User(row))

    return users

def GetByID(id: int) -> Optional[User]:
    query = "SELECT * FROM sushi2go.user WHERE id = ?"

    try:
        result, _ = MySQL().execute(query, (id,), True)
    except:
        raise

    if len(result) == 0:
        return None

    return User(result[0])

def GetByUsername(slug: str) -> Optional[User]:
    query = "SELECT * FROM sushi2go.user WHERE username = ?"

    try:
        result, _ = MySQL().execute(query, (slug,), True)
    except:
        raise

    if len(result) == 0:
        return None

    return User(result[0])

def Create(user: User) -> int:
    query = "INSERT INTO sushi2go.user (`username`, `password`) VALUES (?, ?)"

    try:
       _, last_inserted_id = MySQL().execute(query, (user.username, user.password,), usePrepared=True, autoCommit=False)
    except:
        raise

    if last_inserted_id is None:
        try:
            MySQL().rollback()
        except:
            raise errors.InternalError('failed to create user')

        raise errors.InternalError('failed to create user')

    return last_inserted_id
