# 🎯 Interview Cheat Sheet - Quick Reference

## 📋 TASK 1: Raft Consensus Algorithm

### The 3 States
```
FOLLOWER (default)
  ↓ (timeout 1s)
CANDIDATE (election)
  ↓ (majority votes)
LEADER (elected)
  ↓ (crash)
FOLLOWER (restart)
```

### The 3 Messages
| Message | Sent By | Purpose |
|---------|---------|---------|
| **Heartbeat** | Leader | Prove alive, prevent elections |
| **Candidacy** | Candidate | Request votes |
| **Vote** | Follower | Support candidate |

### Key Numbers
- **1 second** = Follower timeout
- **0.5 seconds** = Leader heartbeat interval
- **2 seconds** = Vote collection time
- **5 seconds** = Election cooldown
- **> 50%** = Majority needed

### Election Process (5 Steps)
```
1. Follower times out (no heartbeat for 1s)
2. Becomes candidate, broadcasts candidacy
3. Other nodes vote if haven't voted yet
4. Candidate counts votes
5. If majority (> 50%), becomes leader
```

### Key Functions
| Function | Purpose | Line |
|----------|---------|------|
| `run()` | Main loop | 32 |
| `deliver()` | Process messages | 86 |
| `broadcast()` | Send to all nodes | 69 |
| `count_active_nodes()` | Count working nodes | 29 |
| `crash()` | Simulate failure | 74 |
| `recover()` | Restart node | 80 |

### The 5 Bugs
1. **Race condition** - Buffer accessed without locks (lines 34-36, 72)
2. **Resigned bug** - Initialized to 0 instead of time.time() (line 17)
3. **Voted bug** - Never reset to False (line 97)
4. **Last heartbeat** - Initialized to current time (line 16)
5. **Missing locks** - Global variables not protected (lines 6-7)

### Message Flow
```
Heartbeat:
  Leader → broadcast → buffer → deliver → follower

Candidacy:
  Candidate → broadcast → buffer → deliver → vote

Vote:
  Voter → broadcast → buffer → deliver → count
```

### State Transitions
```
Follower:
  - Receive heartbeat → stay follower
  - Timeout 1s → become candidate
  - Receive candidacy → vote

Candidate:
  - Receive heartbeat → become follower
  - Get majority votes → become leader
  - Receive other candidacy → become follower

Leader:
  - Send heartbeat every 0.5s
  - Crash → become crashed
```

### Important Code Snippets

**Check for majority:**
```python
if self.votes[self.id] > self.count_active_nodes() // 2:
    self.state = 'leader'
```

**Heartbeat handling:**
```python
if msg_type == 'heartbeat':
    self.last_heartbeat = time.time()
    if self.state == 'candidate' or self.leader == None:
        self.state = 'follower'
        self.leader = value
```

**Voting:**
```python
if msg_type == 'candidacy':
    if not self.voted:
        self.broadcast('vote', (self.id, value))
        self.voted = True
```

---

## 📋 TASK 2: Causal Length Set (CLS)

### Counter-Based Membership
```
Odd counter  → Item IS in the set
Even counter → Item is NOT in the set

Example:
  Milk: 1 (odd) → in set
  Milk: 2 (even) → not in set
  Milk: 3 (odd) → in set again
```

### The 4 Operations
| Operation | Purpose | Logic |
|-----------|---------|-------|
| **add()** | Add item | If not exists: counter=1; If even: counter++ |
| **remove()** | Remove item | If odd: counter++ |
| **contains()** | Check membership | Return counter is odd |
| **mutual_sync()** | Sync replicas | Take max counter for each item |

### Key Concept: Maximum Counter
```
Alice: {Milk: 1, Potato: 3}
Bob:   {Milk: 2, Eggs: 1}

After sync:
Both:  {Milk: 2, Potato: 3, Eggs: 1}
       (take maximum for each item)
```

### The Example Trace
```
Step 1: Alice adds {Milk, Potato, Eggs}
Step 2: Bob adds {Sausage, Mustard, Coke, Potato}
Step 3: Bob syncs with Alice
        Both have: {Milk, Potato, Eggs, Sausage, Mustard, Coke}

Step 4: Alice removes Sausage, adds Tofu, removes Potato
        Alice: {Milk, Tofu, Eggs, Sausage, Mustard, Coke, Potato:2}

Step 5: Alice syncs with Bob
        Both have: {Milk, Tofu, Eggs, Sausage, Mustard, Coke, Potato:2}

Final: Bob's list contains Potato? NO (counter is 2, even)
```

### Key Functions
| Function | Purpose | Line |
|----------|---------|------|
| `add()` | Add item | 17 |
| `remove()` | Remove item | 27 |
| `contains()` | Check membership | 35 |
| `mutual_sync()` | Sync replicas | 41 |

### Important Code Snippets

**Add operation:**
```python
def add(self, item):
    if item not in self.cart:
        self.cart[item] = 1
    elif self.cart[item] % 2 == 0:
        self.cart[item] += 1
```

**Remove operation:**
```python
def remove(self, item):
    if item in self.cart and self.cart[item] % 2 == 1:
        self.cart[item] += 1
```

**Contains operation:**
```python
def contains(self, item):
    return item in self.cart and self.cart[item] % 2 == 1
```

**Mutual sync:**
```python
def mutual_sync(self, other_carts):
    mutual_cart = self.cart.copy()
    for other in other_carts:
        for item, counter in other.cart.items():
            if item in mutual_cart:
                mutual_cart[item] = max(mutual_cart[item], counter)
            else:
                mutual_cart[item] = counter
    self.cart = mutual_cart
    for other in other_carts:
        other.cart = mutual_cart
```

### Why CLS Works
- ✅ No central authority needed
- ✅ Handles concurrent operations
- ✅ Automatic conflict resolution
- ✅ Eventual consistency
- ✅ Scalable to many replicas

---

## 🎯 Common Interview Questions

### Task 1 - Easy
- Q: What are the 3 states?
  A: Follower, Candidate, Leader

- Q: What are the 3 messages?
  A: Heartbeat, Candidacy, Vote

- Q: What is the heartbeat timeout?
  A: 1 second

- Q: What is the majority?
  A: > 50% of active nodes

### Task 1 - Hard
- Q: What is the race condition?
  A: Buffer accessed without locks

- Q: Why is resigned = 0 a bug?
  A: time.time() - 0 is huge, condition always true

- Q: Why is voted never reset?
  A: Node can only vote once in lifetime

- Q: What happens if leader crashes?
  A: Followers timeout, new election, new leader elected

### Task 2 - Easy
- Q: How does CLS represent membership?
  A: Odd counter = in set, Even counter = not in set

- Q: What are the 4 operations?
  A: add, remove, contains, mutual_sync

- Q: What does mutual_sync do?
  A: Takes maximum counter for each item

### Task 2 - Hard
- Q: Trace the example, does Bob have Potato?
  A: No, counter is 2 (even)

- Q: Why use maximum in sync?
  A: Preserves all operations, ensures causality

- Q: Is CLS suitable for distributed systems?
  A: Yes, handles eventual consistency

---

## 📊 Quick Comparison

### Raft vs CLS
| Aspect | Raft | CLS |
|--------|------|-----|
| **Consistency** | Strong | Eventual |
| **Leader** | Yes | No |
| **Conflicts** | Prevented | Resolved |
| **Scalability** | Limited | High |
| **Complexity** | High | Low |

---

## 💡 Interview Tips

### Do's
- ✅ Explain clearly
- ✅ Use examples
- ✅ Admit if unsure
- ✅ Ask clarifying questions
- ✅ Show reasoning
- ✅ Discuss trade-offs

### Don'ts
- ❌ Memorize answers
- ❌ Make up answers
- ❌ Blame teammates
- ❌ Get defensive
- ❌ Rush answers
- ❌ Ignore follow-ups

---

## 🚀 Last-Minute Prep

**5 minutes before interview:**
1. Review the 3 states (Raft)
2. Review the 3 messages (Raft)
3. Review the 4 operations (CLS)
4. Review the key numbers (Raft)
5. Take a deep breath

**During interview:**
1. Listen carefully to the question
2. Think before answering
3. Explain your reasoning
4. Use examples from code
5. Ask for clarification if needed

**If you don't know:**
- "I'm not sure, but I think..."
- "Let me think about that..."
- "Can you rephrase the question?"
- "I don't know, but I can explain..."

---

## 📝 Key Formulas

**Majority calculation:**
```
majority = count_active_nodes() // 2
need_votes = majority + 1
```

**Timeout check:**
```
if time.time() - self.last_heartbeat > 1:
    # Timeout occurred
```

**Counter parity:**
```
if counter % 2 == 1:  # Odd
    # Item is in set
else:  # Even
    # Item is not in set
```

---

## 🎓 What Interviewer Wants to See

1. **Understanding** - Do you understand the concepts?
2. **Implementation** - Can you explain the code?
3. **Reasoning** - Can you explain why?
4. **Edge cases** - Do you think about problems?
5. **Improvements** - Can you suggest improvements?
6. **Communication** - Can you explain clearly?

---

## 🏆 Scoring Guide

**0-2 points:** Wrong or no understanding
**3-5 points:** Basic understanding
**6-8 points:** Good understanding
**9-10 points:** Excellent understanding

**Total:** ~10-15 questions × 10 points = 100-150 points

---

## 🎯 Final Checklist

- [ ] Know the 3 states (Raft)
- [ ] Know the 3 messages (Raft)
- [ ] Know the key numbers (Raft)
- [ ] Know the 5 bugs (Raft)
- [ ] Know the 4 operations (CLS)
- [ ] Know the counter logic (CLS)
- [ ] Can trace the example (CLS)
- [ ] Can explain election process (Raft)
- [ ] Can explain mutual_sync (CLS)
- [ ] Can discuss trade-offs
- [ ] Can admit when unsure
- [ ] Can explain clearly

**You're ready!** 💪

---

## 🚀 Good Luck!

Remember:
- The interviewer wants to understand your knowledge
- Be honest and clear
- Think before answering
- Explain your reasoning
- You've studied this material
- You can do this!

**Go get 'em!** 🎉

