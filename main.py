#! /usr/bin/env python3
import argparse
import json
from dateutil.parser import  parse
import pytz
time_zone = pytz.timezone('Asia/Manila')
from glob import glob
from sty import fg, Style, RgbFg
from random import randint
import subprocess
import requests
from threading import Thread
import tailhead

# get catcher url
parser = argparse.ArgumentParser()
parser.add_argument("--c")
args = parser.parse_args()
catcher_url = args.c
if catcher_url == None:
    print('Error: provide event catcher url')
    quit()
    exit()

path = '/var/lib/docker/containers/'

def send_log_to_listener(log):
    requests.post(catcher_url, json={"log": log})

def check_this_out(container_id, format_wild_card):
    result = subprocess.\
        check_output(['docker', 'inspect', container_id, '--format', "'{{json %s}}'" % format_wild_card])
    return json.loads(result.decode("utf-8")[1:-2])

# containers data
container_path_list = glob(path + '*')
container_log_file_list = []
running_containers = []
running_containers_data = []
longest_name_length = 0
for i in container_path_list:
    id = i.split('/')[-1]
    state = check_this_out(id, '.State')
    if not state['Running']:
        continue
    labels = check_this_out(id, '.Config.Labels')
    container_name = ''
    initial_logs = ''
    try:
        name = labels['com.docker.swarm.service.name']
    except:
        name = check_this_out(id, '.Name')
    # get initial logs
    try:
        log_file = '%s%s/%s-json.log' % (path, id, id)
        container_log_file_list.append(log_file)
        with open(log_file, 'r+') as file:
            content = file.read()
            initial_logs += content
    except:
        content = ''
    # for visual pleasure
    name_length = len(name)
    if name_length > longest_name_length:
        longest_name_length = name_length
    running_containers_data.append({"id": id, "name": name, "initial_logs": initial_logs, "current_logs": content})
    running_containers.append(id)

# for visual pleasure
for i in running_containers_data:
    name = i["name"]
    spaces_to_be_added = longest_name_length - len(name)
    name += ' ' * spaces_to_be_added
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    fg.color = Style(RgbFg(r, g, b))
    i["name"] = fg.color + name.capitalize() + fg.rs

def line_formater(line, container_name):
    try:
        parsed = json.loads(line)
        time = parse(parsed['time']).astimezone(time_zone)
        milliseconds = int(round(time.strptime(time.strftime('%d.%m.%Y %H:%M:%S,%f'), '%d.%m.%Y %H:%M:%S,%f').timestamp() * 1000))
        actual_log = '%s | %s | %s' % (container_name, time.strftime('%H:%M:%S %Y-%m-%d'), parsed["log"].split('\n')[0])
        return [actual_log, milliseconds]
    except:
        return ['', 0]

initial_logs_raw = []
for i in running_containers_data:
    log_line_list = i["initial_logs"].split("{\"log")
    for ii in log_line_list:
        results = line_formater("{\"log" + ii, i["name"])
        if results[0] == '':
            continue
        initial_logs_raw.append({
            "log": '%s\n' % results[0],
            "ms": results[1]
        })

sorted_initial_logs = sorted(initial_logs_raw, key=lambda i: i['ms'])
display_initial_logs = ''
for i in sorted_initial_logs:
    display_initial_logs += i['log']
print(display_initial_logs)
send_log_to_listener(display_initial_logs)

def logging_thread(file):
    container_id = file.split('/')[-2]
    container_obj = (next((item for item in running_containers_data if item['id'] == container_id)))
    container_name = container_obj['name']
    for newlines in tailhead.follow_path(file):
        if newlines is not None:
            new_logs_batch = ''
            initial_logs_raw = []
            log_line_list = newlines.split("{\"log")
            for i in log_line_list:
                results = line_formater("{\"log" + i, container_name)
                if results[0] == '':
                    continue
                initial_logs_raw.append({
                    "log": results[0],
                    "ms": results[1]
                })
                for i in initial_logs_raw:
                    new_logs_batch += i['log']
                print(new_logs_batch)
                container_obj['current_logs'] = content
                send_log_to_listener(new_logs_batch)

for i in container_log_file_list:
    worker = Thread(target=logging_thread, args=(i,))
    worker.start()

"""
sudo ./main.py --c http://host-ip-address:6070/
"""
