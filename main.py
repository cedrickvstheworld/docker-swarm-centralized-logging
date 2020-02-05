import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from dateutil.parser import  parse
import pytz
time_zone = pytz.timezone('Asia/Manila')
import container_inspect
from glob import glob
from sty import fg, Style, RgbFg
from random import randint
from threading import Thread

path = '/var/lib/docker/containers/'

# containers data
container_path_list = glob(path + '*')
running_containers = []
running_containers_data = []
for i in container_path_list:
    id = i.split('/')[-1]
    state = container_inspect.check_this_out(id, '.State')
    if not state['Running']:
        continue
    labels = container_inspect.check_this_out(id, '.Config.Labels')
    container_name = ''
    initial_logs = ''
    try:
        name = labels['com.docker.swarm.service.name']
    except:
        name = container_inspect.check_this_out(id, '.Name')
    # get initial logs
    try:
        log_file = '%s%s/%s-json.log' % (path, id, id)
        with open(log_file, 'r+') as file:
            content = file.read()
            initial_logs += content
    except:
        pass
    running_containers.append(id)
    # just some text color
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    fg.color = Style(RgbFg(r, g, b))
    name = fg.color + name.capitalize() + fg.rs
    running_containers_data.append({"id": id, "name": name, "initial_logs": initial_logs})

def line_formater(line, container_name):
    try:
        parsed = json.loads(line)
        time = parse(parsed['time']).astimezone(time_zone)
        milliseconds = int(round(time.strptime(time.strftime('%d.%m.%Y %H:%M:%S,%f'), '%d.%m.%Y %H:%M:%S,%f').timestamp() * 1000))
        return ['%s %s | %s' % (container_name, parsed["log"].split('\n')[0], time.strftime('%H:%M:%S %Y-%m-%d')), milliseconds]
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

displayed_logs = ''
initial_logs_list = initial_logs_raw.split('\n')
for i in initial_logs_list:
    line = json.loads(i)



class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        print('wowowowoww')
        print(event.src_path)
    def on_created(self, event):
        print('here')
        print(event.src_path)
        # if not event.is_directory:
        #     src = event.src_path.split('~')[0]
        #     print(src)
        #     # with open(src, 'r+') as file:
        #     #     content = file.read()
        #     #     content = json.loads(content)
        #     #     time = parse(content['time']).astimezone(time_zone)
        #     #     readable_date = time.strftime('%d.%m.%Y %H:%M:%S,%f')
        #     #     milliseconds = time.strptime(readable_date, '%d.%m.%Y %H:%M:%S,%f').timestamp() * 1000
        #     #     print(int(round(milliseconds)))
        #     #     print(readable_date)

event_hander = Handler()
observer = Observer()
observer.schedule(event_hander, path=path, recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
