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