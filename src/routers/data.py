from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProcessController, NLPController
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

data_router = APIRouter(prefix="/api/v1/data", tags=["data"])


@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: int,
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
    request: Request, project_id: int, process_request: ProcessRequest
):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(request.app.db_client)
    chunk_model = await ChunkModel.create_instance(request.app.db_client)
    asset_model = await AssetModel.create_instance(request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id)

    project_files_ids = {}

    if process_request.file_id:
        asset = await asset_model.get_asset_by_file_id(file_id, project.id)
        if asset:
            project_files_ids = {asset.id: asset.name}
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": ResponseSignal.FILE_ID_ERROR.value},
            )

    else:
        assets = await asset_model.get_all_project_assets(
            project.id, AssetTypeEnums.FILE.value
        )
        project_files_ids = {asset.id: str(asset.name) for asset in assets}

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignal.NO_FILES_TO_PROCESS.value},
        )

    process_controller = ProcessController(project_id)
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser=request.app.template_parser,
    )

    no_records = 0
    processed_files = 0
    failed_files = []

    if do_reset:
        collection_name = nlp_controller.create_collection_name(project.id)

        _ = await request.app.vector_db_client.delete_collection(collection_name)

        deleted_count = await chunk_model.delete_chunks_by_project(project.id)
        logger.info(
            f"Reset: Deleted {deleted_count} chunks for project_id: {project_id}"
        )

    for asset_id, file_id in project_files_ids.items():
        try:
            file_content = process_controller.get_file_content(file_id)

            if file_content is None or len(file_content) == 0:
                logger.error(f"No content loaded for file_id: {file_id}")
                failed_files.append(file_id)
                continue

            file_chunks = process_controller.process_file_content(
                file_content, file_id, chunk_size, overlap_size
            )

            if file_chunks is None or len(file_chunks) == 0:
                logger.error(f"Processing returned no chunks for file_id: {file_id}")
                failed_files.append(file_id)
                continue

            file_chunks_records = [
                DataChunk(
                    text=chunk.page_content,
                    meta=chunk.metadata,
                    order=i + 1,
                    project_id=project.id,
                    asset_id=asset_id,
                )
                for i, chunk in enumerate(file_chunks)
            ]

            inserted = await chunk_model.insert_many_chunks(file_chunks_records)
            no_records += inserted
            processed_files += 1

        except Exception as e:
            logger.error(f"Error processing file_id {file_id}: {e}")
            failed_files.append(file_id)
            continue

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": processed_files,
            "failed_files": failed_files,
        },
    )
