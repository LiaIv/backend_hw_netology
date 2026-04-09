from pydantic import BaseModel, Field


class GradeRecordBase(BaseModel):
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    faculty_name: str = Field(min_length=1, max_length=100)
    course_name: str = Field(min_length=1, max_length=100)
    grade: int = Field(ge=0, le=100)


class GradeRecordCreate(GradeRecordBase):
    pass


class GradeRecordUpdate(GradeRecordBase):
    pass


class GradeRecordResponse(GradeRecordBase):
    id: int


class UserCredentials(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)


class UserRegister(UserCredentials):
    pass


class UserLogin(UserCredentials):
    pass


class AuthResponse(BaseModel):
    user_id: int
    message: str


class MessageResponse(BaseModel):
    message: str
