# Function Calls - English Explanation

## 🎯 All Functions in the Code

```
1. main()                    - Program entry point
2. initialize(N)             - Create N nodes
3. Node.__init__(id)         - Initialize a node
4. node.start()              - Start a node (create thread)
5. node.run()                - Main loop (runs in thread)
6. node.deliver(msg_type, value)  - Process a message
7. node.broadcast(msg_type, value) - Send message to all nodes
8. node.count_active_nodes() - Count active nodes
9. node.crash()              - Simulate node crash
10. node.recover()           - Restart crashed node
```

---

## 📊 Function Call Diagram

```
main()
  │
  ├─→ os.system('clear')
  │
  ├─→ initialize(3)
  │    │
  │    ├─→ Node(0).__init__()
  │    ├─→ Node(1).__init__()
  │    ├─→ Node(2).__init__()
  │    │
  │    ├─→ node0.start()
  │    │    └─→ threading.Thread(target=node0.run)
  │    │         └─→ node0.run() [Thread 1]
  │    │
  │    ├─→ node1.start()
  │    │    └─→ threading.Thread(target=node1.run)
  │    │         └─→ node1.run() [Thread 2]
  │    │
  │    └─→ node2.start()
  │         └─→ threading.Thread(target=node2.run)
  │              └─→ node2.run() [Thread 3]
  │
  ├─→ time.sleep(6)
  │
  └─→ while True:
       ├─→ input()
       ├─→ nodes[id].crash()
       ├─→ nodes[id].recover()
       └─→ print states
```

---

## 🔄 Main Loop - run() Function

The `run()` function is called once per node and runs continuously:

```
node.run()
  │
  ├─ STEP 1: Process Messages
  │   while buffer[self.id]:
  │     msg = buffer[self.id].pop(0)
  │     └─→ deliver(msg_type, value)
  │
  ├─ STEP 2: Check Follower Timeout
  │   if state == 'follower' and timeout > 1s:
  │     └─→ state = 'candidate'
  │
  ├─ STEP 3: Handle Candidate
  │   if state == 'candidate':
  │     if election started:
  │       └─→ count_active_nodes()
  │           └─→ if majority votes: state = 'leader'
  │               └─→ broadcast('heartbeat', self.id)
  │     else:
  │       └─→ broadcast('candidacy', self.id)
  │
  ├─ STEP 4: Handle Leader
  │   if state == 'leader' and 0.5s passed:
  │     └─→ broadcast('heartbeat', self.id)
  │
  └─ STEP 5: Sleep and Loop
      time.sleep(0.1)
      └─→ Go back to STEP 1
```

---

## 💬 Message Processing - deliver() Function

```
deliver(msg_type, value)
  │
  ├─ if msg_type == 'heartbeat':
  │   ├─ Update: last_heartbeat = time.time()
  │   ├─ if state == 'candidate' or leader == None:
  │   │   ├─ state = 'follower'
  │   │   └─ leader = value
  │   └─ print "got heartbeat"
  │
  ├─ elif msg_type == 'candidacy':
  │   ├─ if not voted:
  │   │   ├─→ broadcast('vote', (self.id, value))
  │   │   └─ voted = True
  │   └─ print "voted"
  │
  └─ elif msg_type == 'vote':
      ├─ Count vote: votes[candidate_id] += 1
      ├─→ count_active_nodes()
      ├─ if votes > majority:
      │   ├─ leader = candidate_id
      │   └─ print "detected leader"
      └─ continue
```

---

## 📡 Broadcasting - broadcast() Function

```
broadcast(msg_type, value)
  │
  ├─ if self.working:
  │   └─ for each node in nodes:
  │       └─ buffer[node.id].append((msg_type, value))
  │
  └─ Message is now in all nodes' message queues
```

**Called by:**
- `run()` when becoming leader
- `run()` when starting election
- `deliver()` when voting

---

## 🔧 Helper Functions

### count_active_nodes()
```
count_active_nodes()
  └─ return sum(1 for node in nodes if node.working)
```
**Purpose:** Count how many nodes are still active
**Returns:** Number of active nodes
**Used by:** `run()` and `deliver()` to check majority

### crash()
```
crash()
  ├─ if self.working:
  │   ├─ self.working = False
  │   ├─ self.state = 'crashed'
  │   └─ buffer[self.id] = []
  └─ Node is now offline
```
**Called by:** User input

### recover()
```
recover()
  ├─ if not self.working:
  │   ├─ buffer[self.id] = []
  │   ├─ self.state = 'follower'
  │   └─ self.working = True
  └─ Node is back online
```
**Called by:** User input

---

## ⏱️ Example: 3-Node Election Timeline

```
T=0s:
  main() → initialize(3)
    → Node(0).__init__()
    → Node(1).__init__()
    → Node(2).__init__()
    → node0.start() → node0.run() [Thread 1]
    → node1.start() → node1.run() [Thread 2]
    → node2.start() → node2.run() [Thread 3]

T=1s (Node 0 times out):
  [Thread 1] node0.run()
    → Check: time.time() - last_heartbeat > 1 ✓
    → state = 'candidate'

T=2s (Node 0 starts election):
  [Thread 1] node0.run()
    → broadcast('candidacy', 0)
      → buffer[0].append(('candidacy', 0))
      → buffer[1].append(('candidacy', 0))
      → buffer[2].append(('candidacy', 0))

T=2.1s (Node 1 receives candidacy):
  [Thread 2] node1.run()
    → deliver('candidacy', 0)
      → broadcast('vote', (1, 0))
        → buffer[0].append(('vote', (1, 0)))
        → buffer[1].append(('vote', (1, 0)))
        → buffer[2].append(('vote', (1, 0)))

T=2.2s (Node 2 receives candidacy):
  [Thread 3] node2.run()
    → deliver('candidacy', 0)
      → broadcast('vote', (2, 0))
        → buffer[0].append(('vote', (2, 0)))
        → buffer[1].append(('vote', (2, 0)))
        → buffer[2].append(('vote', (2, 0)))

T=2.3s (Node 0 receives votes):
  [Thread 1] node0.run()
    → deliver('vote', (1, 0))
      → votes[0] = 1
    → deliver('vote', (2, 0))
      → votes[0] = 2
    → count_active_nodes() → 3
    → Check: 2 > 3//2 (2 > 1) ✓
    → state = 'leader'
    → broadcast('heartbeat', 0)
      → buffer[0].append(('heartbeat', 0))
      → buffer[1].append(('heartbeat', 0))
      → buffer[2].append(('heartbeat', 0))

T=2.4s (Nodes 1 and 2 receive heartbeat):
  [Thread 2] node1.run()
    → deliver('heartbeat', 0)
      → last_heartbeat = time.time()
      → state = 'follower'
      → leader = 0

  [Thread 3] node2.run()
    → deliver('heartbeat', 0)
      → last_heartbeat = time.time()
      → state = 'follower'
      → leader = 0

T=2.9s (Node 0 sends heartbeat):
  [Thread 1] node0.run()
    → Check: time.time() - last_heartbeat >= 0.5 ✓
    → broadcast('heartbeat', 0)

... (System stable, heartbeats every 0.5s)
```

---

## 📋 Function Call Summary

| Function | Called By | Calls | Frequency |
|----------|-----------|-------|-----------|
| main() | System | initialize() | Once |
| initialize() | main() | Node.__init__(), start() | Once |
| __init__() | initialize() | None | N times |
| start() | initialize() | threading.Thread() | N times |
| run() | Thread | deliver(), broadcast(), count_active_nodes() | Continuous |
| deliver() | run() | broadcast(), count_active_nodes() | When messages arrive |
| broadcast() | run(), deliver() | None | When sending messages |
| count_active_nodes() | run(), deliver() | None | When checking majority |
| crash() | User input | None | On demand |
| recover() | User input | None | On demand |

---

## 🎯 Key Points

1. **main()** starts everything
2. **initialize()** creates nodes and starts threads
3. **run()** is the main loop (runs in each thread)
4. **deliver()** processes messages
5. **broadcast()** sends messages to all nodes
6. **count_active_nodes()** counts active nodes
7. **crash()** and **recover()** are user-controlled

---

## 💡 Understanding the Flow

**Initialization:**
```
main() → initialize() → Node.__init__() → start() → run()
```

**Main Loop (in each thread):**
```
run() → deliver() → broadcast() → count_active_nodes() → run()
```

**Message Processing:**
```
broadcast() → buffer → run() → deliver() → broadcast()
```

**State Transitions:**
```
Follower → (timeout) → Candidate → (majority) → Leader → (heartbeat) → Follower
```

---

## 🔍 Tracing a Message

**Example: Node 0 sends candidacy message**

```
1. node0.run()
   └─→ broadcast('candidacy', 0)
       └─→ buffer[0].append(('candidacy', 0))
       └─→ buffer[1].append(('candidacy', 0))
       └─→ buffer[2].append(('candidacy', 0))

2. node1.run()
   └─→ while buffer[1]: ✓
       └─→ deliver('candidacy', 0)
           └─→ broadcast('vote', (1, 0))
               └─→ buffer[0].append(('vote', (1, 0)))
               └─→ buffer[1].append(('vote', (1, 0)))
               └─→ buffer[2].append(('vote', (1, 0)))

3. node0.run()
   └─→ while buffer[0]: ✓
       └─→ deliver('vote', (1, 0))
           └─→ votes[0] = 1
```

That's how messages flow through the system!

