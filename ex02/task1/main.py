import os
import time
import threading
import random

nodes = []  # Global list to store all node instances
buffer = {}  # Global message buffer: {node_id: [(msg_type, value), ...]}
# Message types: "heartbeat" (leader alive), "candidacy" (vote request), "vote" (vote response)

class Node:
    def __init__(self, id):
        buffer[id] = []
        self.id = id
        self.working = True
        self.state = 'follower'
        self.last_heartbeat = time.time()  # Timestamp of last heartbeat received
        self.resigned = 0  # Timestamp to prevent immediate re-election (5-second cooldown)
        self.election = False  # Flag: is election in progress
        self.voted = False  # Flag: has this node voted in current election
        self.votes = {}  # Dictionary to count votes: {candidate_id: vote_count}
        self.leader = None  # ID of current leader

    def start(self):
        print(f'node {self.id} started')
        threading.Thread(target=self.run, daemon=True).start()

    def count_active_nodes(self):  # Count number of working nodes (for majority calculation)
        return sum(1 for node in nodes if node.working)

    def run(self):
        while True:
            # Process all messages in buffer
            while buffer[self.id]:
                msg_type, value = buffer[self.id].pop(0)
                if self.working:
                    self.deliver(msg_type, value)

            # Check for heartbeat timeout
            if self.working and self.state == 'follower' and time.time() - self.last_heartbeat > 1:  # If no heartbeat for 1 second
                if time.time() - self.resigned > 5:  # If 5-second cooldown has passed
                    self.votes = {}
                    self.voted = False
                    self.leader = None
                    self.state = 'candidate'  # Transition to candidate state

            # Handle election
            if self.working and self.state == 'candidate':  # If node is a candidate
                if self.election:  # If election is in progress
                    time.sleep(2)  # Wait 2 seconds to collect votes
                    if self.id in self.votes and self.votes[self.id] > self.count_active_nodes() // 2:
                        self.state = 'leader'
                        self.election = False 
                        self.broadcast('heartbeat', self.id)
                else:  # Election not yet started
                    time.sleep(random.uniform(1, 3))  # Wait random time (1-3 seconds) to avoid simultaneous elections
                    for msg_type, value in buffer[self.id]:  #  buffer is like [[('candidacy', 0), ('candidacy', 1)], [('vote', (0, 1))]]
                        if msg_type == 'candidacy' and value != self.id:  # If received candidacy from another node
                            self.state = 'follower'
                            self.resigned = time.time()
                    if self.state == 'candidate':  # If still candidate after random wait
                        print(f'node {self.id} is starting an election')
                        self.election = True
                        self.broadcast('candidacy', self.id)  # Request votes from all nodes

            # Send heartbeat periodically
            if self.working and self.state == 'leader' and time.time() - self.last_heartbeat >= 0.5:  # If leader and 0.5 seconds passed
                self.broadcast('heartbeat', self.id)  # Send heartbeat to all nodes

            time.sleep(0.1)

    def broadcast(self, msg_type, value):  # Send message to all nodes
        if self.working:
            for node in nodes:
                buffer[node.id].append((msg_type, value))  # Add message to node's buffer

    def crash(self):  # Simulate node crash
        if self.working:
            self.working = False
            self.state = 'crashed'
            buffer[self.id] = []

    def recover(self):  # Recover from crash
        if not self.working:
            buffer[self.id] = []
            self.state = 'follower'
            self.working = True

    def deliver(self, msg_type, value):  # Process received message based on type
        if msg_type == 'heartbeat':
            self.last_heartbeat = time.time()  # Update last heartbeat timestamp
            if self.state == 'candidate' or self.leader == None:  # If candidate or no leader known
                self.state = 'follower'
                print(f'node {self.id} got a heartbeat and followed node {value}')
                self.leader = value
                self.election = False

        elif msg_type == 'candidacy':  # Handle candidacy message (vote request)
            if not self.voted:
                self.broadcast('vote', (self.id, value))  # Send vote for this candidate
                self.voted = True
                print(f'node {self.id} voted to node {value}')

        elif msg_type == 'vote':  # Handle vote message
            voter_id, candidate_id = value
            if candidate_id in self.votes:  # If already have votes for this candidate
                self.votes[candidate_id] += 1  # Increment vote count
            else:  # First vote for this candidate
                self.votes[candidate_id] = 1

            # Check if candidate has majority votes
            if self.votes[candidate_id] > self.count_active_nodes() // 2 and self.leader == None:  # If majority reached and no leader yet
                print(f'node {self.id} detected node {candidate_id} as leader')
                self.leader = candidate_id

def initialize(N):
    global nodes 
    nodes = [Node(i) for i in range(N)]  # Create N nodes with IDs 0 to N-1
    for node in nodes:
        node.start()  # Start the node's main loop in a daemon thread

if __name__ == "__main__":
    os.system('clear')
    N = 3
    initialize(N)  # Initialize and start all nodes
    time.sleep(6)  # Wait 6 seconds for nodes to elect a leader
    print('actions: state, crash, recover')

    while True:
        act = input('\t$ ')

        if act == 'crash':  # Crash a node
            id = int(input('\tid > '))
            if 0 <= id and id < N:
                nodes[id].crash()

        elif act == 'recover':  # Recover a crashed node
            id = int(input('\tid > '))
            if 0 <= id and id < N:
                nodes[id].recover()

        elif act == 'state':  # Print state of all nodes
            for node in nodes:
                print(f'\t\tnode {node.id}: {node.state}')

