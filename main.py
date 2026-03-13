from db import SessionLocal, init_db
from repository import StudentRepository


def main() -> None:
    init_db()

    with SessionLocal() as session:
        repository = StudentRepository(session)
        repository.import_from_csv("students.csv")

        print("Студенты факультета ФПМИ:")
        for student in repository.get_students_by_faculty("ФПМИ")[:10]:
            print(student)

        print("\nУникальные курсы:")
        for course in repository.get_unique_courses():
            print(course)

        print("\nСтуденты по курсу 'Мат. Анализ' с оценкой ниже 30:")
        for record in repository.get_students_by_course_with_low_grades("Мат. Анализ"):
            print(record)

        print("\nСредний балл по факультету АВТФ:")
        print(repository.get_average_grade_by_faculty("АВТФ"))


if __name__ == "__main__":
    main()
