from dataclasses import dataclass

MIN_STUDENTS = 1
MAX_STUDENTS = 1000
BUILDINGS = ["A", "V", "L", "F", "E"]

@dataclass
class ValidationResult:
    valid: bool
    error: str = ""

    def __bool__(self):
        return self.valid

class FieldValidator:
    @staticmethod
    def validate_students(num_students_str: str) -> ValidationResult:
        if not num_students_str.isdigit():
            return ValidationResult(False, "Number of students must be a positive number")
        num_students = int(num_students_str)
        if not MIN_STUDENTS <= num_students <= MAX_STUDENTS:
            return ValidationResult(False, f"Students must be between {MIN_STUDENTS} and {MAX_STUDENTS}")
        return ValidationResult(True)

    @staticmethod
    def validate_block(year: str, course: str, number: str) -> ValidationResult:
        if not year or not year.isdigit() or len(year) != 2:
            return ValidationResult(False, "Block year must be 2 digits")
        if not course or not course.isalpha() or len(course) < 2 or len(course) > 5:
            return ValidationResult(False, "Course code must be 2-5 letters")
        if not number or not number.isdigit() or len(number) != 2:
            return ValidationResult(False, "Block number must be 2 digits")
        return ValidationResult(True)

    @staticmethod
    def validate_room(building: str, number: str) -> ValidationResult:
        if not building or building not in BUILDINGS:
            return ValidationResult(False, "Invalid building code")
        if not number or not number.isdigit() or len(number) != 3:
            return ValidationResult(False, "Room number must be 3 digits")
        floor = int(number[0])
        room = int(number[1:])
        if floor < 1 or floor > 9:
            return ValidationResult(False, "Floor must be between 1-9")
        if room < 1 or room > 99:
            return ValidationResult(False, "Room number must be between 01-99")
        return ValidationResult(True)

    @staticmethod
    def validate_time_range(start_time: str, end_time: str) -> ValidationResult:
        def to_minutes(t):
            h, m = map(int, t.split(":"))
            return h * 60 + m
        start = to_minutes(start_time)
        end = to_minutes(end_time)
        if end <= start:
            return ValidationResult(False, "End time must be after start time.")
        duration = end - start
        if duration >= 300:
            return ValidationResult(False, "Time range must be less than 5 hours.")
        return ValidationResult(True)
