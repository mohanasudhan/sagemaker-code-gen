class SageMakerCoreError(Exception):
    """Base class for all exceptions in SageMaker Core"""
    fmt = 'An unspecified error occurred.'

    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        Exception.__init__(self, msg)
        self.kwargs = kwargs

### Generic Validation Errors
class ValidationError(SageMakerCoreError):
    """Raised when a validation error occurs."""
    fmt = "An error occurred while validating user input/setup: {message}"

### Waiter Errors
class WaiterError(SageMakerCoreError):
    """Raised when an error occurs while waiting."""
    fmt = "An error occurred while waiting for {resource_type}. Final Resource State: {status}."

class FailedStatusError(WaiterError):
    """Raised when a resource enters a failed state."""
    fmt = "Encountered unexpected failed state while waiting for {resource_type}. Final Resource State: {status}. Failure Reason: {reason}"

class TimeoutExceededError(WaiterError):
    """Raised when a specified timeout is exceeded"""
    fmt = "Timeout exceeded while waiting for {resource_type}. Final Resource State: {status}. Increase the timeout and try again."
 
### Intelligent Defaults Errors
class IntelligentDefaultsError(SageMakerCoreError):
    """Raised when an error occurs in the Intelligent Defaults"""
    fmt = "An error occurred while loading Intelligent Defaults: {message}"

class LocalConfigNotFoundError(IntelligentDefaultsError):
    """Raised when a configuration file is not found in local file system"""
    fmt = "Failed to load configuration file from location: {file_path}. {debug_message}"
    pass

class S3ConfigNotFoundError(IntelligentDefaultsError):
    """Raised when a configuration file is not found in S3"""
    fmt = "Failed to load configuration file from S3 location: {s3_uri}. {debug_message}"

class ConfigSchemaValidationError(IntelligentDefaultsError, ValidationError):
    """Raised when a configuration file does not adhere to the schema"""
    fmt = "Failed to validate configuration file from location: {file_path}. {debug_message}"