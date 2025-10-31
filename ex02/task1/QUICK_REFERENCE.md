# Quick Reference Cards - For Memorization

## CARD 1: THE THREE STATES (Memorize this!)

```
┌─────────────────────────────────────────────────────────┐
│                    FOLLOWER                             │
│  • Default state                                        │
│  • Waits for heartbeat                                  │
│  • No heartbeat for 1s → becomes CANDIDATE              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    CANDIDATE                            │
│  • Asks for votes                                       │
│  • Waits 2 seconds to collect votes                     │
│  • Gets majority → becomes LEADER                       │
│  • Loses → back to FOLLOWER + 5s cooldown               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     LEADER                              │
│  • Sends heartbeat every 0.5 seconds                    │
│  • Proves it's alive                                    │
│  • Crashes → new election starts                        │
└─────────────────────────────────────────────────────────┘
```

---

## CARD 2: THE THREE MESSAGES (Memorize this!)

| Message | Sent By | Content | Effect |
|---------|---------|---------|--------|
| **HEARTBEAT** | Leader | "I'm alive" | Follower stays follower |
| **CANDIDACY** | Candidate | "Vote for me" | Node votes for candidate |
| **VOTE** | Voter | "I support you" | Candidate counts votes |

---

## CARD 3: KEY NUMBERS (Memorize this!)

```
Heartbeat Timeout:     1 second
  → If no heartbeat for 1s, become candidate

Leader Heartbeat:      0.5 seconds
  → Leader sends heartbeat every 0.5s

Vote Collection:       2 seconds
  → Candidate waits 2s to collect votes

Election Cooldown:     5 seconds
  → Wait 5s before trying election again

Majority:              > 50% of votes
  → With 3 nodes: need 2 votes
  → With 5 nodes: need 3 votes
```

---

## CARD 4: OPENING STATEMENT (Memorize this!)

**"Hello everyone. Today I'm going to explain the Raft Consensus Algorithm.**

**Imagine you have multiple computers that need to work together and agree on a leader. This code shows how they do it.**

**The main idea is: one leader, many followers. The leader makes decisions, and followers follow the leader's instructions."**

---

## CARD 5: EXAMPLE SCENARIO (Memorize this!)

**With 3 nodes:**

1. **Start**: All 3 nodes are followers
2. **Timeout**: Node 0 doesn't get heartbeat for 1s → becomes candidate
3. **Election**: Node 0 asks nodes 1 and 2 for votes
4. **Voting**: Nodes 1 and 2 vote for node 0
5. **Leader**: Node 0 gets 2 votes (majority) → becomes leader
6. **Heartbeat**: Node 0 sends heartbeat every 0.5s
7. **Crash**: If node 0 crashes → nodes 1 and 2 timeout and start new election

---

## CARD 6: COMMON QUESTIONS & ANSWERS

**Q: Why do we need a leader?**
A: "The leader coordinates decisions. Without a leader, nodes might make conflicting decisions."

**Q: Why 1 second timeout?**
A: "It's a balance. Too short = too many elections. Too long = slow to detect crashes."

**Q: Why 5 second cooldown?**
A: "It prevents the system from having too many elections. It gives the new leader time to stabilize."

**Q: Why majority voting?**
A: "It ensures only one leader is elected. With majority, two different leaders can't both get elected."

**Q: What if two nodes become candidates at the same time?**
A: "They both ask for votes. The one that gets majority first becomes leader. The other becomes follower."

---

## CARD 7: PRONUNCIATION PRACTICE

Read these out loud 5 times:

- **Raft**: /ræft/ - "RAFT" (like the boat)
- **Consensus**: /kənˈsɛnsəs/ - "con-SEN-sus"
- **Algorithm**: /ˈælɡərɪðəm/ - "AL-go-rith-um"
- **Candidate**: /ˈkændɪdeɪt/ - "CAN-di-date"
- **Heartbeat**: /ˈhɑːrtbiːt/ - "HART-beat"
- **Majority**: /məˈdʒɒrɪti/ - "ma-JOR-i-ty"
- **Timeout**: /ˈtaɪmaʊt/ - "TIME-out"
- **Cooldown**: /ˈkuːldaʊn/ - "COOL-down"

---

## CARD 8: PRESENTATION FLOW

```
1. INTRODUCTION (30s)
   ↓
2. WHAT IS THIS CODE? (1 min)
   ↓
3. THREE STATES (1 min)
   ↓
4. THREE MESSAGES (1 min)
   ↓
5. HOW IT WORKS - EXAMPLE (2 min)
   ↓
6. KEY CONCEPTS (1 min)
   ↓
7. WHY IS THIS IMPORTANT? (30s)
   ↓
8. CONCLUSION (30s)

TOTAL: 7-8 minutes
```

---

## CARD 9: PRACTICE CHECKLIST

- [ ] Read the script 3 times
- [ ] Memorize the three states
- [ ] Memorize the three messages
- [ ] Memorize the key numbers (1s, 0.5s, 2s, 5s)
- [ ] Practice the example scenario
- [ ] Practice pronunciation
- [ ] Time yourself - aim for 7-8 minutes
- [ ] Practice in front of a mirror
- [ ] Record yourself and listen
- [ ] Practice with a friend

---

## CARD 10: EMERGENCY BACKUP - SUPER SHORT VERSION

If you forget everything, remember this:

**"This code implements leader election. Nodes start as followers. If the leader disappears, they become candidates and vote for a new leader. The winner sends heartbeats to prove it's alive. If it crashes, the process repeats."**

That's it! That's the whole algorithm in 2 sentences.

---

## TIPS FOR MEMORIZATION

1. **Read out loud** - Don't just read silently
2. **Use the mind map** - Visual memory is stronger
3. **Practice the example** - Repeat steps 1-7 many times
4. **Teach someone else** - Explaining helps memorization
5. **Record yourself** - Listen to your own voice
6. **Use flashcards** - Cover and recall
7. **Practice timing** - Know how long each section takes
8. **Relax** - Don't stress, you know this!

Good luck! 🍀

