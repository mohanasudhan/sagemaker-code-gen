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
"""Utility module for common utility methods."""
import re
import subprocess

WORD_SEPARATORS = [".", "-", "/", "::", "_"]

def add_indent(text, num_spaces=4):
    """
    Add customizable indent spaces to a given text.

    Parameters:
        text (str): The text to which the indent spaces will be added.
        num_spaces (int): Number of spaces to be added for each level of indentation. Default is 4.

    Returns:
        str: The text with added indent spaces.
    """
    indent = ' ' * num_spaces
    lines = text.split('\n')
    indented_text = '\n'.join(indent + line for line in lines)
    return indented_text.rstrip(' ')


def clean_documentaion(documentation):
    documentation = re.sub(r'<\/?p>', '', documentation)
    documentation = re.sub(r'<\/?code>', "'", documentation)
    return documentation


def convert_to_snake_case(entity_name):
    """
    Convert a string to snake_case.

    Args:
        entity_name (str): The string to convert.

    Returns:
        str: The converted string in snake_case.
    """
    
    # Replace any separator with an "_"
    modified_string = entity_name
    for separator in WORD_SEPARATORS:
        modified_string = modified_string.replace(separator, "_")
    
    # check if it is already in upper snake case
    if all(part.isupper() for part in modified_string.split("_")):
        return modified_string.lower()
    
    snake_case_string = re.sub(r'(?<!^)(?=[A-Z])', '_', modified_string).lower()

    # Remove consecutive "_"
    snake_case_string = re.sub(r'_{2,}', '_', snake_case_string)
    
    return snake_case_string


def reformat_file_with_black(filename):
    try:
        # Run black with specific options using subprocess
        subprocess.run(["black", "-l", "100", filename], check=True)
        print(f"File '{filename}' reformatted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while reformatting '{filename}': {e}")
