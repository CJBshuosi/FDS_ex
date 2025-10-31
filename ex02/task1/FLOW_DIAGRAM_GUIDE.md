# Code Execution Flow Diagrams - Guide

## 📊 You Have 3 Flow Diagrams

### 1. **Detailed Flow Diagram** (Complex)
- Shows every decision point
- Shows all function calls
- Shows message handling
- **Best for:** Understanding every detail

### 2. **Simplified Flow Diagram** (Medium)
- Shows main phases
- Groups related functions
- Shows state transitions
- **Best for:** Understanding the big picture

### 3. **Function Call Timeline** (Simple)
- Shows step-by-step execution
- Shows exact timing
- Shows message flow
- **Best for:** Understanding the sequence

---

## 🎯 How to Read the Diagrams

### Boxes
- **Rectangular boxes** = Function calls or actions
- **Diamond boxes** = Decision points (if/else)
- **Rounded boxes** = Start/End points

### Arrows
- **Solid arrows** = Normal flow
- **Labeled arrows** = Condition (yes/no)
- **Curved arrows** = Loop back

### Colors
- **Red** = Start/Entry point
- **Blue** = Main loop
- **Green** = State transitions
- **Yellow** = Leader actions
- **Purple** = Message handling

---

## 📖 Reading Guide

### For the Detailed Diagram:

**Start at the top:**
1. Program starts with `main()`
2. Clear screen with `os.system('clear')`
3. Initialize nodes with `initialize(3)`
4. Create each node with `Node.__init__()`
5. Start each node with `node.start()`
6. Enter main loop with `node.run()`

**In the main loop:**
1. Process messages from buffer
2. Check for follower timeout
3. Handle candidate state
4. Handle leader state
5. Sleep 0.1 seconds
6. Loop back to step 1

**Message processing:**
1. Check message type
2. Handle heartbeat, candidacy, or vote
3. Call appropriate functions
4. Return to main loop

---

## 🔄 The Main Loop Cycle

Every 0.1 seconds, each node does this:

```
1. Process all messages in buffer
   └─→ Call deliver() for each message

2. Check if follower timed out
   └─→ If yes, become candidate

3. If candidate:
   └─→ If election started: wait for votes
   └─→ If election not started: start election

4. If leader:
   └─→ Send heartbeat every 0.5 seconds

5. Sleep 0.1 seconds

6. Go back to step 1
```

---

## 💬 Message Flow

### Heartbeat Message Flow:
```
Leader sends heartbeat
  ↓
broadcast('heartbeat', leader_id)
  ↓
Add to all nodes' buffers
  ↓
Each node's run() processes it
  ↓
deliver('heartbeat', leader_id)
  ↓
Update last_heartbeat
  ↓
Become follower
```

### Candidacy Message Flow:
```
Candidate starts election
  ↓
broadcast('candidacy', candidate_id)
  ↓
Add to all nodes' buffers
  ↓
Each node's run() processes it
  ↓
deliver('candidacy', candidate_id)
  ↓
If not voted: broadcast('vote', ...)
  ↓
Vote message added to buffers
```

### Vote Message Flow:
```
Voter sends vote
  ↓
broadcast('vote', (voter_id, candidate_id))
  ↓
Add to all nodes' buffers
  ↓
Each node's run() processes it
  ↓
deliver('vote', (voter_id, candidate_id))
  ↓
Count vote
  ↓
If majority: set leader
```

---

## 🎯 Key Function Calls

### Initialization Phase:
```
main()
  → initialize(N)
    → Node(i).__init__()
    → node.start()
      → threading.Thread(target=run)
        → node.run()
```

### Main Loop Phase:
```
node.run()
  → deliver(msg_type, value)
    → broadcast(msg_type, value)
    → count_active_nodes()
  → broadcast(msg_type, value)
  → count_active_nodes()
```

### Message Processing Phase:
```
deliver(msg_type, value)
  → if heartbeat: update state
  → if candidacy: broadcast vote
  → if vote: count votes
```

---

## ⏱️ Timing of Key Events

| Time | Event | Function |
|------|-------|----------|
| 0s | Program starts | main() |
| 0s | Nodes created | initialize() |
| 0s | Threads started | node.start() |
| 0s | Main loop begins | node.run() |
| 1s | Follower timeout | run() |
| 1s | Become candidate | run() |
| 1s | Request votes | broadcast('candidacy') |
| 1.1s | Receive candidacy | deliver('candidacy') |
| 1.1s | Send vote | broadcast('vote') |
| 1.2s | Receive vote | deliver('vote') |
| 1.3s | Majority reached | deliver('vote') |
| 1.3s | Become leader | run() |
| 1.3s | Send heartbeat | broadcast('heartbeat') |
| 1.4s | Receive heartbeat | deliver('heartbeat') |
| 1.4s | Become follower | deliver('heartbeat') |
| 1.9s | Send heartbeat | broadcast('heartbeat') |
| 2.4s | Send heartbeat | broadcast('heartbeat') |

---

## 🔍 Tracing a Single Node

### Node 0 Timeline:

```
T=0s:
  run() starts
  state = 'follower'
  last_heartbeat = 0s

T=1s:
  run() checks: time.time() - last_heartbeat > 1 ✓
  state = 'candidate'
  election = False

T=1.5s:
  run() checks: state == 'candidate' and not election ✓
  sleep(random 1-3 seconds)

T=2s:
  run() checks: state == 'candidate' and not election ✓
  election = True
  broadcast('candidacy', 0)

T=2.1s:
  run() checks: state == 'candidate' and election ✓
  sleep(2 seconds)

T=2.3s:
  run() processes buffer
  deliver('vote', (1, 0))
  deliver('vote', (2, 0))
  votes[0] = 2
  count_active_nodes() = 3
  Check: 2 > 3//2 (2 > 1) ✓
  state = 'leader'
  broadcast('heartbeat', 0)

T=2.4s:
  run() checks: state == 'leader' and 0.5s passed ✓
  broadcast('heartbeat', 0)

T=2.9s:
  run() checks: state == 'leader' and 0.5s passed ✓
  broadcast('heartbeat', 0)

... (continues sending heartbeats every 0.5s)
```

---

## 📊 State Transition Diagram

```
START
  ↓
FOLLOWER (default state)
  ↓
  ├─ Receive heartbeat → FOLLOWER (stay)
  ├─ Timeout 1s → CANDIDATE
  │   ↓
  │   CANDIDATE
  │   ├─ Receive heartbeat → FOLLOWER
  │   ├─ Receive other candidacy → FOLLOWER
  │   ├─ Get majority votes → LEADER
  │   │   ↓
  │   │   LEADER
  │   │   ├─ Send heartbeat every 0.5s
  │   │   ├─ Crash → CRASHED
  │   │   └─ (continues until crash)
  │   │
  │   └─ Lose election → FOLLOWER (+ 5s cooldown)
  │
  └─ Crash → CRASHED
      ↓
      CRASHED
      └─ Recover → FOLLOWER
```

---

## 💡 Understanding Each Phase

### Phase 1: Initialization (0s)
- Create nodes
- Initialize properties
- Start threads
- Enter main loop

### Phase 2: Waiting (0-1s)
- All nodes are followers
- Waiting for heartbeat
- No messages yet

### Phase 3: Timeout (1s)
- First node times out
- Becomes candidate
- Waits random time

### Phase 4: Election (1-2s)
- Candidate asks for votes
- Other nodes vote
- Candidate counts votes

### Phase 5: Leader Election (2-2.3s)
- Candidate gets majority
- Becomes leader
- Sends heartbeat

### Phase 6: Stable State (2.3s+)
- Leader sends heartbeat every 0.5s
- Followers receive heartbeat
- System is stable

---

## 🎯 Quick Reference

**Main Functions:**
1. `main()` - Entry point
2. `initialize()` - Create nodes
3. `run()` - Main loop
4. `deliver()` - Process messages
5. `broadcast()` - Send messages
6. `count_active_nodes()` - Count active nodes

**Key Timings:**
- 0.1s - Main loop cycle
- 0.5s - Leader heartbeat interval
- 1s - Follower timeout
- 2s - Vote collection time
- 5s - Election cooldown

**Message Types:**
- HEARTBEAT - "I'm alive"
- CANDIDACY - "Vote for me"
- VOTE - "I support you"

---

## 📝 How to Present This

When explaining the code flow:

1. **Start with initialization**
   - Show how nodes are created
   - Show how threads are started

2. **Explain the main loop**
   - Show the 5 steps
   - Show the 0.1s cycle

3. **Explain message processing**
   - Show how messages are delivered
   - Show how broadcast works

4. **Show the timeline**
   - Walk through a complete election
   - Show exact timing

5. **Show state transitions**
   - Show how states change
   - Show the conditions

---

## 🚀 Using These Diagrams in Your Presentation

**For your 7-8 minute presentation:**

1. **Show the simplified diagram** (1 minute)
   - Explain the 5 phases
   - Show the main functions

2. **Walk through the timeline** (2 minutes)
   - Show step-by-step execution
   - Show message flow

3. **Explain state transitions** (1 minute)
   - Show how states change
   - Show the conditions

4. **Show function calls** (1 minute)
   - Show which functions call which
   - Show the relationships

This gives your audience a complete understanding of how the code works!

