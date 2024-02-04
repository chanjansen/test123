import os
import logging

class FileFilter:
    # Define lists of file extensions for different types
    CONFIG_EXTENSIONS = ['.json', '.yaml', '.yml', '.ini', '.conf']
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.odg']
    DOCUMENT_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.txt', '.md', 'pptx']
    IGNORED_DIRECTORIES = ['node_modules', '.git', 'build', 'dist']
    BINARY_EXTENSIONS = [
        '.exe', '.dll', '.so', '.bin',  # Executables and libraries
        '.zip', '.tar', '.tar.gz', '.rar', '.7z',  # Archives
        '.mp3', '.wav', '.aac',  # Audio files
        '.mp4', '.avi', '.mov', '.mkv',  # Video files
        '.dat',  # Generic data files that could be binary
    ]

    @staticmethod
    def should_skip(file_path):
        # Check if file is in an ignored directory
        if any(ignored_dir in file_path.split(os.sep) for ignored_dir in FileFilter.IGNORED_DIRECTORIES):
            logging.info(f"Skipping file in ignored directory: {file_path}")
            return True

        _, ext = os.path.splitext(file_path)
        
        # Check if file extension matches any in the specified lists
        if ext in {*FileFilter.CONFIG_EXTENSIONS, *FileFilter.IMAGE_EXTENSIONS, *FileFilter.DOCUMENT_EXTENSIONS, *FileFilter.BINARY_EXTENSIONS}:
            logging.info(f"Skipping file based on extension: {file_path}")
            return True

        # Optionally, handle dot-prefixed files/directories explicitly
        if file_path.startswith('.') or '/.' in file_path:
            logging.info(f"Skipping dot-prefixed file or file in dot-prefixed directory: {file_path}")
            return True

        return False