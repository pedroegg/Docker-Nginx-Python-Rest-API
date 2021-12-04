import werkzeug.exceptions as errors

class InternalError(errors.InternalServerError):
    name = 'INTERNAL_ERROR'

    def __init__(self, message: str):
        super().__init__(description=message)

class BadRequest(errors.BadRequest):
    name = 'BAD_REQUEST'

    def __init__(self, message: str):
        super().__init__(description=message)

class NotFound(errors.NotFound):
    name = 'NOT_FOUND'
    
    def __init__(self, message: str):
        super().__init__(description=message)

class Conflict(errors.Conflict):
    name = 'CONFLICT'

    def __init__(self, message: str):
        super().__init__(description=message)

class Unauthorized(errors.Unauthorized):
    name = 'UNAUTHORIZED'

    def __init__(self, message: str):
        super().__init__(description=message)

class Forbidden(errors.Forbidden):
    name = 'FORBIDDEN'

    def __init__(self, message: str):
        super().__init__(description=message)

class FoodNotFound(NotFound):
    def __init__(self, field: str, value):
        super().__init__(message='food with {} "{}" was not found'.format(field, value))

class FoodOutOfStock(BadRequest):
    def __init__(self, field: str, value):
        super().__init__(message='food with {} "{}" is out of stock'.format(field, value))

class OrderNotFound(NotFound):
    def __init__(self, field: str, value):
        super().__init__(message='order with {} "{}" was not found'.format(field, value))

class FailedUploadFile(InternalError):
    #name = 'FAILED_UPLOAD_FILE'
    def __init__(self):
        super().__init__(message='failed to upload image. this could be due to invalid file or temporary error. please, try again if you think that it is not an invalid file')

class UserAlreadyExists(Conflict):
    def __init__(self):
        super().__init__(message='user with this name already exists. please, try another username')

class UserNotFound(NotFound):
    def __init__(self):
        super().__init__(message='user not found')

class IncorrectPassword(BadRequest):
    def __init__(self):
        super().__init__(message='incorrect password')

class AlreadyLoggedIn(BadRequest):
    def __init__(self):
        super().__init__(message='you are already logged in')

class NotLoggedIn(Unauthorized):
    def __init__(self):
        super().__init__(message='you are not logged in')

class NotAdmin(Forbidden):
    def __init__(self):
        super().__init__(message='you are not an admin')

class InvalidJWT(Unauthorized):
    def __init__(self):
        super().__init__(message='invalid jwt token')
