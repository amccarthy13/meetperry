class InvalidEventStatusException(Exception):

    status_code = 400
    description = "Invalid event status"

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)

class DuplicateTaskCreationException(Exception):

    status_code = 409
    description = "Duplicate task creation"

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)

class TaskNotFoundException(Exception):

    status_code = 400
    description = "Invalid event status"

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)

class TaskInvalidStatusException(Exception):

    status_code = 400
    description = "Invalid task status"

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)