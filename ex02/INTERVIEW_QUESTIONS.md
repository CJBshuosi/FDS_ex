# 🎤 Interview Questions - Task 1 & Task 2

## 📋 Interview Format
- **Duration:** ~30-45 minutes per person
- **Focus:** Theoretical understanding + Implementation details
- **Questions:** Mix of conceptual and code-specific questions
- **Difficulty:** Progressive (easy → hard)

---

## 🎯 TASK 1: Raft Consensus Algorithm

### Level 1: Basic Understanding (Easy)

**Q1.1: What is the main purpose of the Raft Consensus Algorithm?**
- Expected answer: To elect a leader in a distributed system where multiple nodes need to agree on a single leader
- Follow-up: Why do we need a leader?

**Q1.2: What are the three states a node can be in?**
- Expected answer: Follower, Candidate, Leader
- Follow-up: Can a node be in multiple states at the same time?

**Q1.3: What are the three types of messages in your implementation?**
- Expected answer: Heartbeat, Candidacy, Vote
- Follow-up: What does each message do?

**Q1.4: What is the purpose of the heartbeat message?**
- Expected answer: To prove the leader is alive and to prevent new elections
- Follow-up: How often does the leader send heartbeats?

**Q1.5: What happens when a follower doesn't receive a heartbeat for 1 second?**
- Expected answer: It becomes a candidate and starts an election
- Follow-up: Why 1 second? What if it was 0.5 seconds or 5 seconds?

---

### Level 2: Implementation Details (Medium)

**Q2.1: Explain the election process step by step.**
- Expected answer: 
  1. Follower times out → becomes candidate
  2. Candidate broadcasts candidacy message
  3. Other nodes vote if they haven't voted yet
  4. Candidate counts votes
  5. If majority, becomes leader
- Follow-up: What if two candidates start elections at the same time?

**Q2.2: What is the purpose of the `voted` flag?**
- Expected answer: To prevent a node from voting twice in the same election
- Follow-up: When should this flag be reset?

**Q2.3: What is the purpose of the `resigned` variable?**
- Expected answer: To prevent a node from immediately becoming a candidate again (5-second cooldown)
- Follow-up: Why is this cooldown necessary?

**Q2.4: How does the code determine if a candidate has won the election?**
- Expected answer: By checking if `votes[candidate_id] > count_active_nodes() // 2`
- Follow-up: What does `// 2` mean? Why not just `/ 2`?

**Q2.5: What is the purpose of the `buffer` dictionary?**
- Expected answer: To store messages for each node asynchronously
- Follow-up: Why not send messages directly instead of using a buffer?

**Q2.6: Explain the `deliver()` method. What does it do for each message type?**
- Expected answer:
  - Heartbeat: Update last_heartbeat, become follower if candidate
  - Candidacy: Vote if haven't voted yet
  - Vote: Count vote, check if majority reached
- Follow-up: Why does heartbeat make a candidate become a follower?

---

### Level 3: Advanced & Edge Cases (Hard)

**Q3.1: What happens if the leader crashes?**
- Expected answer: 
  1. Followers don't receive heartbeat
  2. After 1 second, they timeout
  3. They become candidates and start new election
  4. One of them becomes new leader
- Follow-up: How long does it take to elect a new leader?

**Q3.2: What is a race condition in your code? Can you identify one?**
- Expected answer: The `buffer` dictionary is accessed without locks in a multithreaded environment
- Follow-up: What could go wrong? How would you fix it?

**Q3.3: Why is `self.resigned = 0` a bug?**
- Expected answer: Because `time.time() - 0` is a huge number, so the condition `time.time() - self.resigned > 5` is always true at startup
- Follow-up: What should it be initialized to?

**Q3.4: Why is the `voted` flag never reset in the current code?**
- Expected answer: It's set to True in line 97 but never reset to False, so a node can only vote once in its lifetime
- Follow-up: When should it be reset?

**Q3.5: What happens if a node receives a heartbeat from a different leader than the one it knows?**
- Expected answer: It updates `self.leader` to the new leader
- Follow-up: Is this correct behavior? Why or why not?

**Q3.6: Explain the difference between these two ways of determining the leader:**
```python
# Way 1: Each node counts votes
if self.votes[candidate_id] > self.count_active_nodes() // 2 and self.leader == None:
    self.leader = candidate_id

# Way 2: Only candidate counts votes
if self.votes[candidate_id] > self.count_active_nodes() // 2 and self.leader == None and self.state == 'candidate':
    self.leader = candidate_id
```
- Expected answer: Way 1 allows any node to detect the leader; Way 2 only allows the candidate to announce itself
- Follow-up: Which is better? Why?

**Q3.7: What is the purpose of `time.sleep(random.uniform(1, 3))` in the candidate state?**
- Expected answer: To prevent multiple candidates from starting elections at exactly the same time
- Follow-up: What if all candidates started elections at the same time?

**Q3.8: Why does the code check `if self.state == 'candidate'` after the sleep?**
- Expected answer: Because the node might have received a heartbeat or candidacy message during the sleep and changed state
- Follow-up: What if it didn't check?

**Q3.9: What is the threading model used in your code?**
- Expected answer: Each node runs in a daemon thread
- Follow-up: What does daemon=True mean? What happens when the main thread exits?

**Q3.10: How would you handle the case where a node crashes and recovers multiple times?**
- Expected answer: The recover() method resets the node to follower state and clears the buffer
- Follow-up: Is there any state that should be preserved?

---

### Level 4: Design & Optimization (Very Hard)

**Q4.1: What are the limitations of your current implementation?**
- Possible answers:
  - No persistence (state lost on crash)
  - No log replication
  - No Byzantine fault tolerance
  - Race conditions in buffer access
  - No timeout for vote collection

**Q4.2: How would you improve the election process to be faster?**
- Possible answers:
  - Reduce timeout from 1s to 0.5s
  - Reduce vote collection time from 2s to 1s
  - Use exponential backoff for retries

**Q4.3: What happens if the network is partitioned (split brain)?**
- Expected answer: Both partitions might elect different leaders
- Follow-up: How would you prevent this?

**Q4.4: How would you add log replication to this system?**
- Expected answer: Leader sends log entries to followers, followers acknowledge
- Follow-up: What if a follower crashes before acknowledging?

**Q4.5: What is the time complexity of the election process?**
- Expected answer: O(n) where n is the number of nodes (broadcast to all nodes)
- Follow-up: Can you optimize it?

---

## 🎯 TASK 2: Causal Length Set (CLS)

### Level 1: Basic Understanding (Easy)

**Q2.1: What is a Causal Length Set (CLS)?**
- Expected answer: A data structure that represents a set where items can be added and removed, and the state can be synchronized across multiple replicas
- Follow-up: Why is it called "causal"?

**Q2.2: How does CLS represent whether an item is in the set or not?**
- Expected answer: Using a counter - odd counter means in the set, even counter means not in the set
- Follow-up: Why use a counter instead of a boolean?

**Q2.3: What are the four main operations in CLS?**
- Expected answer: add(), remove(), contains(), mutual_sync()
- Follow-up: What does each operation do?

**Q2.4: What happens when you add an item that's already in the set?**
- Expected answer: Nothing (the code checks if counter is even before incrementing)
- Follow-up: What if you add it multiple times?

**Q2.5: What happens when you remove an item that's not in the set?**
- Expected answer: Nothing (the code checks if item exists and counter is odd)
- Follow-up: What if you remove it multiple times?

---

### Level 2: Implementation Details (Medium)

**Q2.6: Explain the add() method. Why does it check `self.cart[item] % 2 == 0`?**
- Expected answer: To check if the counter is even (item not in set), so it can be incremented to make it odd (item in set)
- Follow-up: What if the counter is odd?

**Q2.7: Explain the remove() method. Why does it check `self.cart[item] % 2 == 1`?**
- Expected answer: To check if the counter is odd (item in set), so it can be incremented to make it even (item not in set)
- Follow-up: What if the counter is even?

**Q2.8: What is the purpose of the mutual_sync() method?**
- Expected answer: To synchronize the state of multiple CLS instances by taking the maximum counter for each item
- Follow-up: Why use maximum instead of other operations?

**Q2.9: Trace through the example in the code. What is the final state of Bob's list?**
- Expected answer: 
  - After first sync: Bob has {Milk:1, Potato:1, Eggs:1, Sausage:1, Mustard:1, Coke:1}
  - After Alice's operations and second sync: Bob has {Milk:1, Tofu:1, Eggs:1, Sausage:1, Mustard:1, Coke:1, Potato:2}
  - So Bob's list contains: Milk, Tofu, Eggs, Sausage, Mustard, Coke (NOT Potato)
- Follow-up: Why doesn't Bob's list contain Potato?

**Q2.10: What is the difference between `self.cart.copy()` and `self.cart`?**
- Expected answer: copy() creates a shallow copy, so changes to the copy don't affect the original
- Follow-up: Is shallow copy sufficient here? Why or why not?

---

### Level 3: Advanced & Edge Cases (Hard)

**Q3.1: What is the "causal" property in CLS?**
- Expected answer: The operations respect causality - if A happens before B, then the result reflects this ordering
- Follow-up: How does the counter ensure causality?

**Q3.2: What happens if you sync with multiple CLS instances at the same time?**
- Expected answer: The method takes the maximum counter for each item across all instances
- Follow-up: Is the order of syncing important?

**Q3.3: Can you have a situation where two replicas have different states after syncing?**
- Expected answer: No, after mutual_sync(), all replicas have the same state
- Follow-up: What if a new operation happens after sync?

**Q3.4: What is the time complexity of the mutual_sync() method?**
- Expected answer: O(n*m) where n is the number of other CLS instances and m is the number of items
- Follow-up: Can you optimize it?

**Q3.5: What happens if you add and remove the same item multiple times?**
- Expected answer: The counter keeps incrementing, so you can track the history of operations
- Follow-up: What if the counter overflows?

**Q3.6: Is CLS suitable for a distributed system with network partitions?**
- Expected answer: Yes, because it can handle concurrent operations and eventual consistency
- Follow-up: What if two replicas are partitioned and both add the same item?

**Q3.7: What is the difference between CLS and a traditional set?**
- Expected answer: CLS can handle concurrent add/remove operations without conflicts, while traditional sets cannot
- Follow-up: What is the trade-off?

**Q3.8: Can you implement CLS with a different data structure (not a dictionary)?**
- Expected answer: Yes, you could use a list or other data structures
- Follow-up: What would be the advantages/disadvantages?

---

### Level 4: Design & Optimization (Very Hard)

**Q4.1: What are the limitations of CLS?**
- Possible answers:
  - Counters can overflow
  - No garbage collection (counters keep growing)
  - No ordering of operations
  - No support for other operations (union, intersection, etc.)

**Q4.2: How would you implement garbage collection for CLS?**
- Expected answer: Periodically reset counters when they reach a certain threshold
- Follow-up: How would you ensure consistency?

**Q4.3: How would you extend CLS to support ordered operations?**
- Expected answer: Add timestamps or vector clocks to track operation order
- Follow-up: What would be the overhead?

**Q4.4: How would you implement CLS in a distributed system?**
- Expected answer: Each node maintains its own CLS and syncs with others periodically
- Follow-up: What if nodes are offline?

**Q4.5: What is the relationship between CLS and CRDT (Conflict-free Replicated Data Type)?**
- Expected answer: CLS is a type of CRDT that handles concurrent operations without conflicts
- Follow-up: What other CRDTs do you know?

---

## 🎯 Cross-Task Questions

**Q1: How are Task 1 and Task 2 related?**
- Expected answer: Both deal with distributed systems and consistency
- Follow-up: Could you use CLS in the Raft system?

**Q2: What is the difference between strong consistency (Raft) and eventual consistency (CLS)?**
- Expected answer: Raft ensures all nodes have the same state at all times; CLS allows temporary inconsistency but guarantees eventual consistency
- Follow-up: When would you use each?

**Q3: What are the main challenges in distributed systems?**
- Expected answer: Consistency, availability, partition tolerance (CAP theorem)
- Follow-up: How do Raft and CLS address these?

**Q4: How would you combine Raft and CLS?**
- Expected answer: Use Raft to elect a leader, then use CLS for data replication
- Follow-up: What would be the advantages?

---

## 💡 Tips for Answering

### Do's:
- ✅ Explain your reasoning clearly
- ✅ Use examples from the code
- ✅ Admit if you don't know something
- ✅ Ask clarifying questions
- ✅ Show your understanding of the concepts
- ✅ Discuss trade-offs and alternatives

### Don'ts:
- ❌ Memorize answers word-for-word
- ❌ Make up answers
- ❌ Blame your teammates
- ❌ Get defensive
- ❌ Rush through answers
- ❌ Ignore follow-up questions

---

## 📊 Expected Answer Quality

### Poor Answer (0-2 points):
- Incorrect or incomplete
- Shows no understanding
- Cannot explain reasoning

### Average Answer (3-5 points):
- Mostly correct
- Shows basic understanding
- Can explain some reasoning

### Good Answer (6-8 points):
- Correct and complete
- Shows solid understanding
- Can explain reasoning clearly

### Excellent Answer (9-10 points):
- Correct, complete, and insightful
- Shows deep understanding
- Can discuss trade-offs and alternatives
- Can connect to other concepts

---

## 🎯 Preparation Strategy

1. **Understand the concepts** (not just the code)
2. **Know the code** (line by line)
3. **Practice explaining** (out loud)
4. **Prepare examples** (from the code)
5. **Think about edge cases** (what could go wrong?)
6. **Know the limitations** (what's missing?)
7. **Be ready for follow-ups** (think deeper)
8. **Stay calm** (it's just a conversation)

---

## ⏱️ Time Management

- **Easy questions:** 1-2 minutes each
- **Medium questions:** 2-3 minutes each
- **Hard questions:** 3-5 minutes each
- **Very hard questions:** 5-10 minutes each

**Total:** ~30-45 minutes for 10-15 questions

---

## 🚀 Good Luck!

Remember: The interviewer wants to understand your knowledge, not trick you. Be honest, think carefully, and explain your reasoning clearly.

**You've got this!** 💪

