from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProcessController
from src.models import ResponseSignal, DataBaseEnums, AssetTypeEnums
from src.models.ProjectModel import ProjectModel
from src.models.ChunkModel import ChunkModel
from src.models.AssetModel import AssetModel
from src.models.db_schemas import DataChunk, Project, Asset
from .schemas.data import ProcessRequest
import aiofiles
import logging
import os

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):
    project_model = await ProjectModel.create_instance(request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id)

    data_controller = DataController()
    is_valid, result_message = data_controller.validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": result_message}
        )

    file_path, file_id = data_controller.generate_unique_filePath(file, project_id)

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(chunk)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignal.FILE_UPLOAD_FAILED.value},
        )

    asset_model = await AssetModel.create_instance(request.app.db_client)

    asset: Asset = Asset(
        project_id=project.id,
        type=AssetTypeEnums.FILE.value,
        name=file_id,
        size=os.path.getsize(file_path),
    )

    assest_record = await asset_model.create_asset(asset)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(assest_record.id),
        },
    )


@data_router.post("/process/{project_id}")
async def process_data(
    request: Request, project_id: str, process_request: ProcessRequest
):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(request.app.db_client)
    chunk_model = await ChunkModel.create_instance(request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id)

    process_controller = ProcessController(project_id)

    file_content = process_controller.get_file_content(file_id)

    file_chunks = process_controller.process_file_content(
        file_content, file_id, chunk_size, overlap_size
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignal.PROCESSING_FAILED.value},
        )

    file_chunks_records = [
        DataChunk(
            text=chunk.page_content,
            metadata=chunk.metadata,
            order=i + 1,
            project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    if do_reset:
        deleted_count = await chunk_model.delete_chunks_by_project(project.id)
        logger.info(
            f"Reset: Deleted {deleted_count} chunks for project_id: {project_id}"
        )

    no_records = await chunk_model.insert_many_chunks(file_chunks_records)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
        },
    )
