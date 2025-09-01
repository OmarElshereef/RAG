from fastapi import HTTPException, UploadFile
from src.controllers.BaseController import BaseController
from .ProjectController import ProjectController
from src.models import ResponseSignal
import re, os


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576  # 1024 * 1024, for MB conversion

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value

    def generate_unique_filePath(self, file: UploadFile, project_id: str) -> str:
        random_key = self.generate_random_string()

        project_path = ProjectController().get_project_path(project_id)

        cleaned_file_name = self.get_clean_filename(file.filename)

        new_file_path = os.path.join(project_path, f"{random_key}_{cleaned_file_name}")

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path, f"{random_key}_{cleaned_file_name}"
            )

        return new_file_path, f"{random_key}_{cleaned_file_name}"

    def get_clean_filename(self, filename: str) -> str:
        filename = filename.strip()

        filename = filename.replace(" ", "_")

        # Remove all characters except alphanumeric, underscore, and dot
        filename = re.sub(r"[^a-zA-Z0-9_.]", "", filename)

        return filename
