CRITICAL = 0.10

WARNING = 0.65

OKAY = 0.90
import json
import uuid
import threading
lock = threading.Lock()

def parse_json_playbook_output(output)-> str:
    str_output = str(output)
    print(str_output[2:-1], type(str_output[2:-1]))

    data = json.loads(str_output[2:-1]) 

    res = {'plays': []}
    for k in data['plays']:
    
        # wont work for nested tasks...
        # for task in k['tasks']:
        #     if task['task']['name'] == 'Gathering Facts':
                
        #         del task['hosts']
        res['plays'].append(k)
    res['stats'] = data['stats']
    #print(json.dumps(res,indent=4))


    # last task should be the output of the day-2 operation
    num_plays = len(res['plays']) - 1
    num_tasks = len(res['plays'][num_plays]['tasks']) - 1

    last_task = res['plays'][num_plays]['tasks'][num_tasks]

    for host_key in last_task['hosts']:
        host = last_task['hosts'][host_key]
        return host['msg']


def generate_action_id():
    # generate a random UUID and convert it to a string
    my_uuid = str(uuid.uuid4())
    return my_uuid


def update_object(old_obj, new_obj):
    # iterate over the attributes of the new object
    for attr, value in new_obj.__dict__.items():
        # skip the actionId attribute
        if attr == "actionId":
            continue
        # set the value of the attribute on the old object
        setattr(old_obj, attr, value)
    # return the updated object
    return old_obj