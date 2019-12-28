import json
from collections import defaultdict

def create_courses_dicts(file):
	# file contains a list of dictionaries
	# each dictionary is a course taken by a student
	read_file = open(file, "r")
	student_data = json.load(read_file)

	# create dictionaries of student_id to list of courses taken
	SCB = defaultdict(list)
	AB = defaultdict(list)

	for student_course in student_data:
		deg = student_course['degree_short']
		student_id = student_course['declaration_uuid']

		if deg =="Sc.B.":
			use_dict = SCB
		elif deg == "A.B.":
			use_dict = AB
		else:
			raise Exception("Unknown degree: " + deg)

		# store course entry in dictionary
		use_dict[student_id].append(student_course)

	read_file.close()
	return(SCB, AB)

def create_category_dict(req_list):
	if 'requirement_definitions' in req_list[0]:
		new_req_list = []
		for req in req_list:
			new_req_list += req['requirement_definitions']
		return create_category_dict(new_req_list)
	else:
		uuids = []
		courses = []
		for req in req_list:
			if 'requirement_definitions' in req:
				sub_uuids, sub_courses = create_category_dict(req['requirement_definitions'])
				uuids += sub_uuids
				courses += sub_courses
			else:
				uuids.append(req['requirement_uuid'])
				courses.append(req['title'])
		return uuids, courses

def parse_spec(spec):
	uuids_dict = {}
	courses_dict = {}
	requirements = spec['requirement_definitions_json']
	for req in requirements:
		if req['title'] == 'Calculus Prerequisite':
			uuids, courses = create_category_dict([req])
			uuids_dict[req['title']] = uuids
			courses_dict[req['title']] = courses
		elif req['title'] == "Introductory Courses":
			intro_uuids_dict = {}
			intro_courses_dict = {}
			for sequence in req['requirement_definitions'][0]['requirement_definitions']:
				title = sequence['title']
				uuids, courses = create_category_dict([sequence])
				intro_uuids_dict[title] = uuids
				intro_courses_dict[title] = courses
			uuids_dict[req['title']] = intro_uuids_dict
			courses_dict[req['title']] = intro_courses_dict
		elif req['title'] == "Intermediate Courses":
			intermed_uuids_dict = {}
			intermed_courses_dict = {}
			for category in req['requirement_definitions'][0]['requirement_definitions'][0]['requirement_definitions']:
				title = category['title']
				uuids, courses = create_category_dict([category])
				intermed_uuids_dict[title] = uuids
				intermed_courses_dict[title] = courses
			uuids_dict[req['title']] = intermed_uuids_dict
			courses_dict[req['title']] = intermed_courses_dict
		elif req['title'] == "Pathways":
			pathway_uuids_dict = {}
			pathway_courses_dict = {}
			for pathway in req['requirement_definitions'][0]['requirement_definitions']:
				title = pathway['title']
				# smushes core, related, and intermediate into one list
				uuids, courses = create_category_dict([pathway])
				pathway_uuids_dict[title] = uuids
				pathway_courses_dict[title] = courses
			uuids_dict[req['title']] = pathway_uuids_dict
			courses_dict[req['title']] = pathway_courses_dict
		elif req['title'] == "Additional Courses":
			uuids, courses = create_category_dict([req])
			uuids_dict[req['title']] = uuids
			courses_dict[req['title']] = courses
		elif req['title'] == "Professional Track":
			uuids, courses = create_category_dict([req])
			uuids_dict[req['title']] = uuids
			courses_dict[req['title']] = courses 
		elif req['title'] == "Capstone Course":
			uuids, courses = create_category_dict([req])
			uuids_dict[req['title']] = uuids
			courses_dict[req['title']] = courses
		else:
			print("Unknown requirements category: " + req['title'])
	return uuids_dict, courses_dict

def create_reqid_dict(spec): 
	id_dict = {}
	for (k, v) in spec.items():
		if k in ["Introductory Courses", "Intermediate Courses", "Pathways"]:
			for (title, courses) in v.items():
				for course in courses:
					new_category = k + " - " + title
					id_dict[course] = new_category
		elif k in ["Calculus Prerequisite", "Additional Courses", "Professional Track", "Capstone Course"]:
			for course in v:
				id_dict[course] = k
		else:
			print("Unknown requirements category: " + k)
	return id_dict


def process_defs(file):
	read_file = open(file, "r")
	defs = json.load(read_file)

	# dictionary of program title to program plan
	uuid_req_dicts = {}
	course_req_dicts = {}
	for d in defs:
		tag = d['degree_short'] + d['term_id']
		if d['track_code']:
			tag += d['track_code']
		uuids_dict, courses_dict = parse_spec(d) # parse the definition plan into requirement areas
		uuids_req = create_reqid_dict(uuids_dict)
		courses_req = create_reqid_dict(courses_dict) # map the requirement slots to their areas
		uuid_req_dicts[tag] = uuids_req
		course_req_dicts[tag] = courses_req
	read_file.close()
	return (uuid_req_dicts, course_req_dicts)

def student_plan(student, uuids):
	metadata = student[0]
	if metadata['term_id'] in ['201820', '201800', '201910', '201900']:
		term_id = metadata['degree_short'] + '201810'
	elif metadata['term_id'] in ['201620', '201710']:
		term_id = metadata['degree_short'] + '201720'
	else:
		term_id = metadata['degree_short'] + metadata['term_id']
	if metadata['track_code']:
		term_id += metadata['track_code']
	req_dict = uuids[term_id]
	plan = {}
	for course in student:
		if course['subject_code'] and course['course_number']:
			course_name = course['subject_code'] + course['course_number']
		else:
			course_name = course['course_number']
			print("Substitution:" + course['course_number'])
		if course['requirement_uuid'] in req_dict:
			req_tag = req_dict[course['requirement_uuid']]
			if req_tag in plan:
				plan[req_tag].append(course_name)
			else:
				plan[req_tag] = [course_name]
			pass
		else:
			print("no requirement ID found for " + course_name + ": " + course['requirement_uuid'])
	return plan

def count_students(degree, uuids):
	student_ids = list(degree.keys())
	num_students = len(student_ids)
	all_categories = {}
	for student in student_ids:
		plan = student_plan(degree[student], uuids)
		for key in plan:
			if key not in all_categories:
				all_categories[key] = 0
			all_categories[key] += 1
	for (k, v) in all_categories.items():
		if k.startswith("Introductory Courses") or k.startswith("Pathways"):
			decimal = float(v) / float(num_students)
			print(k + ": {:.2f}".format(decimal) + " (%d / %d)" % (v, num_students))

def main():
	taken_file = "COMP courses taken.json"
	defs_file = "COMP program defs.json"

	(SCB, AB) = create_courses_dicts(taken_file)
	(uuids, courses) = process_defs(defs_file)

	print("AB percentages:")
	count_students(AB, uuids)
	print("SCB percentages:")
	count_students(SCB, uuids)

if __name__ == "__main__":
	main()