
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import logging
import os

from boto3.session import Session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_logger(log_level=None):
    """Reset the logging configuration based on log level.

    Usage:
        Set Environment Variable LOG_LEVEL to DEBUG to see debug logs
        reset_logger()
        reset_logger("DEBUG")

    Args:
        log_level (str): The log level to set.
            Accepted values are: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".

    Raises:
        AttributeError: If the log level is invalid.
    """
    if not log_level:
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    _logger = logging.getLogger()
    _logger.setLevel(getattr(logging, log_level))
    # reset any currently associated handlers with log level
    for handler in _logger.handlers:
        _logger.removeHandler(handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    _logger.addHandler(console_handler)


def snake_to_pascal(snake_str):
    """
    Convert a snake_case string to PascalCase.

    Args:
        snake_str (str): The snake_case string to be converted.

    Returns:
        str: The PascalCase string.

    """
    components = snake_str.split('_')
    return ''.join(x.title() for x in components[0:])



def pascal_to_snake(pascal_str):
    """
    Converts a PascalCase string to snake_case.

    Args:
        pascal_str (str): The PascalCase string to be converted.

    Returns:
        str: The converted snake_case string.
    """
    return ''.join(['_' + i.lower() if i.isupper() else i for i in pascal_str]).lstrip('_')


class Unassigned:
    """A custom type used to signify an undefined optional argument."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class SingletonMeta(type):
    """
    Singleton metaclass. Ensures that a single instance of a class using this metaclass is created.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Overrides the call method to return an existing instance of the class if it exists,
        or create a new one if it doesn't.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SageMakerClient(metaclass=SingletonMeta):
    """
    A singleton class for creating a SageMaker client.
    """
    def __init__(self, session: Session = None, region_name: str = None, service_name='sagemaker'):
        """
        Initializes the SageMakerClient with a boto3 session, region name, and service name.
        Creates a boto3 client using the provided session, region, and service.
        """
        if session is None:
            logger.warning("No boto3 session provided. Creating a new session.")
            session = Session()

        if region_name is None:
            logger.warning("No region provided. Using default region.")
            region_name = session.region_name

        self.session = session
        self.region_name = region_name
        self.service_name = service_name
        self.client = session.client(service_name, region_name)


