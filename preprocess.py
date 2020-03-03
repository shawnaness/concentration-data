import json
from collections import defaultdict

'''
PARSE STUDENT COURSES
'''

def parse_student_courses(file):
	# file contains a list of dictionaries
	# each dictionary is a course taken by a student
	read_file = open(file, "r")
	student_data = json.load(read_file)

	# KEY: student_id, VALUE: list of courses declared
	SCB = defaultdict(list)
	AB = defaultdict(list)

	for student_course in student_data:
		deg = student_course['degree_short']
		student_id = student_course['declaration_uuid']

		if deg == "Sc.B.":
			use_dict = SCB
		elif deg == "A.B.":
			use_dict = AB
		else:
			raise Exception('Unknown degree: ' + deg)

		use_dict[student_id].append(student_course)

	read_file.close()
	return (SCB, AB)


'''
PARSE DECLARATION REQUIREMENTS
'''

def parse_declaration_reqs(file):
	# file contains a list of dictionaries
	# each dictionary contains requirements for a concentration declaration
	read_file = open(file, "r")
	program_definitions = json.load(read_file)

	# KEY: declaration title, VALUE: dictionary of program plan (uuids)
	uuid_req_dicts = {}
	# KEY: declaration title, VALUE: dictionary of program plan (course name)
	course_req_dicts = {}
	for program in program_definitions:
		# parse definition plan into requirement areas
		uuids_dict, courses_dict, uuid_to_course, course_to_uuid = \
			parse_program_spec(program)

		# convert to KEY: uuid, VALUE: list of categories
		uuid_to_category = create_dict_to_category(uuids_dict)
		# convert to KEY: course name: VALUE, list of categories
		course_to_category = create_dict_to_category(courses_dict)

		title = program['degree_short'] + program['term_id']
		if program['track_code']:
			title += program['track_code']

		uuid_req_dicts[title] = uuid_to_category
		course_req_dicts[title] = course_to_category
	read_file.close()
	return uuid_req_dicts, course_req_dicts, uuid_to_course, course_to_uuid


def parse_program_spec(program):
	uuids_dict = {}
	courses_dict = {}
	all_uuid_to_course = defaultdict(list)
	all_course_to_uuid = defaultdict(list)
	requirements = program['requirement_definitions_json']
	for req in requirements:
		r_title = req['title']
		if r_title in ['Calculus Prerequisite', 'Additional Courses', \
		'Professional Track', 'Capstone Course']:
			uuids, courses, uuid_to_course, course_to_uuid = \
				create_category_dict([req])
			uuids_dict[r_title] = uuids
			courses_dict[r_title] = courses
			for (k, v) in uuid_to_course.items():
				all_uuid_to_course[k].extend(v)
			for (k, v) in course_to_uuid.items():
				all_course_to_uuid[k].extend(v)
		elif r_title == 'Introductory Courses':
			intro_uuids_dict = {}
			intro_courses_dict = {}
			for sequence in req['requirement_definitions'][0]['requirement_definitions']:
				s_title = sequence['title']
				uuids, courses, uuid_to_course, course_to_uuid = 
					create_category_dict([sequence])
				intro_uuids_dict[s_title] = uuids
				intro_courses_dict[s_title] = courses
				for (k, v) in uuid_to_course.items():
					all_uuid_to_course[k].extend(v)
				for (k, v) in course_to_uuid.items():
					all_course_to_uuid[k].extend(v)
			uuids_dict[r_title] = intro_uuids_dict
			courses_dict[r_title] = intro_courses_dict
		elif r_title == 'Intermediate Courses':
			intermed_uuids_dict = {}
			intermed_courses_dict = {}
			for category in req['requirement_definitions'][0]['requirement_definitions']\
			[0]['requirement_definitions']:
				c_title = category['title']
				uuids, courses, uuid_to_course, course_to_uuid = \
					create_category_dict([category])
				intermed_uuids_dict[c_title] = uuids
				intermed_courses_dict[c_title] = courses
				for (k, v) in uuid_to_course.items():
					all_uuid_to_course[k].extend(v)
				for (k, v) in course_to_uuid.items():
					all_course_to_uuid[k].extend(v)
			uuids_dict[r_title] = intermed_uuids_dict
			courses_dict[r_title] = intermed_courses_dict
		elif r_title == 'Pathways':
			pathway_uuids_dict = {}
			pathway_courses_dict = {}
			for pathway in req['requirement_definitions'][0]['requirement_definitions']:
				p_title = pathway['title']
				if p_title == 'Self-Designed Pathway':
					uuids, courses, uuid_to_course, course_to_uuid = \
						create_category_dict([pathway])
					pathway_uuids_dict[p_title] = uuids
					pathway_courses_dict[p_title] = courses
					for (k, v) in uuid_to_course.items():
						all_uuid_to_course[k].extend(v)
					for (k, v) in course_to_uuid.items():
						all_course_to_uuid[k].extend(v)
				else:
					group_uuids_dict = {}
					group_courses_dict = {}
					for group in pathway['requirement_definitions']:
						g_title = group['title']
						uuids, courses, uuid_to_course, course_to_uuid = \
							create_category_dict([group])
						group_uuids_dict[g_title] = uuids
						group_courses_dict[g_title] = courses
						for (k, v) in uuid_to_course.items():
							all_uuid_to_course[k].extend(v)
						for (k, v) in course_to_uuid.items():
							all_course_to_uuid[k].extend(v)
					pathway_uuids_dict[p_title] = group_uuids_dict
					pathway_courses_dict[p_title] = group_courses_dict
			uuids_dict[r_title] = pathway_uuids_dict
			courses_dict[r_title] = pathway_courses_dict
		else:
			print("Unknown requirements category: " + r_title)
	return uuids_dict, courses_dict, all_uuid_to_course, all_course_to_uuid


def create_category_dict(req_list):
	if 'requirement_definitions' in req_list[0]:
		new_req_list = []
		for req in req_list:
			if 'requirement_definitions' in req:
				new_req_list += req['requirement_definitions']
			else:
				new_req_list.append(req)
		return create_category_dict(new_req_list)
	else:
		uuids = []
		courses = []
		uuid_to_course = defaultdict(list)
		course_to_uuid = defaultdict(list)
		for req in req_list:
			if 'requirement_definitions' in req:
				sub_uuids, sub_courses, sub_utc, sub_ctu = \
					create_category_dict(req['requirement_definitions'])
				uuids += sub_uuids
				courses += sub_courses
				for (k, v) in sub_utc.items():
					uuid_to_course[k].extend(v)
				for (k, v) in sub_ctu.items():
					course_to_uuid[k].extend(v)
			else:
				uuid = req['requirement_uuid']
				course = req['title']
				uuids.append(uuid)
				courses.append(course)
				uuid_to_course[uuid].append(course)
				course_to_uuid[course].append(uuid)
		return uuids, courses, uuid_to_course, course_to_uuid


def create_dict_to_category(old_dict):
	courses_dict = defaultdict(list)
	for (k, v) in old_dict.items():
		if isinstance(v, dict):
			flattened = flatten_dict(k, v)
			for (sub_k, sub_v) in flattened.items():
				for course in sub_v:
					courses_dict[course].append(sub_k)
		elif isinstance(v, list):
			for course in v:
				courses_dict[course].append(k)
		else:
			raise Exception('Improperly formatted requirements dictionary.')
	return courses_dict


def flatten_dict(key, d):
	new_dict = {}
	for (k, v) in d.items():
		if isinstance(v, dict):
			sub_dict = flatten_dict(k, v)
			for (sub_k, sub_v) in sub_dict.items():
				new_key = key + '/' + sub_k
				new_dict[new_key] = sub_v
		else:
			new_key = key + '/' + k
			new_dict[new_key] = v
	return new_dict