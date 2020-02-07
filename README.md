# Centralized Logging for Docker Swarm

1. Nodes must have python3.*  and pip3 installed.
2. Clone the project in every swarm node.
3. Navigate to the project directory and install the dependencies:
    ```bash
    $ pip3 install -r requirements.txt
    ```
4. In the node where you wish to catch logs, probably in the master, run the catcher:
    ```bash
    $ export FLASK_APP=event_catcher.py
    $ python3 -m flask run --port=6070 --host=0.0.0.0
    ```
5. Open the flask server port in the vm for 
6. run the watcher in every nodes:
    ```bash
    $ sudo ./main.py --c http://localhost:8000/
    ```