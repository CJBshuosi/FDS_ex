# Code Execution Flow - Function Calls

## 📊 Overview

This document shows the complete execution flow of the Raft Consensus Algorithm code, including which functions are called at each step.

---

## 🚀 Phase 1: Initialization

```
main()
  ↓
os.system('clear')                    # Clear screen
  ↓
initialize(N=3)                       # Create 3 nodes
  ↓
  for i in range(3):
    Node(i)                           # Create node with id=0,1,2
      ↓
      __init__(id)                    # Initialize node
        - buffer[id] = []
        - self.state = 'follower'
        - self.last_heartbeat = time.time()
        - self.voted = False
        - self.votes = {}
        - self.leader = None
  ↓
  for node in nodes:
    node.start()                      # Start each node
      ↓
      threading.Thread(target=self.run, daemon=True).start()
        ↓
        node.run()                    # Enter main loop (in separate thread)
```

---

## 🔄 Phase 2: Main Loop - run() Method

The `run()` method is the heart of the algorithm. It runs continuously in a loop:

```
while True:
  ├─ Step 1: Process Messages
  │   while buffer[self.id]:
  │     msg_type, value = buffer[self.id].pop(0)
  │     if self.working:
  │       deliver(msg_type, value)    # Process message
  │
  ├─ Step 2: Check Follower Timeout
  │   if self.state == 'follower' and time.time() - self.last_heartbeat > 1:
  │     if time.time() - self.resigned > 5:
  │       self.state = 'candidate'
  │       self.votes = {}
  │       self.voted = False
  │       self.leader = None
  │
  ├─ Step 3: Handle Candidate State
  │   if self.state == 'candidate':
  │     if self.election:
  │       time.sleep(2)
  │       if self.votes[self.id] > count_active_nodes() // 2:
  │         self.state = 'leader'
  │         broadcast('heartbeat', self.id)
  │     else:
  │       time.sleep(random.uniform(1, 3))
  │       for msg in buffer[self.id]:
  │         if msg_type == 'candidacy' and value != self.id:
  │           self.state = 'follower'
  │           self.resigned = time.time()
  │       if self.state == 'candidate':
  │         self.election = True
  │         broadcast('candidacy', self.id)
  │
  ├─ Step 4: Handle Leader State
  │   if self.state == 'leader' and time.time() - self.last_heartbeat >= 0.5:
  │     broadcast('heartbeat', self.id)
  │
  └─ Step 5: Sleep and Loop
      time.sleep(0.1)
      # Go back to Step 1
```

---

## 💬 Phase 3: Message Processing - deliver() Method

When a message is received, the `deliver()` method processes it:

### Message Type 1: HEARTBEAT
```
deliver('heartbeat', leader_id)
  ├─ self.last_heartbeat = time.time()
  ├─ if self.state == 'candidate' or self.leader == None:
  │   ├─ self.state = 'follower'
  │   ├─ self.leader = leader_id
  │   └─ self.election = False
  └─ print(f'node {self.id} got a heartbeat and followed node {leader_id}')
```

### Message Type 2: CANDIDACY
```
deliver('candidacy', candidate_id)
  ├─ if not self.voted:
  │   ├─ broadcast('vote', (self.id, candidate_id))
  │   ├─ self.voted = True
  │   └─ print(f'node {self.id} voted to node {candidate_id}')
  └─ else:
      # Already voted, ignore
```

### Message Type 3: VOTE
```
deliver('vote', (voter_id, candidate_id))
  ├─ if candidate_id in self.votes:
  │   └─ self.votes[candidate_id] += 1
  ├─ else:
  │   └─ self.votes[candidate_id] = 1
  ├─ if self.votes[candidate_id] > count_active_nodes() // 2 and self.leader == None:
  │   ├─ self.leader = candidate_id
  │   └─ print(f'node {self.id} detected node {candidate_id} as leader')
  └─ # Continue
```

---

## 📡 Phase 4: Broadcasting - broadcast() Method

When a node needs to send a message to all other nodes:

```
broadcast(msg_type, value)
  ├─ if self.working:
  │   └─ for node in nodes:
  │       └─ buffer[node.id].append((msg_type, value))
  └─ # Message added to all nodes' buffers
```

**Called by:**
- `run()` when becoming leader: `broadcast('heartbeat', self.id)`
- `run()` when starting election: `broadcast('candidacy', self.id)`
- `deliver()` when voting: `broadcast('vote', (self.id, candidate_id))`

---

## 🔧 Helper Methods

### count_active_nodes()
```
count_active_nodes()
  └─ return sum(1 for node in nodes if node.working)
```
**Purpose:** Count how many nodes are still active (not crashed)
**Used by:** `run()` to check if candidate has majority votes

### crash()
```
crash()
  ├─ if self.working:
  │   ├─ self.working = False
  │   ├─ self.state = 'crashed'
  │   └─ buffer[self.id] = []
  └─ # Node is now offline
```
**Called by:** User input in main loop

### recover()
```
recover()
  ├─ if not self.working:
  │   ├─ buffer[self.id] = []
  │   ├─ self.state = 'follower'
  │   └─ self.working = True
  └─ # Node is back online
```
**Called by:** User input in main loop

---

## 📋 Complete Function Call Sequence

### Scenario: 3-Node Election

```
T=0s:
  main()
    → initialize(3)
      → Node(0).__init__()
      → Node(1).__init__()
      → Node(2).__init__()
      → node0.start() → node0.run() [Thread 1]
      → node1.start() → node1.run() [Thread 2]
      → node2.start() → node2.run() [Thread 3]

T=1s (Node 0 times out):
  [Thread 1] node0.run()
    → Check: time.time() - last_heartbeat > 1 ✓
    → self.state = 'candidate'
    → self.election = False
    → time.sleep(random.uniform(1, 3))

T=2s (Node 0 starts election):
  [Thread 1] node0.run()
    → self.election = True
    → broadcast('candidacy', 0)
      → buffer[0].append(('candidacy', 0))
      → buffer[1].append(('candidacy', 0))
      → buffer[2].append(('candidacy', 0))

T=2.1s (Node 1 receives candidacy):
  [Thread 2] node1.run()
    → while buffer[1]: ✓
      → deliver('candidacy', 0)
        → if not self.voted: ✓
          → broadcast('vote', (1, 0))
            → buffer[0].append(('vote', (1, 0)))
            → buffer[1].append(('vote', (1, 0)))
            → buffer[2].append(('vote', (1, 0)))
          → self.voted = True

T=2.2s (Node 2 receives candidacy):
  [Thread 3] node2.run()
    → while buffer[2]: ✓
      → deliver('candidacy', 0)
        → if not self.voted: ✓
          → broadcast('vote', (2, 0))
            → buffer[0].append(('vote', (2, 0)))
            → buffer[1].append(('vote', (2, 0)))
            → buffer[2].append(('vote', (2, 0)))
          → self.voted = True

T=2.3s (Node 0 receives votes):
  [Thread 1] node0.run()
    → while buffer[0]: ✓
      → deliver('vote', (1, 0))
        → self.votes[0] = 1
      → deliver('vote', (2, 0))
        → self.votes[0] = 2
    → Check: self.votes[0] > count_active_nodes() // 2
      → 2 > 1 ✓
      → self.state = 'leader'
      → broadcast('heartbeat', 0)
        → buffer[0].append(('heartbeat', 0))
        → buffer[1].append(('heartbeat', 0))
        → buffer[2].append(('heartbeat', 0))

T=2.4s (Nodes 1 and 2 receive heartbeat):
  [Thread 2] node1.run()
    → while buffer[1]: ✓
      → deliver('heartbeat', 0)
        → self.last_heartbeat = time.time()
        → self.state = 'follower'
        → self.leader = 0

  [Thread 3] node2.run()
    → while buffer[2]: ✓
      → deliver('heartbeat', 0)
        → self.last_heartbeat = time.time()
        → self.state = 'follower'
        → self.leader = 0

T=2.9s (Node 0 sends heartbeat again):
  [Thread 1] node0.run()
    → Check: time.time() - last_heartbeat >= 0.5 ✓
      → broadcast('heartbeat', 0)
        → buffer[0].append(('heartbeat', 0))
        → buffer[1].append(('heartbeat', 0))
        → buffer[2].append(('heartbeat', 0))

... (System stable, heartbeats continue every 0.5s)
```

---

## 🎯 Key Function Relationships

```
main()
  ├─ initialize()
  │   ├─ Node.__init__()
  │   └─ node.start()
  │       └─ node.run() [Main Loop]
  │           ├─ deliver()
  │           │   ├─ broadcast()
  │           │   └─ count_active_nodes()
  │           ├─ broadcast()
  │           └─ count_active_nodes()
  │
  ├─ time.sleep(6)
  │
  └─ while True:
      ├─ input()
      ├─ nodes[id].crash()
      ├─ nodes[id].recover()
      └─ print node states
```

---

## ⏱️ Timing of Function Calls

| Time | Function | Action |
|------|----------|--------|
| 0s | initialize() | Create nodes |
| 0s | node.start() | Start threads |
| 0s | node.run() | Enter main loop |
| 1s | run() | Follower timeout |
| 1s | broadcast('candidacy') | Request votes |
| 1.1s | deliver('candidacy') | Receive candidacy |
| 1.1s | broadcast('vote') | Send vote |
| 1.2s | deliver('vote') | Receive vote |
| 1.3s | broadcast('heartbeat') | Become leader |
| 1.4s | deliver('heartbeat') | Receive heartbeat |
| 1.9s | broadcast('heartbeat') | Send heartbeat |
| 2.4s | broadcast('heartbeat') | Send heartbeat |

---

## 📝 Summary

**Main Functions:**
1. `main()` - Program entry point
2. `initialize()` - Create and start nodes
3. `run()` - Main loop (runs in thread)
4. `deliver()` - Process messages
5. `broadcast()` - Send messages to all nodes
6. `count_active_nodes()` - Count active nodes
7. `crash()` - Simulate node failure
8. `recover()` - Restart crashed node

**Call Frequency:**
- `run()` - Continuous (every 0.1s)
- `deliver()` - When messages arrive
- `broadcast()` - When sending messages
- `count_active_nodes()` - When checking majority
- `crash()` / `recover()` - User input only

