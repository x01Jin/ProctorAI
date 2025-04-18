MIN_STUDENTS = 1
MAX_STUDENTS = 1000
INVALID_STUDENTS_MESSAGE = "Number of students must be a positive number between 1 and 1000."
BUILDINGS = ["A", "V", "L", "F", "E"]

def validate_block(year, course, number):
    if not year or not year.isdigit() or len(year) != 2:
        return False, "Block year must be 2 digits"
    if not course or not course.isalpha() or len(course) < 2 or len(course) > 5:
        return False, "Course code must be 2-5 letters"
    if not number or not number.isdigit() or len(number) != 2:
        return False, "Block number must be 2 digits"
    return True, ""

def validate_room(building, number):
    if not building or building not in BUILDINGS:
        return False, "Invalid building code"
    if not number or not number.isdigit() or len(number) != 3:
        return False, "Room number must be 3 digits"
    floor = int(number[0])
    room = int(number[1:])
    if floor < 1 or floor > 9:
        return False, "Floor must be between 1-9"
    if room < 1 or room > 99:
        return False, "Room number must be between 01-99"
    return True, ""

def validate_num_students(num_students_str):
    if not num_students_str.isdigit():
        return False, INVALID_STUDENTS_MESSAGE
    num_students = int(num_students_str)
    if not (MIN_STUDENTS <= num_students <= MAX_STUDENTS):
        return False, INVALID_STUDENTS_MESSAGE
    return True, ""
