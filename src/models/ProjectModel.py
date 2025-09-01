from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enums.DataBaseEnums import DataBaseEnums
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import func


class ProjectModel(BaseDataModel):
    def __init__(self, db_client: sessionmaker):
        super().__init__(db_client)

    @classmethod
    async def create_instance(cls, db_client: sessionmaker):
        instance = cls(db_client)
        return instance

    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)

        return project

    async def get_project_or_create_one(self, project_id: int):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                if not project:
                    project = await self.create_project(Project(id=project_id))

            return project

    async def get_all_projects(self, page: int = 1, page_size: int = 10):

        async with self.db_client() as session:
            async with session.begin():
                total_documents = await session.execute(
                    select(func.count()).select_from(Project)
                ).scalar_one()

                total_pages = (total_documents + page_size - 1) // page_size

                query = select(Project).offset((page - 1) * page_size).limit(page_size)

                results = await session.execute(query)
                projects = results.scalars().all()

        return projects, total_pages
