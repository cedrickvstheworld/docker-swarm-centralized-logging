import subprocess
import json


def check_this_out(container_id, format_wild_card):
    result = subprocess.\
        check_output(['docker', 'inspect', container_id, '--format', "'{{json %s}}'" % format_wild_card])
    return json.loads(result.decode("utf-8")[1:-2])
