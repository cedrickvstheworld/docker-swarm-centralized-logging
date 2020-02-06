# Centralized Logging for Docker Swarm

1. clone the project in every swarm node.
2. nodes must have python3.*  and pip3 installed.
3. run pip3 install in the project directory.
4. In the node where you wish to catch logs, probably in the master, run the catcher:
    ```bash
    $ export FLASK_APP=event_catcher.py
    $ python3 -m flask run --port=8000
    ```
5. run the watcher in every nodes:
    ```bash
    $ sudo ./main.py --c http://localhost:8000/
    ```