from preprocess import *
from collections import defaultdict


def get_student_term_id(student):
	# use first course entry for metadata
	metadata = student[0]
	if metadata['term_id'].startswith('2018') or metadata['term_id'].startswith('2019'):
		term_id = metadata['degree_short'] + '201810'
	elif metadata['term_id'].startswith('2016') or metadata['term_id'].startswith('2017'):
		term_id = metadata['degree_short'] + '201720'
	else:
		raise Exception('Unknown term: ' + metadata['term_id'])
	if metadata['track_code']:
		term_id += metadata['track_code']
	return term_id

def student_plan(student, uuids):
	term_id = get_student_term_id(student)
	reqs = uuids[term_id]
	plan = defaultdict(list)
	all_uuids = set()
	all_courses = set()
	for course in student:
		if course['subject_code'] and course['course_number']:
			course_name = course['subject_code'] + course['course_number']
		else: # substituted courses
			course_name = course['course_number']
			# print('Substitution: ' + course['course_number'])		
		if course['requirement_uuid'] in reqs:
			category = reqs[course['requirement_uuid']]
			if len(category) > 1:
				print('ID associated with multiple categories')
			else:
				category = category[0]
				plan[category].append(course_name)
		else:
			print('No requirement ID found for ' + course_name + ': ' + course['requirement_uuid'])
		all_uuids.add(course['requirement_uuid'])
		all_courses.add(course_name)
	return plan, all_uuids, all_courses

def analyze_degree_by_intro(degree, uuids):
	student_ids = list(degree.keys())
	num_students = 0
	all_intros = defaultdict(int)
	for student in student_ids:
		plan, _, _ = student_plan(degree[student], uuids)
		sequence = []
		for key in plan:
			if key.startswith('Introductory Courses'):
				sequence.append(key)
		if len(sequence) != 1:
			print('Declared', len(sequence), 'intro sequences.')
		else:
			num_students += 1
			for s in sequence:
				all_intros[s] += 1
	for (k, v) in all_intros.items():
		decimal = float(v) / float(num_students)
		print(k + ': {:.2f}'.format(decimal) + ' (%d / %d)' % (v, num_students))

def analyze_pathway_by_intro(degree, uuids, num_pathways):
	student_ids = list(degree.keys())
	sequence_1 = defaultdict(int)
	num_1 = 0
	sequence_2 = defaultdict(int)
	num_2 = 0
	sequence_3 = defaultdict(int)
	num_3 = 0
	for student in student_ids:
		plan, _, _ = student_plan(degree[student], uuids)
		sequence = []
		pathways = set()
		for key in plan:
			if key.startswith('Introductory Courses'):
				sequence.append(key)
			if key.startswith('Pathways'):
				pathway = ' - '.join(key.split(' - ')[0:2])
				pathways.add(pathway)
		if len(sequence) == 1 and len(pathways) == num_pathways:
			if sequence[0] == 'Introductory Courses - Sequence 1':
				curr_seq = sequence_1
				num_1 += 1
			elif sequence[0] == 'Introductory Courses - Sequence 2':
				curr_seq = sequence_2
				num_2 += 1
			elif sequence[0] == 'Introductory Courses - Sequence 3':
				curr_seq = sequence_3
				num_3 += 1
			for p in pathways:
				curr_seq[p] += 1
	print('CSCI0150/0160:')
	for (k, v) in sequence_1.items():
		decimal = float(v) / float(num_1)
		print(k + ": {:.2f}".format(decimal) + " (%d / %d)" % (v, num_1))
	print('CSCI0170/0180:')
	for (k, v) in sequence_2.items():
		decimal = float(v) / float(num_2)
		print(k + ": {:.2f}".format(decimal) + " (%d / %d)" % (v, num_2))
	print('CSCI0190:')
	for (k, v) in sequence_3.items():
		decimal = float(v) / float(num_3)
		print(k + ": {:.2f}".format(decimal) + " (%d / %d)" % (v, num_3))


def analyze_pathways(degree, uuids, num_pathways):
	student_ids = list(degree.keys())
	num_students = 0
	all_pathways = defaultdict(int)
	for student in student_ids:
		plan, _, _ = student_plan(degree[student], uuids)
		pathways = set()
		for key in plan:
			if key.startswith('Pathways'):
				pathway = ' - '.join(key.split(' - ')[0:2])
				pathways.add(pathway)
		if len(pathways) != num_pathways:
			print('Declared', len(pathways), 'pathways.')
		else:
			num_students += 1
			for p in pathways:
				all_pathways[p] += 1
	for (k, v) in all_pathways.items():
		decimal = float(v) / float(num_students)
		print(k + ': {:.2f}'.format(decimal) + ' (%d / %d)' % (v, num_students))

def analyze_intro_by_degree(ab, scb, uuids):	
	num_students = 0
	all_intros = defaultdict(lambda: defaultdict(int))
	for degree, tag in [(ab, "AB"), (scb, "SCB")]:
		student_ids = list(degree.keys())
		for student in student_ids:
			plan, _, _ = student_plan(degree[student], uuids)
			sequence = []
			for key in plan:
				if key.startswith('Introductory Courses'):
					sequence.append(key)
			if len(sequence) != 1:
				print('Declared', len(sequence), 'intro sequences.')
			else:
				num_students += 1
				for s in sequence:
					all_intros[s][tag] += 1
	for intro, degrees in all_intros.items():
		print(intro)
		total = sum(degrees.values())
		for (k, v) in degrees.items():
			decimal = float(v) / float(total)
			print(k + ': {:.2f}'.format(decimal) + ' (%d / %d)' % (v, total))


def pathways_touched_by_intro(degree, uuids, courses):
	student_ids = list(degree.keys())
	num_students = len(student_ids)
	sequence_1 = defaultdict(int)
	num_1 = 0
	sequence_2 = defaultdict(int)
	num_2 = 0
	sequence_3 = defaultdict(int)
	num_3 = 0
	for student in student_ids:
		plan, _, all_courses = student_plan(degree[student], uuids)
		sequence = []
		for key in plan:
			if key.startswith('Introductory Courses'):
				sequence.append(key)
		if len(sequence) != 1:
			print('Declared', len(sequence), 'intro sequences.')
		else:
			if sequence[0] == 'Introductory Courses - Sequence 1':
				curr_seq = sequence_1
				num_1 += 1
			elif sequence[0] == 'Introductory Courses - Sequence 2':
				curr_seq = sequence_2
				num_2 += 1
			elif sequence[0] == 'Introductory Courses - Sequence 3':
				curr_seq = sequence_3
				num_3 += 1
			term_id = get_student_term_id(degree[student])
			term_courses = courses[term_id]
			categories_touched = set()
			for course in all_courses:
				categories_touched.update(term_courses[course])
			pathways_touched = [x for x in categories_touched if x.endswith('Core Courses')]
			for p in pathways_touched:
				curr_seq[p] += 1
	print('CSCI0150/0160:')
	for (k, v) in sequence_1.items():
		decimal = float(v) / float(num_1)
		print(k + ": {:.2f}".format(decimal) + " (%d / %d)" % (v, num_1))
	print('CSCI0170/0180:')
	for (k, v) in sequence_2.items():
		decimal = float(v) / float(num_2)
		print(k + ": {:.2f}".format(decimal) + " (%d / %d)" % (v, num_2))
	print('CSCI0190:')
	for (k, v) in sequence_3.items():
		decimal = float(v) / float(num_3)
		print(k + ": {:.2f}".format(decimal) + " (%d / %d)" % (v, num_3))

def main():
	taken_file = 'COMP courses taken.json'
	defs_file = 'COMP program defs.json'

	(SCB, AB) = parse_student_courses(taken_file)
	(uuids, courses, uuid_to_course, course_to_uuid) = parse_declaration_reqs(defs_file)

	# analyze_degree_by_intro(AB, uuids)
	# analyze_degree_by_intro(SCB, uuids)
	# analyze_pathway_by_intro(AB, uuids, num_pathways=1)
	# analyze_pathway_by_intro(SCB, uuids, num_pathways=2)


	# analyze_pathways(AB, uuids, num_pathways=1)
	# analyze_pathways(SCB, uuids, num_pathways=2)
	# analyze_intro_by_degree(AB, SCB, uuids)

	# pathways_touched_by_intro(AB, uuids, courses)
	# pathways_touched_by_intro(SCB, uuids, courses)

if __name__ == '__main__':
	main()