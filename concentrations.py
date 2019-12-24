import json
from collections import defaultdict

def create_courses_dicts(file):
    # list of dictionaries
    # each dictionary corresponds to a course taken by a student
    read_file = open(file, "r")
    student_data = json.load(read_file)

    # dictionaries
    # student_ID: list of courses taken
    SCB = defaultdict(list)
    AB = defaultdict(list)

    for student_course in student_data:
        deg = student_course['degree_short']
        student_id = student_course['declaration_uuid']

        # choose the degree dictionary to use
        if deg == "Sc.B.":
            use_dict = SCB
        elif deg == "A.B.":
            use_dict = AB
        else:
            raise Exception("Unknown degree: " + deg)

        # store course entry in dictionary
        use_dict[student_id].append(student_course)

    read_file.close()
    return(SCB, AB)

def create_category_dict(req_list, title):
    if 'requirement_definitions' in req_list[0]:
        return create_category_dict(req_list[0]['requirement_definitions'], req_list[0]['title'])
    else:
        uuids = []
        courses = []
        for req in req_list:
            uuids.append(req['requirement_uuid'])
            courses.append(req['title'])
        return uuids, courses

def parse_spec(spec):
    uuids_dict = {}
    courses_dict = {}
    requirements = spec['requirement_definitions_json']
    for req in requirements:
        if req['title'] == "Calculus Prerequisite":
            pass
            # uuids, courses = create_category_dict([req], req['title'])
            # uuids_dict[req['title']] = uuids
            # courses_dict[req['title']] = courses
        elif req['title'] == "Introductory Courses":
            intro_uuids_dict = {}
            intro_courses_dict = {}
            for sequence in req['requirement_definitions'][0]['requirement_definitions']:
                uuids, courses = create_category_dict([sequence], sequence['title'])
                intro_uuids_dict[sequence['title']] = uuids
                intro_courses_dict[sequence['title']] = courses
            uuids_dict[req['title']] = intro_uuids_dict
            courses_dict[req['title']] = intro_courses_dict           
        elif req['title'] == "Intermediate Courses":
            pass
        elif req['title'] == "Pathways":
            pass
        elif req['title'] == "Additional Courses":
            print(req)
            pass

def process_defs(file):
    read_file = open(file, "r")
    defs = json.load(read_file)

    # create dictionary of program terms to program plans
    degree_reqdicts = {}
    for d in defs:
        # skipping the professional tracks
        if not d['track_code']:
            tag = d['degree_short'] + d['term_id']
            if tag == 'A.B.201720': # REMOVE
                spec = parse_spec(d)
    read_file.close()
    return degree_reqdicts


def main():
    taken_file = "COMP courses taken.json"
    defs_file = "COMP program defs.json"

    (SCB, AB) = create_courses_dicts(taken_file)
    degree_reqdicts = process_defs(defs_file)

    list_AB = list(AB)
    student = AB[list_AB[0]]
    # print(student_plan(student, degree_reqdicts))



if __name__ == "__main__":
    main()

# req_ids is the box id
# which pathways are people doing; which courses are they taking over; which intro sequences
# **** 79% of ABs are doing ML/AI
# there's like 10 pathways now
# also see what courses people are taking; there will be some odd struggling
# self-designed pathways? not processed - maybe just skip
# how many people are taking both 32 and 33? but likely in the ScB