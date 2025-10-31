# Code Comments Summary - All Files Annotated

## ✅ Completed: All 5 files have been annotated with English comments

### Files Annotated:

1. **ex01/task1/main.py** ✅
   - Vector Clock computation algorithm
   - Kahn's topological sorting algorithm
   - Causal graph construction
   - Edge reduction algorithm
   - Comments on every major function and key logic

2. **ex01/task2/client/client.py** ✅
   - gRPC client implementation
   - User registration workflow
   - Data storage and retrieval
   - One-time passcode generation
   - Hash computation request
   - Comments explaining each RPC call and workflow step

3. **ex01/task2/hashServer/server.py** ✅
   - gRPC hash server implementation
   - Data retrieval from data server
   - SHA256 hash computation
   - Server initialization and startup
   - Comments on each step of the hash computation process

4. **ex02/task1/main.py** ✅
   - Raft Consensus Algorithm implementation
   - Node state machine (Follower → Candidate → Leader)
   - Message handling (Heartbeat, Candidacy, Vote)
   - Election process with majority voting
   - Node crash and recovery simulation
   - Comments on all state transitions and message handling

5. **ex02/task2/main.py** ✅
   - Causal Length Set (CLS) CRDT implementation
   - Counter-based set membership
   - Add/Remove/Contains operations
   - Mutual synchronization with eventual consistency
   - Test case with detailed step-by-step comments
   - Comments explaining counter semantics and operations

---

## 📝 Comment Style Used

All comments are placed **on the right side of code lines** in English:

```python
# Example format:
variable = value  # Comment explaining what this line does
function_call()  # Comment explaining the purpose
```

---

## 🎯 Key Topics Covered in Comments

### ex01/task1 - Vector Clocks & Causal Graphs
- Vector clock computation algorithm
- Topological sorting using Kahn's algorithm
- Causal precedence rules
- Transitive edge reduction
- Example scenarios with actual values

### ex01/task2 - gRPC Microservices
- gRPC channel creation and stub initialization
- RPC method calls and message passing
- Multi-service communication workflow
- Error handling and response processing
- Server initialization with thread pool

### ex02/task1 - Raft Consensus
- Node state transitions (Follower → Candidate → Leader)
- Heartbeat mechanism and timeout detection
- Election process with random delays
- Vote counting and majority determination
- Message buffer and asynchronous communication
- Node crash and recovery handling

### ex02/task2 - CRDT (Causal Length Set)
- Counter-based membership representation
- Add/Remove/Contains operations
- Eventual consistency through synchronization
- Maximum counter merging strategy
- Concurrent operation handling
- Test case walkthrough with state changes

---

## 💡 Presentation Tips

When presenting these projects tomorrow:

### For ex01/task1:
1. Explain vector clocks: "Each process has a vector, increment own component on local event"
2. Show example: "A1=[1,0,0], B1=[0,1,0], A2=[1,1,0] (takes max of parents)"
3. Explain Kahn's algorithm: "Process nodes with in-degree 0, remove edges, repeat"
4. Show edge reduction: "Remove transitive edges to simplify graph"

### For ex01/task2:
1. Explain gRPC: "Remote Procedure Call framework for microservices"
2. Show workflow: "Client → Data Server (register, store, get passcode) → Hash Server"
3. Explain each step: "Register user, store data, generate passcode, compute hash"
4. Show communication: "Client calls data server, hash server calls data server"

### For ex02/task1:
1. Explain Raft: "Distributed consensus algorithm for leader election"
2. Show states: "Follower (default) → Candidate (election) → Leader (elected)"
3. Explain messages: "Heartbeat (alive), Candidacy (vote request), Vote (support)"
4. Show election: "Timeout → Candidacy → Voting → Leader → Heartbeat"
5. Explain majority: "Need > 50% votes to become leader"

### For ex02/task2:
1. Explain CLS: "CRDT for distributed shopping lists without conflicts"
2. Show counter logic: "Odd=in set, Even=not in set"
3. Explain operations: "Add/Remove increment counter, Contains checks parity"
4. Show sync: "Take maximum counter for each item across replicas"
5. Trace example: "Alice adds items, Bob adds items, they sync, Alice removes, they sync again"

---

## 🚀 Ready for Presentation!

All files are now fully commented and ready for your presentation tomorrow. The comments:
- ✅ Are in English
- ✅ Are placed on the right side of code lines
- ✅ Explain key logic and operations
- ✅ Include example scenarios
- ✅ Cover all major functions and algorithms
- ✅ Help explain the workflow and data flow

You can now confidently explain each project step by step!

---

## 📋 Quick Reference

| File | Topic | Key Concepts |
|------|-------|--------------|
| ex01/task1/main.py | Vector Clocks | Topological sort, Causal precedence, Edge reduction |
| ex01/task2/client/client.py | gRPC Client | RPC calls, Message passing, Workflow |
| ex01/task2/hashServer/server.py | gRPC Server | Server implementation, Hash computation |
| ex02/task1/main.py | Raft Consensus | Leader election, State machine, Voting |
| ex02/task2/main.py | CRDT (CLS) | Counter semantics, Synchronization, Eventual consistency |

Good luck with your presentation! 🎉

