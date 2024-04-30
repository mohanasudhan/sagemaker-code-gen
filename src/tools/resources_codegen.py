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
"""Generates the resource classes for the service model."""
import json
import os
import logging

from constants import BASIC_JSON_TYPES_TO_PYTHON_TYPES, \
                        GENERATED_CLASSES_LOCATION, \
                        RESOURCES_CODEGEN_FILE_NAME, \
                        LICENCES_STRING
from src.util.util import add_indent, convert_to_snake_case
from resources_extractor import ResourcesExtractor
from shapes_extractor import ShapesExtractor
from templates import CREATE_METHOD_TEMPLATE, GET_METHOD_TEMPLATE

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ResourcesCodeGen():
    """
    A class for generating resources based on a service JSON file.

    Args:
        file_path (str): The path to the service JSON file.

    Attributes:
        version (str): The API version of the service.
        protocol (str): The protocol used by the service.
        service (str): The full name of the service.
        service_id (str): The ID of the service.
        uid (str): The unique identifier of the service.
        operations (dict): The operations supported by the service.
        shapes (dict): The shapes used by the service.
        resources_extractor (ResourcesExtractor): An instance of the ResourcesExtractor class.
        resources_plan (DataFrame): The resource plan in dataframe format.
        shapes_extractor (ShapesExtractor): An instance of the ShapesExtractor class.

    Raises:
        Exception: If the service ID is not supported or the protocol is not supported.

    """

    def __init__(self, file_path):
        # Load the service JSON file
        with open(file_path, 'r') as file:
            self.service_json = json.load(file)

        # Extract the metadata
        metadata = self.service_json['metadata']
        self.version = metadata['apiVersion']
        self.protocol = metadata['protocol']
        self.service = metadata['serviceFullName']
        self.service_id = metadata['serviceId']
        self.uid = metadata['uid']

        # Check if the service ID and protocol are supported
        if self.service_id != 'SageMaker':
            raise Exception(f"ServiceId {self.service_id} not supported in this resource generator")
        if self.protocol != 'json':
            raise Exception(f"Protocol {self.protocol} not supported in this resource generator")

        # Extract the operations and shapes
        self.operations = self.service_json['operations']
        self.shapes = self.service_json['shapes']

        # Initialize the resources and shapes extractors
        self.resources_extractor = ResourcesExtractor(self.service_json)
        self.shapes_extractor = ShapesExtractor(self.service_json)

        # Extract the resources plan and shapes DAG
        self.resources_plan = self.resources_extractor.get_resource_plan()
        self.shape_dag = self.shapes_extractor.get_shapes_dag()

        # Generate the resources
        self.generate_resources()

    def generate_license(self) -> str:
        """
        Generate the license for the generated resources file.

        Returns:
            str: The license.

        """
        return LICENCES_STRING
    
    def generate_imports(self) -> str:
        """
        Generate the import statements for the generated resources file.

        Returns:
            str: The import statements.
        """
        # List of import statements
        imports = [
            "import datetime",
            "import boto3",
            "import pprint",
            "from pydantic import BaseModel",
            "from typing import List, Dict, Optional",
            "from boto3.session import Session",
            "from utils import Unassigned",
            "from shapes import *",
        ]

        formated_imports = "\n".join(imports)
        formated_imports += "\n\n\n"

        # Join the import statements with a newline character and return
        return formated_imports

    def generate_resources(self, 
                           output_folder=GENERATED_CLASSES_LOCATION,
                           file_name=RESOURCES_CODEGEN_FILE_NAME) -> None:
        """
        Generate the resources file.

        Args:
            output_folder (str, optional): The output folder path. Defaults to "GENERATED_CLASSES_LOCATION".
        """
        # Check if the output folder exists, if not, create it
        os.makedirs(output_folder, exist_ok=True)
        
        # Create the full path for the output file
        output_file = os.path.join(output_folder, file_name)
        
        # Open the output file
        with open(output_file, "w") as file:
            # Generate and write the license to the file
            file.write(self.generate_license())

            # Generate and write the imports to the file
            file.write(self.generate_imports())

            # Iterate over the rows in the resources plan
            for _, row in self.resources_plan.iterrows():
                # Extract the necessary data from the row
                resource_name = row['resource_name']
                class_methods = row['class_methods']
                object_methods = row['object_methods']
                additional_methods = row['additional_methods']
                raw_actions = row['raw_actions']

                # Generate the resource class
                resource_class = self.generate_resource_class(resource_name, 
                                                              class_methods, 
                                                              object_methods, 
                                                              additional_methods, 
                                                              raw_actions)
                
                # If the resource class was successfully generated, write it to the file
                if resource_class:
                    file.write(f"{resource_class}\n\n")

    def generate_resource_class(self, 
                                resource_name: str, 
                                class_methods: list, 
                                object_methods: list, 
                                additional_methods: list, 
                                raw_actions: list) -> str:
        """
        Generate the resource class for a resource.

        Args:
            resource_name (str): The name of the resource.
            class_methods (list): The class methods.
            object_methods (list): The object methods.
            additional_methods (list): The additional methods.
            raw_actions (list): The raw actions.

        Returns:
            str: The formatted resource class.

        """
        # Initialize an empty string for the resource class
        resource_class = ""

        # Check if 'get' is in the class methods
        if 'get' in class_methods:
            # Start defining the class
            resource_class = f"class {resource_name}(BaseModel):\n"

            # Get the operation and shape for the 'get' method
            get_operation = self.operations["Describe" + resource_name]
            get_operation_shape = get_operation["output"]["shape"]

            # Generate the class attributes based on the shape
            class_attributes = self.shapes_extractor.generate_data_shape_members(get_operation_shape)

            # Check if 'create' is in the class methods
            if 'create' in class_methods:
                # Generate the 'create' method
                create_method = self.generate_create_method(resource_name)
            else:
                # If there's no 'create' method, log a message and set 'create_method' to an empty string
                create_method = ""
                log.warning(f"Resource {resource_name} does not have a CREATE method")

            # Generate the 'get' method
            get_method = self.generate_get_method(resource_name)

            try:
                # Add the class attributes, 'create' method, and 'get' method to the class definition
                resource_class += add_indent(class_attributes, 4)

                if create_method:
                    resource_class += "\n"
                    resource_class += add_indent(create_method, 4)

                resource_class += "\n"
                resource_class += add_indent(get_method, 4)
            except Exception:
                # If there's an error, log the class attributes for debugging and raise the error
                log.error(f"DEBUG HELP {class_attributes} \n {create_method} \n {get_method}")
                raise
        else:
            # If there's no 'get' method, log a message
            # TODO: Handle the resources without 'get' differently
            log.warning(f"Resource {resource_name} does not have a GET method")

        # Return the class definition
        return resource_class
    
    def generate_create_method(self, resource_name) -> str:
        """
        Auto-generate the CREATE method for a resource.

        Args:
            resource (str): The resource name.

        Returns:
            str: The formatted Create Method template.

        """
        # Get the operation and shape for the 'create' method
        operation = self.operations["Create" + resource_name]
        operation_input_shape_name = operation["input"]["shape"]

        # Generate the arguments for the 'create' method
        typed_shape_members = self.shapes_extractor.generate_shape_members(operation_input_shape_name)
        create_args = ",\n\t".join(f"{attr}: {type}" for attr, type in typed_shape_members.items())
        create_args += ","

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        # Generate the input arguments for the operation
        input_shape_members = self.shapes[operation_input_shape_name]["members"].keys()
        operation_input_args = {member: convert_to_snake_case(member) for member in input_shape_members}

        # Convert the operation name to snake case
        operation = convert_to_snake_case("Create" + resource_name)

        # Initialize an empty string for the object attribute assignments
        object_attribute_assignments = ""

        # Check if the operation has an 'output'
        if "output" in operation:
            # Get the shape for the operation output
            operation_output_shape_name = operation["output"]["shape"]
            output_shape_members = self.shapes[operation_output_shape_name]["members"]

            # Generate the object attribute assignments
            for member in output_shape_members.keys():
                attribute_from_member = convert_to_snake_case(member)
                object_attribute_assignments += f"{resource_lower}.{attribute_from_member} = response[\"{member}\"]\n"

            # Add indentation to the object attribute assignments
            object_attribute_assignments = add_indent(object_attribute_assignments, 4)

        # Format the method using the CREATE_METHOD_TEMPLATE
        formatted_method = CREATE_METHOD_TEMPLATE.format(
            create_args=create_args,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
            object_attribute_assignments=object_attribute_assignments,
        )

        # Return the formatted method
        return formatted_method
    
    def generate_get_method(self, resource_name) -> str:
        """
        Auto-generate the GET method (describe API) for a resource.

        Args:
            resource (str): The resource name.

        Returns:
            str: The formatted Get Method template.

        """
        # Get the operation and shapes for the 'get' method
        resource_operation = self.operations["Describe" + resource_name]
        resource_operation_input_shape_name = resource_operation["input"]["shape"]
        resource_operation_output_shape_name = resource_operation["output"]["shape"]

        # Generate the arguments for the 'get' method
        typed_shape_members = self.shapes_extractor.generate_shape_members(resource_operation_input_shape_name)
        describe_args = ",\n".join(f"{attr}: {type}" for attr, type in typed_shape_members.items())
        describe_args += ","

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        # Generate the input arguments for the operation
        input_shape_members = self.shapes[resource_operation_input_shape_name]["members"].keys()
        operation_input_args = {member: convert_to_snake_case(member) for member in input_shape_members}

        # Convert the operation name to snake case
        operation = convert_to_snake_case("Describe" + resource_name)

        # Initialize an empty string for the object attribute assignments
        object_attribute_assignments = ""

        # Get the members for the operation output shape
        output_shape_members = self.shapes[resource_operation_output_shape_name]["members"]

        # Generate the object attribute assignments
        for member in output_shape_members.keys():
            attribute_from_member = convert_to_snake_case(member)
            object_attribute_assignments += f"{resource_lower}.{attribute_from_member} = response[\"{member}\"]\n"

        # Add indentation to the object attribute assignments
        object_attribute_assignments = add_indent(object_attribute_assignments, 4)

        # Format the method using the GET_METHOD_TEMPLATE
        formatted_method = GET_METHOD_TEMPLATE.format(
            describe_args=describe_args,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
            object_attribute_assignments=object_attribute_assignments,
        )

        # Return the formatted method
        return formatted_method

if __name__ == "__main__":
    file_path = os.getcwd() + '/sample/sagemaker/2017-07-24/service-2.json'
    resource_generator = ResourcesCodeGen(file_path)
