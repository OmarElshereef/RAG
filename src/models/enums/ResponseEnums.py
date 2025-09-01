from enum import Enum


class ResponseSignal(Enum):
    FILE_VALIDATION_SUCCESS = "file validation success"
    FILE_TYPE_NOT_SUPPORTED = "file type not supported"
    FILE_SIZE_EXCEEDED = "file size exceeded the limit"
    FILE_UPLOAD_SUCCESS = "file upload success"
    FILE_UPLOAD_FAILED = "file upload failed"
    PROCESSING_SUCCESS = "file processing success"
    PROCESSING_FAILED = "file processing failed"
    NO_FILES_TO_PROCESS = "no files to process"
    FILE_ID_ERROR = "No file found with the provided file_id"
    PROJECT_NOT_FOUND = "project not found"
    INSERT_INTO_VECTOR_DB_ERROR = "failed to insert data into vector database"
    INSERT_INTO_VECTOR_DB_SUCCESS = "data inserted into vector database successfully"
    GET_INDEX_INFO_ERROR = "failed to get index information"
    GET_INDEX_INFO_SUCCESS = "index information retrieved successfully"
    SEARCH_IN_VECTOR_DB_ERROR = "failed to search in vector database"
    SEARCH_IN_VECTOR_DB_SUCCESS = "search in vector database successful"
    RAG_ANSWER_GENERATION_ERROR = "failed to generate answer for the query"
    RAG_ANSWER_GENERATION_SUCCESS = "answer generated successfully"
