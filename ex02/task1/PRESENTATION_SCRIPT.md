# Raft Consensus Algorithm - Presentation Script

## INTRODUCTION (30 seconds)

"Hello everyone. Today I'm going to explain a distributed system called **Raft Consensus Algorithm**.

Imagine you have multiple computers that need to work together and agree on a leader. This code shows how they do it.

The main idea is: **one leader, many followers**. The leader makes decisions, and followers follow the leader's instructions."

---

## PART 1: WHAT IS THIS CODE? (1 minute)

"This code implements a **leader election system**. 

Think of it like a classroom election:
- First, everyone is a **follower** - waiting for a leader
- If the leader disappears, students become **candidates** - they run for election
- They ask for votes from other students
- Whoever gets the most votes becomes the new leader
- The leader sends regular messages saying 'I'm still here' - we call this a **heartbeat**

This is exactly what this code does, but with computer nodes instead of students."

---

## PART 2: THE THREE STATES (1 minute)

"Every node has three possible states:

**First: FOLLOWER**
- This is the default state
- The node waits for the leader's heartbeat
- If it receives a heartbeat, it knows the leader is alive
- If it doesn't receive a heartbeat for 1 second, it becomes a candidate

**Second: CANDIDATE**
- The node wants to become a leader
- It sends a message to all other nodes asking for votes
- It waits 2 seconds to collect votes
- If it gets more than half the votes, it becomes a leader
- If it loses, it goes back to being a follower and waits 5 seconds before trying again

**Third: LEADER**
- The node won the election
- Every 0.5 seconds, it sends a heartbeat to all other nodes
- This tells everyone: 'I'm still alive, keep following me'
- If the leader crashes, the followers will timeout and start a new election"

---

## PART 3: THE THREE MESSAGE TYPES (1 minute)

"There are three types of messages in this system:

**Message 1: HEARTBEAT**
- Sent by the leader every 0.5 seconds
- Message: 'I'm alive, I'm your leader'
- When a follower receives this, it updates the time and stays as a follower
- If a candidate receives this, it becomes a follower

**Message 2: CANDIDACY**
- Sent by a candidate when starting an election
- Message: 'Vote for me to be the leader'
- When a node receives this, it votes for the candidate (if it hasn't voted yet)

**Message 3: VOTE**
- Sent by a node to support a candidate
- Message: 'I vote for you'
- When the candidate receives votes, it counts them
- If the candidate gets more than half the votes, it becomes the leader"

---

## PART 4: HOW THE SYSTEM WORKS (2 minutes)

"Let me walk you through a complete example with 3 nodes:

**Step 1: Initialization**
- All 3 nodes start as followers
- They wait for a leader

**Step 2: Timeout**
- After 1 second with no heartbeat, node 0 becomes a candidate
- It sends a candidacy message to nodes 1 and 2

**Step 3: Voting**
- Node 1 receives the candidacy message and votes for node 0
- Node 2 receives the candidacy message and votes for node 0
- Node 0 counts the votes: it has 2 votes

**Step 4: Leader Election**
- Node 0 needs more than half of 3 votes, which is 2 votes
- Node 0 has exactly 2 votes, so it becomes the leader
- It sends a heartbeat to all nodes

**Step 5: Normal Operation**
- Nodes 1 and 2 receive the heartbeat and become followers
- Every 0.5 seconds, node 0 sends a heartbeat
- Nodes 1 and 2 keep receiving heartbeats and stay as followers

**Step 6: Node Crash**
- If node 0 crashes, nodes 1 and 2 don't receive heartbeats
- After 1 second, they timeout and become candidates
- They start a new election

**Step 7: Recovery**
- If node 0 recovers, it becomes a follower again
- It receives heartbeats from the new leader"

---

## PART 5: KEY CONCEPTS (1 minute)

"Let me highlight the important concepts:

**Majority Voting:**
- To become a leader, you need more than half the votes
- With 3 nodes, you need 2 votes
- With 5 nodes, you need 3 votes
- This ensures only one leader is elected

**Heartbeat Timeout:**
- If a follower doesn't receive a heartbeat for 1 second, it becomes a candidate
- This timeout is important - it detects when the leader has crashed

**Election Cooldown:**
- After losing an election, a node waits 5 seconds before trying again
- This prevents the system from having too many elections
- It gives the new leader time to stabilize

**Message Queue:**
- Each node has a message buffer
- Messages are processed one by one
- This prevents messages from being lost"

---

## PART 6: WHY IS THIS IMPORTANT? (30 seconds)

"This algorithm is used in real-world systems like:
- Kubernetes (container orchestration)
- etcd (distributed database)
- Consul (service mesh)

It solves a fundamental problem: **How do distributed systems agree on a leader?**

The answer is: **voting and heartbeats**."

---

## CONCLUSION (30 seconds)

"To summarize:
- Nodes start as followers
- If the leader disappears, they become candidates
- They vote for a new leader
- The winner sends heartbeats to prove it's alive
- If it crashes, the process repeats

This is the Raft Consensus Algorithm. Thank you!"

---

## TIMING GUIDE

- Introduction: 30 seconds
- Part 1: 1 minute
- Part 2: 1 minute
- Part 3: 1 minute
- Part 4: 2 minutes
- Part 5: 1 minute
- Part 6: 30 seconds
- Conclusion: 30 seconds

**Total: ~7-8 minutes**

---

## PRONUNCIATION TIPS

- **Raft**: /ræft/ (like "craft" without the "c")
- **Consensus**: /kənˈsɛnsəs/ (con-SEN-sus)
- **Algorithm**: /ˈælɡərɪðəm/ (AL-go-rith-um)
- **Candidate**: /ˈkændɪdeɪt/ (CAN-di-date)
- **Heartbeat**: /ˈhɑːrtbiːt/ (HART-beat)
- **Majority**: /məˈdʒɒrɪti/ (ma-JOR-i-ty)
- **Timeout**: /ˈtaɪmaʊt/ (TIME-out)
- **Cooldown**: /ˈkuːldaʊn/ (COOL-down)

---

## PRACTICE TIPS

1. Read the script out loud 3-5 times
2. Practice the timing - aim for 7-8 minutes total
3. Memorize the key phrases in each section
4. Practice the example scenario (Step 1-7) multiple times
5. Be ready to answer questions about the three states and message types

