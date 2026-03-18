from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Course, Faculty, GradeRecord, Student


class StudentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _normalize_text(value: str) -> str:
        return value.strip()

    def _serialize_grade_record(self, record: GradeRecord) -> dict[str, str | int]:
        return {
            "id": record.id,
            "last_name": record.student.last_name,
            "first_name": record.student.first_name,
            "faculty_name": record.student.faculty.name,
            "course_name": record.course.name,
            "grade": record.grade,
        }

    def add_faculty(self, name: str) -> Faculty:
        name = self._normalize_text(name)
        faculty = self.session.scalar(select(Faculty).where(Faculty.name == name))
        if faculty is None:
            faculty = Faculty(name=name)
            self.session.add(faculty)
            self.session.flush()
        return faculty

    def add_course(self, name: str) -> Course:
        name = self._normalize_text(name)
        course = self.session.scalar(select(Course).where(Course.name == name))
        if course is None:
            course = Course(name=name)
            self.session.add(course)
            self.session.flush()
        return course

    def add_student(self, last_name: str, first_name: str, faculty_name: str) -> Student:
        last_name = self._normalize_text(last_name)
        first_name = self._normalize_text(first_name)
        faculty = self.add_faculty(faculty_name)
        student = self.session.scalar(
            select(Student).where(
                Student.last_name == last_name,
                Student.first_name == first_name,
                Student.faculty_id == faculty.id,
            )
        )
        if student is None:
            student = Student(
                last_name=last_name,
                first_name=first_name,
                faculty=faculty,
            )
            self.session.add(student)
            self.session.flush()
        return student

    def add_grade_record(
        self,
        last_name: str,
        first_name: str,
        faculty_name: str,
        course_name: str,
        grade: int,
        *,
        commit: bool = True,
    ) -> GradeRecord:
        student = self.add_student(last_name, first_name, faculty_name)
        course = self.add_course(course_name)

        record = self.session.scalar(
            select(GradeRecord).where(
                GradeRecord.student_id == student.id,
                GradeRecord.course_id == course.id,
            )
        )
        if record is None:
            record = GradeRecord(student=student, course=course, grade=grade)
            self.session.add(record)
            self.session.flush()
        else:
            record.grade = grade

        if commit:
            self.session.commit()
        return record

    def create_grade_record(
        self,
        last_name: str,
        first_name: str,
        faculty_name: str,
        course_name: str,
        grade: int,
    ) -> dict[str, str | int]:
        student = self.add_student(last_name, first_name, faculty_name)
        course = self.add_course(course_name)
        existing_record = self.session.scalar(
            select(GradeRecord).where(
                GradeRecord.student_id == student.id,
                GradeRecord.course_id == course.id,
            )
        )
        if existing_record is not None:
            self.session.rollback()
            raise ValueError("A record for this student and course already exists.")

        record = GradeRecord(student=student, course=course, grade=grade)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return self._serialize_grade_record(record)

    def get_grade_record_count(self) -> int:
        return int(self.session.scalar(select(func.count(GradeRecord.id))) or 0)

    def get_all_grade_records(self) -> list[dict[str, str | int]]:
        stmt = (
            select(GradeRecord)
            .join(GradeRecord.student)
            .join(Student.faculty)
            .join(GradeRecord.course)
            .order_by(GradeRecord.id)
        )
        records = self.session.scalars(stmt).all()
        return [self._serialize_grade_record(record) for record in records]

    def get_grade_record_by_id(self, record_id: int) -> dict[str, str | int] | None:
        stmt = (
            select(GradeRecord)
            .join(GradeRecord.student)
            .join(Student.faculty)
            .join(GradeRecord.course)
            .where(GradeRecord.id == record_id)
        )
        record = self.session.scalar(stmt)
        return None if record is None else self._serialize_grade_record(record)

    def update_grade_record(
        self,
        record_id: int,
        last_name: str,
        first_name: str,
        faculty_name: str,
        course_name: str,
        grade: int,
    ) -> dict[str, str | int] | None:
        record = self.session.get(GradeRecord, record_id)
        if record is None:
            return None

        student = self.add_student(last_name, first_name, faculty_name)
        course = self.add_course(course_name)
        existing_record = self.session.scalar(
            select(GradeRecord).where(
                GradeRecord.student_id == student.id,
                GradeRecord.course_id == course.id,
                GradeRecord.id != record_id,
            )
        )
        if existing_record is not None:
            self.session.rollback()
            raise ValueError("A record for this student and course already exists.")

        record.student = student
        record.course = course
        record.grade = grade
        self.session.commit()
        self.session.refresh(record)
        return self._serialize_grade_record(record)

    def delete_grade_record(self, record_id: int) -> bool:
        record = self.session.get(GradeRecord, record_id)
        if record is None:
            return False

        self.session.delete(record)
        self.session.commit()
        return True

    def import_from_csv(self, csv_path: str | Path) -> None:
        with Path(csv_path).open(encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.add_grade_record(
                    last_name=row["Фамилия"].strip(),
                    first_name=row["Имя"].strip(),
                    faculty_name=row["Факультет"].strip(),
                    course_name=row["Курс"].strip(),
                    grade=int(row["Оценка"]),
                    commit=False,
                )
        self.session.commit()

    def get_students_by_faculty(self, faculty_name: str) -> list[dict[str, str]]:
        stmt = (
            select(Student.last_name, Student.first_name, Faculty.name)
            .join(Faculty, Student.faculty_id == Faculty.id)
            .where(Faculty.name == faculty_name)
            .order_by(Student.last_name, Student.first_name)
        )
        return [
            {"last_name": last_name, "first_name": first_name, "faculty": faculty}
            for last_name, first_name, faculty in self.session.execute(stmt).all()
        ]

    def get_unique_courses(self) -> list[str]:
        stmt = select(Course.name).distinct().order_by(Course.name)
        return list(self.session.scalars(stmt).all())

    def get_students_by_course_with_low_grades(
        self,
        course_name: str,
        threshold: int = 30,
    ) -> list[dict[str, str | int]]:
        stmt = (
            select(
                Student.last_name,
                Student.first_name,
                Faculty.name,
                Course.name,
                GradeRecord.grade,
            )
            .join(GradeRecord.student)
            .join(Student.faculty)
            .join(GradeRecord.course)
            .where(Course.name == course_name, GradeRecord.grade < threshold)
            .order_by(GradeRecord.grade, Student.last_name, Student.first_name)
        )
        return [
            {
                "last_name": last_name,
                "first_name": first_name,
                "faculty": faculty,
                "course": course,
                "grade": grade,
            }
            for last_name, first_name, faculty, course, grade in self.session.execute(stmt).all()
        ]

    def get_average_grade_by_faculty(self, faculty_name: str) -> float | None:
        stmt = (
            select(func.avg(GradeRecord.grade))
            .join(GradeRecord.student)
            .join(Student.faculty)
            .where(Faculty.name == faculty_name)
        )
        average = self.session.scalar(stmt)
        return round(float(average), 2) if average is not None else None
