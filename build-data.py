import json
from collections import defaultdict

# TODO
# figure out why self-designed pathways aren't getting picked up in program defs

# -- Create dicts with each student's courses --

# data is a list of dictionaries
# each dictionary corresponds to a course taken by a student
with open("COMP courses taken.json", "r") as read_file:
    studentdata = json.load(read_file)

# SCB and AB will be dictionaries mapping student IDs
# to the courses they have taken
SCB = defaultdict(list)
AB = defaultdict(list)

for studcourse in studentdata:
    deg = studcourse["degree_short"]
    studid = studcourse["declaration_uuid"]

    # choose the degree dictionary to use
    if deg == "Sc.B.":
        use_dict = SCB
    elif deg == "A.B.":
        use_dict = AB
    else:
        raise Exception("unknown degree " + deg)

    # store studcourse entry in dictionary
    use_dict[studid].append(studcourse)

# -- Create dicts mapping program IDs to requirements --

# read in the json file of program definitions
with open("COMP program defs.json", "r") as read_file:
    defs = json.load(read_file)


def blank_plan():
    'Create a blank plan of courses for an individual student'
    return {'intro': [],
            'intermed': [],
            'pathways': [],
            'additional': [],
            'capstone': []}

def register_course_ids(req_dict, id_list):
    if 'requirement_definitions' in req_dict:
        # append the ids from digging into each of those req defns
        for rd in req_dict['requirement_definitions']:
            register_course_ids(rd, id_list)
    else: # at a bottom-level requirement
        id_list.append(req_dict['requirement_uuid'])


def parse_planspec(spec: dict) -> dict:
    '''parse one program plan specification into a summary of the
        id numbers that go with each category of requirements
    '''
    specmap = blank_plan()
    for req in spec['requirement_definitions_json']:
        if req['title'] == "Calculus Prerequisite":
            print("ignoring calc")
        elif req['title'] == "Introductory Courses":
            #print("found intro")
            register_course_ids(req, specmap['intro'])
        elif req['title'] == "Intermediate Courses":
            #print("found intermed")
            register_course_ids(req, specmap['intermed'])
        elif req['title'] == "Pathways":
            #print("found pathways")
            for pway_dict in req['requirement_definitions'][0]['requirement_definitions']:
                pway_id_list = []
                pway_tuple = [pway_dict['title'], pway_id_list]
                for pway_group in pway_dict['requirement_definitions']:
                    if pway_group['title'] in ['Core Courses', 'Related Courses']:
                        register_course_ids(pway_group, pway_id_list)
                specmap['pathways'].append(pway_tuple)
        elif req['title'] == "Additional Courses":
            #print("found additional")
            register_course_ids(req, specmap['additional'])
        elif req['title'] == "Capstone Course":
            #print("found capstone")
            register_course_ids(req, specmap['capstone'])
        else: raise Exception("unknown top-level req " + req['title'])
    return specmap



def create_reqid_dict(specmap: dict) -> dict:
    '''convert a mapping from requirement areas to ids into one
        from ids into requirement areas.
        EVENTUALLY: Optimize this to happen within parse_planspec
    '''
    id_dict = {}
    for category in list(specmap.keys()):
        if category == 'pathways':
            for plist in specmap[category]:
                for id in plist[1]:
                    id_dict[id] = (plist[0] + "-Pathway")
        else:
            #print('processing ' + category)
            for id in specmap[category]: id_dict[id] = category
    return id_dict


# create dictionary of program terms to program plans
# skipping the professional tracks
degree_reqdicts = {}

for d in defs:
    if d['track_code'] == None:
        tag = d['degree_short'] + d['term_id']
        spec = parse_planspec(d)  # parse the definition plan into requirement areas
        req_dict = create_reqid_dict(spec) # map the requirement slots to their areas
        degree_reqdicts[tag] = req_dict

# ABspec1 = parse_planspec(defs[0])
# ABids = create_reqid_dict(ABspec1)

# -- Create dicts with each student's declaration content --

def student_plan(for_stud) -> dict:
    d = for_stud[0]
    print("processing student ") # + d['declaration_uuid'])
    if d['term_id'] == '201820':
        req_dict = degree_reqdicts[d['degree_short'] + '201810']
    else:
        req_dict = degree_reqdicts[d['degree_short'] + d['term_id']]
    plan = blank_plan()
    for course_dict in for_stud:
        course_name = course_dict['subject_code'] + course_dict['course_number']
        #print(course_name)
        if course_dict['requirement_uuid'] in req_dict:
            # print('found id for ' + course_name)
            req_tag = req_dict[course_dict['requirement_uuid']]
            # add the requirement tag to the plan dictionary. This needs to happen
            # the first time each pathway is encountered
            if req_tag in plan:
                plan[req_tag].append(course_name)
            else:
                plan[req_tag] = [course_name]
        else:
            print('no id found for ' + course_name + ' (req_id ' + course_dict['requirement_uuid'] + ') for student ' + d['declaration_uuid'])
    return plan

# following is how we extract one student plan to try summarizing

print()

stud = student_plan(AB[list(AB)[0]])

#ABplans = [student_plan(AB(s)) for s in AB]

#print(student_plan(AB[list(AB)[0]]))
#print(student_plan(AB[list(AB)[1]]))
#print(student_plan(AB[list(AB)[2]]))
#print(student_plan(AB[list(AB)[3]]))
#print(student_plan(AB[list(AB)[4]]))
#print(student_plan(AB[list(AB)[5]]))
#print(student_plan(AB[list(AB)[6]]))
#print(student_plan(AB[list(AB)[7]]))

ABplans = []
for n in range(50):
    print(student_plan(AB[list(AB)[n]]))

#ABplans2 = [student_plan(AB(list(AB)[n])) for n in range(5)]
#print(ABplans2)
