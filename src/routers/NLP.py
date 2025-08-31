from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from src.controllers import NLPController
from src.models import ProjectModel, ChunkModel, AssetModel
from .schemas.NLP import PushRequest, SearchRequest
from src.models.enums.ResponseEnums import ResponseSignal
import logging


logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(prefix="/api/v1/nlp", tags=["NLP"])


@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_reqeust: PushRequest):

    project_model = await ProjectModel.create_instance(request.app.db_client)

    chunk_model = await ChunkModel.create_instance(request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
    )

    has_records = True
    page = 1
    inserted_count = 0

    while has_records:
        chunks = await chunk_model.get_chunks_by_project(project.id, page=page)
        if len(chunks):
            page += 1

        if not chunks or len(chunks) == 0:
            has_records = False
            break

        is_inserted = nlp_controller.index_into_vector_db(
            project, chunks, do_reset=push_reqeust.do_reset
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"signal": ResponseSignal.INSERT_INTO_VECTOR_DB_ERROR.value},
            )
        inserted_count += len(chunks)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTOR_DB_SUCCESS.value,
            "inserted_count": inserted_count,
        },
    )


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    project_model = await ProjectModel.create_instance(request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
    )

    index_info = nlp_controller.get_vector_db_collection_info(project)

    if index_info is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseSignal.GET_INDEX_INFO_ERROR.value},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.GET_INDEX_INFO_SUCCESS.value,
            "index_info": index_info,
        },
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(
    request: Request, project_id: str, search_request: SearchRequest
):
    project_model = await ProjectModel.create_instance(request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id)

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    search_results = nlp_controller.search_vector_db_collection(
        project, search_request.text, limit=search_request.limit
    )

    if search_results is False:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseSignal.SEARCH_IN_VECTOR_DB_ERROR.value},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.SEARCH_IN_VECTOR_DB_SUCCESS.value,
            "results": [result.model_dump() for result in search_results],
        },
    )
