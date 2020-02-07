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
5. Open flask server port in the vm for guest vm connections:
    ```bash
    $ sudo iptables -I INPUT -p tcp --dport 6070 -s $MACHINE_IPs -j ACCEPT
    ```
6. run the watcher in every nodes:
    ```bash
    $ sudo ./main.py --c http://localhost:6070/
    ```
### note:
    In my case, my docker-machines are ubuntu-servers running on virtual machines. If you are gonna use
    boot2docker vms, you will have a hard time installing python3 dependencies same with rancherOS.