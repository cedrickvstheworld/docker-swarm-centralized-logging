#! /usr/bin/env python3
import argparse
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from dateutil.parser import  parse
import pytz
time_zone = pytz.timezone('Asia/Manila')
from glob import glob
from sty import fg, Style, RgbFg
from random import randint
import subprocess
import requests

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
        with open(log_file, 'r+') as file:
            content = file.read()
            initial_logs += content
    except:
        pass
    # for visual pleasure
    name_length = len(name)
    if name_length > longest_name_length:
        longest_name_length = name_length
    running_containers_data.append({"id": id, "name": name, "initial_logs": initial_logs})
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
    log_line_list = i["initial_logs"].split('\n')
    for ii in log_line_list:
        results = line_formater(ii, i["name"])
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

class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            src = event.src_path
            container_id = src.split('/')[-2]
            with open(src, 'r+') as file:
                content = file.read()
                line = content.split('\n')[-2]
                container_name = (next((item for item in running_containers_data if item['id'] == container_id)))['name']
                new_line = line_formater(line, container_name)[0]
                print(new_line)
                send_log_to_listener(new_line)

event_hander = Handler()
observer = Observer()
observer.schedule(event_hander, path=path, recursive=True)
observer.start()
try:
    while True:
        time.sleep(0.3)
except KeyboardInterrupt:
    observer.stop()
observer.join()

"""
sudo ./main.py --c http://host-ip-address:6070/
"""
