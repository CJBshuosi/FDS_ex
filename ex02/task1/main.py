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
        self.resigned = 0 # Later this will become a time so we can lock out new candidacy for a certain amount of time to stop overlapping elections
        self.election = False 
        self.voted = False # To prevent double voting
        self.votes = {} # To count votes received, so everyone can count for themselves
        self.leader = None

    def start(self):
        print(f'node {self.id} started')
        threading.Thread(target=self.run, daemon=True).start() # Make threads stop when exiting main program

    # Count active nodes, which is necessary to determine majority later on
    # We need to specifically look at nodes that are still working, as crashed nodes don't count
    def count_active_nodes(self):
        return sum(1 for node in nodes if node.working)

    def run(self):
        while True:
            while buffer[self.id]:
                msg_type, value = buffer[self.id].pop(0)
                if self.working: self.deliver(msg_type,value)
            
            # Check for heartbeat. If time since last heartbeat > 1s, switch to candidate state
            if self.working and self.state == 'follower' and time.time() - self.last_heartbeat > 1:
                if time.time() - self.resigned > 5: # prevent immediate re-candidacy
                    self.votes = {}
                    self.voted = False
                    self.leader = None
                    self.state = 'candidate'

            if self.working and self.state == 'candidate':
                if self.election:
                    time.sleep(2) # 2 seconds to collect votes
                    if self.votes[self.id] > self.count_active_nodes() // 2: # If received majority of votes
                        self.state = 'leader'
                        self.election = False
                        self.broadcast('heartbeat', self.id)
                else:
                    time.sleep(random.uniform(1, 3)) # wait for random time between 1s and 3s
                    for msg_type, value in buffer[self.id]:
                        if msg_type == 'candidacy' and value != self.id:
                            self.state = 'follower'
                            self.resigned = time.time() # prevent immediate re-candidacy
                    if self.state == 'candidate': # If still candidate, start election
                        print(f'node {self.id} is starting an election')
                        self.election = True
                        self.broadcast('candidacy', self.id)

            # If leader, send heartbeat every 0.5s
            if self.working and self.state == 'leader' and time.time() - self.last_heartbeat >= 0.5:
                self.broadcast('heartbeat', self.id)
            time.sleep(0.1)

    def broadcast(self, msg_type, value):
        if self.working:
            for node in nodes:
                buffer[node.id].append((msg_type,value))
    
    def crash(self):
        if self.working:
            self.working = False
            self.state = 'crashed' # set to crashed state
            buffer[self.id] = []
    
    def recover(self):
        if not self.working:
            buffer[self.id] = []
            self.state = 'follower' # reset to follower state
            self.working = True

    def deliver(self, msg_type, value):
        if msg_type == 'heartbeat':
            self.last_heartbeat = time.time()
            if self.state == 'candidate' or self.leader == None: 
                self.state = 'follower'
                print(f'node {self.id} got a heartbeat and followed node {value}')
                self.leader = value
                self.election = False
        elif msg_type == 'candidacy':
            if not self.voted:
                self.broadcast('vote', (self.id, value)) # vote for candidate
                self.voted = True
                print(f'node {self.id} voted to node {value}')
        elif msg_type == 'vote':
            voter_id, candidate_id = value
            if candidate_id in self.votes:
                self.votes[candidate_id] += 1
            else:
                self.votes[candidate_id] = 1
            """"There is multiple ways to determine the leader. Here each node counts votes for themselves and determines leader that way, 
            but it would also be possible to have the candidate count votes and announce themselves as leader through heartbeat.
            Candidate is only one who counts:
            if self.votes[candidate_id] > self.count_active_nodes() // 2 and self.leader == None and self.state == 'candidate':
            
            The way we coded it is that each node counts votes and can determine leader by themselves. See below:
            """
            if self.votes[candidate_id] > self.count_active_nodes() // 2 and self.leader == None:
                print(f'node {self.id} detected node {candidate_id} as leader')
                self.leader = candidate_id

def initialize(N):
    global nodes
    nodes = [Node(i) for i in range(N)]
    for node in nodes:
        node.start()

if __name__ == "__main__":
    os.system('clear')
    N = 3
    initialize(N)
    time.sleep(6) # Let nodes start up and elect a leader
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

