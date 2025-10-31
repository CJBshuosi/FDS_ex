# Raft Consensus Algorithm - Code Explanation

## Overview
This code implements a **Raft consensus algorithm** - a distributed system where multiple nodes elect a leader to coordinate decisions.

---

## 1. Global Variables (Lines 6-8)

```python
nodes = []                    # List of all nodes in the system
buffer = {}                   # Message queue for each node
# msg_type: "heartbeat", "candidacy", "vote"
```

**Simple explanation:**
- `nodes`: Stores all the nodes (like a list of computers)
- `buffer`: Each node has a message queue to receive messages from other nodes
- Three types of messages: heartbeat (leader is alive), candidacy (I want to be leader), vote (I support you)

---

## 2. Node Class - Initialization (Lines 10-21)

```python
class Node:
    def __init__(self, id):
        self.id = id                    # Unique identifier
        self.state = 'follower'         # Default state: follower
        self.working = True             # Is the node active?
        self.last_heartbeat = time.time()  # When did we last hear from leader?
        self.resigned = 0               # Cooldown timer for re-election
        self.election = False           # Is an election happening?
        self.voted = False              # Have I voted in this election?
        self.votes = {}                 # Count votes for each candidate
        self.leader = None              # Who is the current leader?
```

**Simple explanation:**
- Each node starts as a **follower** (not a leader)
- Tracks when the last heartbeat was received
- Prevents nodes from immediately re-running elections (cooldown)
- Keeps track of votes during elections

---

## 3. Node States

A node can be in one of three states:

| State | Meaning |
|-------|---------|
| **follower** | Waiting for leader's heartbeat |
| **candidate** | Trying to become leader (running for election) |
| **leader** | Won the election, sends heartbeats to others |

---

## 4. Main Loop - `run()` Method (Lines 32-67)

### Step 1: Process Messages (Lines 34-36)
```python
while buffer[self.id]:
    msg_type, value = buffer[self.id].pop(0)
    if self.working: self.deliver(msg_type, value)
```
**Explanation:** Check if there are any messages waiting. If yes, process them one by one.

### Step 2: Check for Leader Timeout (Lines 39-44)
```python
if self.working and self.state == 'follower' and time.time() - self.last_heartbeat > 1:
    if time.time() - self.resigned > 5:  # Wait 5 seconds before re-running
        self.state = 'candidate'         # Become a candidate
        self.votes = {}                  # Reset vote count
        self.voted = False               # Reset vote flag
        self.leader = None               # Forget old leader
```
**Explanation:** 
- If I'm a follower and haven't heard from the leader in 1 second → become a candidate
- But wait 5 seconds after losing an election before trying again (prevents chaos)

### Step 3: Candidate Behavior (Lines 46-62)
```python
if self.working and self.state == 'candidate':
    if self.election:
        # Already running election - wait 2 seconds to collect votes
        time.sleep(2)
        if self.votes[self.id] > self.count_active_nodes() // 2:
            self.state = 'leader'  # Won! Become leader
    else:
        # Not running election yet
        time.sleep(random.uniform(1, 3))  # Wait random time
        # Check if another candidate appeared
        if other_candidate_found:
            self.state = 'follower'  # Give up, follow them
        else:
            self.election = True     # Start election
            self.broadcast('candidacy', self.id)  # Ask for votes
```
**Explanation:**
- If running election: wait for votes, check if I got majority
- If not running election: wait random time, then start election
- If another candidate appears: give up and become follower

### Step 4: Leader Behavior (Lines 65-66)
```python
if self.working and self.state == 'leader' and time.time() - self.last_heartbeat >= 0.5:
    self.broadcast('heartbeat', self.id)
```
**Explanation:** Every 0.5 seconds, send heartbeat to all nodes to prove I'm still alive.

---

## 5. Message Handling - `deliver()` Method (Lines 86-114)

### Heartbeat Message (Lines 87-93)
```python
if msg_type == 'heartbeat':
    self.last_heartbeat = time.time()  # Update last heartbeat time
    self.state = 'follower'            # I'm following this leader
    self.leader = value                # Remember who the leader is
```
**Explanation:** When I receive a heartbeat, I know the leader is alive, so I become a follower.

### Candidacy Message (Lines 94-98)
```python
elif msg_type == 'candidacy':
    if not self.voted:                 # Haven't voted yet?
        self.broadcast('vote', (self.id, value))  # Vote for this candidate
        self.voted = True              # Mark that I voted
```
**Explanation:** When someone asks for votes, I vote for them (if I haven't voted yet).

### Vote Message (Lines 99-114)
```python
elif msg_type == 'vote':
    voter_id, candidate_id = value
    self.votes[candidate_id] += 1      # Count the vote
    if self.votes[candidate_id] > self.count_active_nodes() // 2:
        self.leader = candidate_id     # This candidate won!
```
**Explanation:** Count votes. If someone gets majority, they're the new leader.

---

## 6. Helper Methods

### `broadcast()` - Send message to all nodes (Lines 69-72)
```python
def broadcast(self, msg_type, value):
    for node in nodes:
        buffer[node.id].append((msg_type, value))
```
**Explanation:** Send a message to every node's message queue.

### `crash()` - Simulate node failure (Lines 74-78)
```python
def crash(self):
    self.working = False
    self.state = 'crashed'
    buffer[self.id] = []  # Clear messages
```
**Explanation:** Turn off the node (simulate a computer crash).

### `recover()` - Restart a crashed node (Lines 80-84)
```python
def recover(self):
    self.working = True
    self.state = 'follower'
    buffer[self.id] = []
```
**Explanation:** Turn the node back on and reset it to follower state.

---

## 7. Main Program (Lines 122-138)

```python
if __name__ == "__main__":
    N = 3                    # Create 3 nodes
    initialize(N)            # Start all nodes
    time.sleep(6)            # Wait for election to complete
    
    # Interactive menu
    while True:
        act = input('$ ')
        if act == 'crash':   # Crash a node
        if act == 'recover': # Recover a node
        if act == 'state':   # Show all node states
```
**Explanation:** 
- Create 3 nodes and start them
- Wait 6 seconds for them to elect a leader
- Then let user crash/recover nodes or check their states

---

## How It Works - Example Scenario

1. **Start**: 3 nodes start as followers
2. **Timeout**: After 1 second with no heartbeat, node 0 becomes candidate
3. **Election**: Node 0 asks for votes
4. **Voting**: Nodes 1 and 2 vote for node 0
5. **Leader**: Node 0 gets 2 votes (majority of 3), becomes leader
6. **Heartbeat**: Node 0 sends heartbeat every 0.5 seconds
7. **Crash**: If node 0 crashes, nodes 1 and 2 timeout and start new election
8. **Recovery**: If node 0 recovers, it becomes follower again

---

## Key Concepts

- **Majority**: Need more than half the votes to become leader
- **Heartbeat**: Proves the leader is alive
- **Timeout**: If no heartbeat for 1 second, start new election
- **Cooldown**: Wait 5 seconds after losing election before trying again
- **Voting**: Each node votes only once per election

