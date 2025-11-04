# Chord 实现 - 快速参考指南

## 核心概念速记

### 标识符圆 (m=3 的例子)
```
        0
    7       1
  6           2
    5       3
        4

节点: 0, 1, 3
数据分配:
- Node 0: (3, 0] = {4,5,6,7,0}
- Node 1: (0, 1] = {1}
- Node 3: (1, 3] = {2,3}
```

### 手指表 (Node 0, m=3)
```
finger[1].start = 1 → finger[1] = Node 1
finger[2].start = 2 → finger[2] = Node 3
finger[3].start = 4 → finger[3] = Node 0
```

---

## 关键方法速记

### 查询操作

| 方法 | 目的 | 返回值 |
|------|------|--------|
| `findSuccessor(caller, id)` | 找 id 的后继 | ChordNode |
| `findPredecessor(caller, id)` | 找 id 的前驱 | ChordNode |
| `closestPrecedingFinger(caller, id)` | 找最接近的手指 | ChordNode |

### 加入操作

| 方法 | 模式 | 目的 |
|------|------|------|
| `joinAndUpdate(nprime)` | 静态 | 一次性加入并更新 |
| `joinOnly(nprime)` | 动态 | 只设置后继 |
| `initFingerTable(nprime)` | 静态 | 初始化手指表 |
| `updateOthers()` | 静态 | 通知其他节点 |
| `updateFingerTable(s, i)` | 静态 | 更新单个手指 |

### 稳定化操作

| 方法 | 频率 | 目的 |
|------|------|------|
| `stabilize()` | 定期 | 验证后继 |
| `notify(nprime)` | 被调用 | 接收通知 |
| `fixFingers()` | 定期 | 刷新手指表 |
| `checkPredecessor()` | 定期 | 检查前驱 |
| `checkSuccessor()` | 定期 | 检查后继 |

### 数据操作

| 方法 | 目的 |
|------|------|
| `store(origin, key, value)` | 存储数据 |
| `lookup(origin, key)` | 查询数据 |
| `delete(origin, key)` | 删除数据 |
| `lookupNodeForItem(key)` | 找存储位置 |

---

## 区间类型速记

```
createLeftOpen(a, b)   → (a, b]   左开右闭
createRightOpen(a, b)  → [a, b)   左闭右开
createOpen(a, b)       → (a, b)   开区间

用途:
- 数据责任: (predecessor, this]
- 手指查询: (this, target)
- 手指复用: [this, finger[i])
```

---

## 常用代码片段

### 检查 id 是否在区间内
```java
IdentifierCircularInterval interval = createLeftOpen(a, b);
if (interval.contains(id)) {
    // id 在 (a, b] 范围内
}
```

### 获取手指
```java
Optional<ChordNode> finger = this.fingerTable.node(i);
if (finger.isPresent()) {
    ChordNode node = finger.get();
}
```

### 设置手指
```java
this.fingerTable.setNode(i, node);
```

### 获取手指表起始位置
```java
Identifier start = getNetwork().getIdentifierCircle()
    .getIdentifierAt(this.fingerTable.start(i));
```

### 转换 key 为 Identifier
```java
Identifier identifier = getNetwork().getIdentifierCircle()
    .getIdentifierAt(Integer.parseInt(key));
```

---

## 调试检查清单

### 加入后检查

- [ ] 手指表是否正确初始化?
- [ ] 前驱指针是否正确设置?
- [ ] 其他节点的手指表是否更新?
- [ ] 数据是否正确转移?
- [ ] 是否有数据丢失或重复?

### 查询问题排查

- [ ] findPredecessor 是否返回正确的前驱?
- [ ] closestPrecedingFinger 是否返回最接近的手指?
- [ ] 区间判断是否正确?
- [ ] 是否有无限循环?

### 稳定化问题排查

- [ ] stabilize() 是否定期调用?
- [ ] notify() 是否正确更新前驱?
- [ ] fixFingers() 是否刷新手指表?
- [ ] 是否有竞态条件?

---

## 性能指标

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 查询 | O(log n) | O(1) |
| 加入 | O(log² n) | O(log n) |
| 离开 | O(log n) | O(1) |
| 手指表 | - | O(log n) |

---

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 查询失败 | 手指表错误 | 检查 initFingerTable |
| 数据丢失 | 转移顺序错误 | 先删除后存储 |
| 无限循环 | 区间判断错误 | 检查区间类型 |
| 更新不完整 | 没有递归 | 添加递归调用 |
| 竞态条件 | 并发访问 | 使用同步 |

---

## 测试用例

### 基本测试
```
节点: 0, 1, 3
预期:
- Node 0: finger = [1, 3, 0]
- Node 1: finger = [3, 3, 0]
- Node 3: finger = [0, 0, 0]
```

### 动态加入测试
```
初始: 0, 1, 3
加入: 6
预期:
- Node 6: finger = [0, 0, 3]
- Node 3: finger = [6, 6, 0]
- Node 1: finger = [3, 3, 6]
- Node 0: finger = [1, 3, 6]
```

---

## 论文参考

**论文**: Chord: A Scalable Peer-to-Peer Lookup Service for Internet Applications

**关键图表**:
- Figure 4: 查询算法 (findSuccessor, findPredecessor, closestPrecedingFinger)
- Figure 6: 加入算法 (join, initFingerTable, updateOthers, updateFingerTable)
- Figure 7: 稳定化算法 (stabilize, notify, fixFingers)

---

## 汇报要点

1. **开场**: 解释 Chord 是什么，为什么需要它
2. **架构**: 介绍标识符圆、手指表、前驱指针
3. **查询**: 详细讲解 findSuccessor 和 findPredecessor
4. **加入**: 讲解 joinAndUpdate 的完整流程
5. **稳定化**: 讲解动态模式的稳定化机制
6. **数据**: 讲解数据如何存储和查询
7. **性能**: 讲解时间和空间复杂度
8. **测试**: 展示测试结果

---

## 可能的追问

**Q: 为什么使用圆形而不是线性?**
A: 圆形可以自然地处理边界情况，避免特殊处理

**Q: 手指表大小为什么是 m?**
A: m 个手指可以覆盖所有 2^m 个节点，实现 O(log n) 查询

**Q: 为什么需要前驱指针?**
A: 用于稳定化、数据转移和节点离开处理

**Q: 如何处理节点故障?**
A: 通过 checkPredecessor 和 checkSuccessor 定期检查

**Q: 如何保证数据一致性?**
A: 通过递归更新和定期稳定化

---

## 关键代码行

### findPredecessor 的核心
```java
while (!interval.contains(id)) {
    nprime = nprime.closestPrecedingFinger(caller, id);
    interval = createLeftOpen(nprime.id(), nprime.successor().id());
}
```

### closestPrecedingFinger 的核心
```java
for (int i = getNetwork().getNbits(); i >= 1; i--) {
    if (createOpen(this.id(), id).contains(finger_i.id())) {
        return finger_i;
    }
}
```

### updateFingerTable 的核心
```java
if (createLeftOpen(this.id(), node.id()).contains(s.id())) {
    this.fingerTable.setNode(i, s);
    this.predecessor().updateFingerTable(s, i);
}
```

### stabilize 的核心
```java
if (createOpen(this.id(), this.successor().id()).contains(x.id())) {
    this.fingerTable.setNode(1, x);
}
```

---

## 记忆技巧

**FIND**: Find Successor → Find Predecessor → Closest Preceding Finger
**JOIN**: Join → Init Finger Table → Update Others → Update Finger Table
**STAB**: Stabilize → Notify → Fix Fingers → Check Predecessor/Successor

---

## 最后检查

在汇报前确认:
- [ ] 理解每个方法的目的
- [ ] 能解释每行代码的含义
- [ ] 能用例子说明算法流程
- [ ] 能回答常见问题
- [ ] 能讨论性能和优化
- [ ] 能解释设计决策

