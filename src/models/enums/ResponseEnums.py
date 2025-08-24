from enum import Enum


class ResponseSignal(Enum):
    FILE_VALIDATION_SUCCESS = "file validation success"
    FILE_TYPE_NOT_SUPPORTED = "file type not supported"
    FILE_SIZE_EXCEEDED = "file size exceeded the limit"
    FILE_UPLOAD_SUCCESS = "file upload success"
    FILE_UPLOAD_FAILED = "file upload failed"
