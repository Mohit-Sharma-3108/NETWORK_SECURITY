"""
The steup.py file is an essential part opackaging and 
distributing Python projects. It is used by setuptools
(or disutils in older Python versions) to define the configuration
of your project, such as it's metadata, dependencies and more
"""

from setuptools import find_packages, setup
from typing import List

def get_requirements() -> List[str]:
    """
    Function that returns list of requirements
    """
    requirement_list: List[str] = []
    try:
        with open("requirements.txt", "r") as file:
            # Read lines from the file
            lines = file.readlines()

            # Process each line
            for line in lines:
                requirement = line.strip()

                # Ignore empty lines and -e.
                if requirement and requirement != "-e.":
                    requirement_list.append(requirement)
    
    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_list

setup(
    name="Network_Security",
    version="0.0.1",
    author="Mohit Sharma",
    author_email="mohit1d.lp@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)
