from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from auth import get_current_user, router as auth_router
from db import SessionLocal, init_db
from repository import StudentRepository
from schemas import GradeRecordCreate, GradeRecordResponse, GradeRecordUpdate


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    csv_path = Path("students.csv")

    with SessionLocal() as session:
        repository = StudentRepository(session)
        if csv_path.exists() and repository.get_grade_record_count() == 0:
            repository.import_from_csv(csv_path)

    yield


app = FastAPI(title="Students API", lifespan=lifespan)
app.include_router(auth_router)


def get_db():
    with SessionLocal() as session:
        yield session


def get_repository(session: Session = Depends(get_db)) -> StudentRepository:
    return StudentRepository(session)


@app.get("/", dependencies=[Depends(get_current_user)])
def read_root() -> dict[str, str]:
    return {"message": "Students API is running"}


@app.post(
    "/records",
    response_model=GradeRecordResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_record(
    payload: GradeRecordCreate,
    repository: StudentRepository = Depends(get_repository),
) -> dict[str, str | int]:
    try:
        return repository.create_grade_record(**payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@app.get(
    "/records",
    response_model=list[GradeRecordResponse],
    dependencies=[Depends(get_current_user)],
)
def get_records(
    repository: StudentRepository = Depends(get_repository),
) -> list[dict[str, str | int]]:
    return repository.get_all_grade_records()


@app.get(
    "/records/{record_id}",
    response_model=GradeRecordResponse,
    dependencies=[Depends(get_current_user)],
)
def get_record(
    record_id: int,
    repository: StudentRepository = Depends(get_repository),
) -> dict[str, str | int]:
    record = repository.get_grade_record_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@app.put(
    "/records/{record_id}",
    response_model=GradeRecordResponse,
    dependencies=[Depends(get_current_user)],
)
def update_record(
    record_id: int,
    payload: GradeRecordUpdate,
    repository: StudentRepository = Depends(get_repository),
) -> dict[str, str | int]:
    try:
        record = repository.update_grade_record(record_id, **payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@app.delete(
    "/records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def delete_record(
    record_id: int,
    repository: StudentRepository = Depends(get_repository),
) -> Response:
    deleted = repository.delete_grade_record(record_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
