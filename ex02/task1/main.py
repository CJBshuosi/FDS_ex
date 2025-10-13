import os
import time
import threading
import random

nodes = []
buffer = {} # items are in the form 'node_id': [(msg_type, value)]
# msg_type: "heartbeat", "candidacy", "vote"

class Node:
    def __init__(self,id):
        buffer[id] = []
        self.id = id
        self.working = True
        self.state = 'follower' # follower is default state
        self.last_heartbeat = time.time() # time of last heartbeat received (start with current time)

    def start(self):
        print(f'node {self.id} started')
        threading.Thread(target=self.run, daemon=True).start() # Make threads stop when exiting main program

    def run(self):
        while True:
            while buffer[self.id]:
                msg_type, value = buffer[self.id].pop(0)
                if self.working: self.deliver(msg_type,value)
            
            # Check for heartbeat. If time since last heartbeat > 1s, switch to candidate state
            if self.working and self.state == 'follower' and time.time() - self.last_heartbeat > 1:
                if not self.resign: self.state = 'candidate'

            if self.working and self.state == 'candidate':
                time.sleep(random.uniform(1, 3)) # wait for random time between 1s and 3s
                print(f'node {self.id} is starting an election')

            # If leader, send heartbeat every 0.5s
            if self.working and self.state == 'leader':
                time.sleep(0.5) # leader sends heartbeat every 0.5s
                self.broadcast('heartbeat', time.time())
            time.sleep(0.1)

    def broadcast(self, msg_type, value):
        if self.working:
            for node in nodes:
                buffer[node.id].append((msg_type,value))
    
    def crash(self):
        if self.working:
            self.working = False
            self.state = 'follower' # reset to follower state
            buffer[self.id] = []
    
    def recover(self):
        if not self.working:
            buffer[self.id] = []
            self.working = True

    def deliver(self, msg_type, value):
        if msg_type == 'heartbeat':
            self.last_heartbeat = time.time()
            if self.state == 'candidate': self.state = 'follower' # Leader exists -> stop election process
            self.resign = False
        elif msg_type == 'candidacy':
            pass
        elif msg_type == 'vote':
            pass

def initialize(N):
    global nodes
    nodes = [Node(i) for i in range(N)]
    for node in nodes:
        node.start()
    # For testing, make node 0 the leader
    nodes[0].state = 'leader'

if __name__ == "__main__":
    os.system('clear')
    N = 3
    initialize(N)
    print('actions: state, crash, recover')
    while True:
        act = input('\t$ ')
        if act == 'crash' : 
            id = int(input('\tid > '))
            if 0<= id and id<N: nodes[id].crash()
        elif act == 'recover' : 
            id = int(input('\tid > '))
            if 0<= id and id<N: nodes[id].recover()
        elif act == 'state':
            for node in nodes:
                print(f'\t\tnode {node.id}: {node.state}')

