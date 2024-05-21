class SageMakerCoreError(Exception):
    """Base class for all exceptions in SageMaker Core"""
    fmt = 'An unspecified error occurred.'

    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        Exception.__init__(self, msg)
        self.kwargs = kwargs

### Waiter Exceptions
class WaiterError(SageMakerCoreError):
    """Raised when an error occurs while waiting."""
    fmt = "An error occurred while waiting for {resource_type}. Final Resource State: {status}."

class FailedStatusError(WaiterError):
    """Raised when a resource enters a failed state."""
    fmt = "Encountered unexpected failed state while waiting for {resource_type}. Final Resource State: {status}."

class TimeoutExceededError(WaiterError):
    """Raised when a specified timeout is exceeded"""
    fmt = "Timeout exceeded while waiting for {resource_type}. Final Resource State: {status}. Increase the timeout and try again."