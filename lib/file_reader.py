import os
from typing import Optional


def read_files_in_directory(directory_path: str, get_files: Optional[list[str]] = None):
    """
    Reads all text files in a directory and returns their contents.

    Args:
        directory_path (str): The path to the directory to read files from.

    Returns:
        dict: A dictionary where the keys are file names and the values are file contents.
    """
    file_contents = {}
    for filename in os.listdir(directory_path):
        if get_files is None or any(filename.endswith(ext) for ext in get_files):
            print("Getting file: ", filename)
            with open(os.path.join(directory_path, filename), "r") as file:
                file_contents[filename] = file.read()

    return file_contents
