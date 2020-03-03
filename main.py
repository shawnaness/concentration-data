from preprocess import *

def main():
	taken_file = "COMP courses taken.json"
	defs_file = "COMP program defs.json"

	(SCB, AB) = parse_student_courses(taken_file)
	uuids, courses, uuid_to_course, course_to_uuid = parse_declaration_reqs(defs_file)

if __name__ == "__main__":
	main()