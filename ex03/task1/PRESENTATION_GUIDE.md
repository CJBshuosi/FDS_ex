# Chord P2P Network Implementation - 汇报指南

## 项目概述

这是一个基于论文 [1] 的 **Chord 分布式哈希表 (DHT)** 的 Java 实现。Chord 是一个可扩展的点对点查找服务，用于在分布式系统中定位数据。

### 核心概念

1. **Identifier Circle (标识符圆)**: 所有节点和数据项都被映射到一个 m-bit 的圆形标识符空间（0 到 2^m-1）
2. **Finger Table (手指表)**: 每个节点维护一个包含 m 个条目的表，用于快速路由查询
3. **Successor/Predecessor**: 每个节点知道其在圆上的直接后继和前驱节点

---

## 项目架构

### 关键类和接口

```
ChordNode (接口)
    ↑
    |
AbstractChordPeer (抽象类)
    ↑
    |
ChordPeer (你实现的类) ← 主要工作
```

### 核心数据结构

- **Identifier**: 表示节点或数据项的标识符（包含 hash 和 index）
- **FingerTable**: 存储指向其他节点的指针，用于快速路由
- **IdentifierCircularInterval**: 表示圆形标识符空间中的区间

---

## 你完成的核心方法解释

### 1. **findSuccessor(ChordNode caller, Identifier id)** - 查找后继节点

**目的**: 找到标识符 id 的后继节点

**实现逻辑**:
```java
ChordNode nprime = this.findPredecessor(caller, id);
return nprime.successor();
```

**解释**:
- 先找到 id 的前驱节点 nprime
- 返回 nprime 的后继（因为后继就是 id 的后继）

**参数**:
- `caller`: 调用者（用于模拟/日志）
- `id`: 要查找的标识符

---

### 2. **findPredecessor(ChordNode caller, Identifier id)** - 查找前驱节点

**目的**: 找到标识符 id 的前驱节点

**实现逻辑**:
```java
ChordNode nprime = this;
IdentifierCircularInterval interval = createLeftOpen(nprime.id(), nprime.successor().id());
while (!interval.contains(id)) {
    nprime = nprime.closestPrecedingFinger(caller, id);
    interval = createLeftOpen(nprime.id(), nprime.successor().id());
}
return nprime;
```

**解释**:
- 从当前节点开始
- 检查 id 是否在 (nprime, nprime.successor()] 区间内
- 如果不在，找到最接近 id 的前驱手指，继续搜索
- 循环直到找到正确的前驱节点

**关键概念**:
- `createLeftOpen(a, b)`: 创建左开右闭区间 (a, b]
- 这个算法是 Chord 的核心路由机制

---

### 3. **closestPrecedingFinger(ChordNode caller, Identifier id)** - 找最接近的手指

**目的**: 在手指表中找到最接近 id 的前驱手指

**实现逻辑**:
```java
for (int i = getNetwork().getNbits(); i >= 1; i--) {
    if (this.fingerTable.node(i).isPresent()) {
        ChordNode finger_i = this.fingerTable.node(i).get();
        if (createOpen(this.id(), id).contains(finger_i.id())) {
            return finger_i;
        }
    }
}
return this;
```

**解释**:
- 从最大的手指开始向下遍历（从 m 到 1）
- 检查手指是否在 (this.id(), id) 开区间内
- 返回第一个满足条件的手指
- 如果没有找到，返回自己

**为什么从大到小遍历?** 因为大的手指指向更远的节点，能更快地接近目标

---

### 4. **joinAndUpdate(ChordNode nprime)** - 静态模式下的加入

**目的**: 新节点加入网络（静态模式，无稳定化）

**实现逻辑**:
```java
if (nprime != null) {
    initFingerTable(nprime);
    // 从后继节点转移数据
    Map<String, String> temp_storage = new ConcurrentHashMap<>();
    ChordNode successor = this.fingerTable.node(1).get();
    for (String key : successor.keys()) {
        String value = successor.delete(this, key).get();
        temp_storage.put(key, value);
    }
    updateOthers();
    // 重新分配数据
    Identifier left_bound = this.predecessor().id();
    IdentifierCircularInterval interval = createLeftOpen(left_bound, this.id());
    for (String key : temp_storage.keySet()) {
        Identifier key_id = getNetwork().getIdentifierCircle().getIdentifierAt(Integer.parseInt(key));
        if (interval.contains(key_id)) {
            this.store(this, key, temp_storage.remove(key));
        } else {
            successor.store(this, key, temp_storage.remove(key));
        }
    }
} else {
    // 第一个节点：所有手指指向自己
    for (int i = 1; i <= getNetwork().getNbits(); i++) {
        this.fingerTable.setNode(i, this);
    }
    this.setPredecessor(this);
}
```

**关键步骤**:
1. **initFingerTable**: 初始化手指表
2. **转移数据**: 从后继节点获取属于新节点的数据
3. **updateOthers**: 通知其他节点更新它们的手指表
4. **重新分配**: 将数据分配给正确的节点

---

### 5. **initFingerTable(ChordNode nprime)** - 初始化手指表

**目的**: 基于已有节点 nprime 初始化新节点的手指表

**实现逻辑**:
```java
Identifier ident = getNetwork().getIdentifierCircle().getIdentifierAt(this.fingerTable.start(1));
this.fingerTable.setNode(1, nprime.findSuccessor(this, ident));
this.setPredecessor(this.successor().predecessor());
this.successor().setPredecessor(this);

for (int i = 1; i <= getNetwork().getNbits() - 1; i++) {
    ChordNode finger_i = this.fingerTable.node(i).get();
    Identifier start = getNetwork().getIdentifierCircle().getIdentifierAt(this.fingerTable.start(i + 1));
    if (createRightOpen(this.id(), finger_i.id()).contains(start)) {
        this.fingerTable.setNode(i + 1, finger_i);
    } else {
        start = getNetwork().getIdentifierCircle().getIdentifierAt(this.finger().start(i + 1));
        this.fingerTable.setNode(i + 1, nprime.findSuccessor(this, start));
    }
}
```

**关键步骤**:
1. 找到第一个手指（后继）
2. 设置前驱指针
3. 对于每个后续手指，如果可以复用前一个手指，就复用；否则查询新的

---

### 6. **updateOthers()** - 更新其他节点的手指表

**目的**: 通知所有需要更新的节点，将新节点加入它们的手指表

**实现逻辑**:
```java
for (int i = 1; i <= getNetwork().getNbits(); i++) {
    Identifier ident = getNetwork().getIdentifierCircle().getIdentifierAt(
        this.id().getIndex() - (int) Math.pow(2, i - 1)
    );
    ChordNode p = this.findPredecessor(this, ident);
    if (p.successor().id().equals(ident)) {
        p = p.successor();
    }
    p.updateFingerTable(this, i);
}
```

**解释**:
- 对于每个手指位置 i，计算应该被更新的节点
- 找到那个节点，调用其 updateFingerTable 方法

---

### 7. **updateFingerTable(ChordNode s, int i)** - 更新单个手指表条目

**目的**: 如果节点 s 应该是第 i 个手指，则更新

**实现逻辑**:
```java
finger().node(i).ifPresent(node -> {
    if (createLeftOpen(this.id(), node.id()).contains(s.id())) {
        this.fingerTable.setNode(i, s);
        ChordNode p = this.predecessor();
        p.updateFingerTable(s, i);
    }
});
```

**解释**:
- 检查 s 是否在 (this.id(), 当前第i个手指) 区间内
- 如果是，更新手指表并递归通知前驱节点

---

### 8. **stabilize()** - 稳定化（动态模式）

**目的**: 定期验证后继节点并通知它

**实现逻辑**:
```java
if (this.successor().predecessor() != null) {
    ChordNode x = this.successor().predecessor();
    if (createOpen(this.id(), this.successor().id()).contains(x.id())) {
        this.fingerTable.setNode(1, x);
    }
}
this.successor().notify(this);
```

**解释**:
- 检查后继的前驱是否更合适
- 通知后继自己的存在

---

### 9. **notify(ChordNode nprime)** - 接收通知

**目的**: 当另一个节点认为它可能是我们的前驱时调用

**实现逻辑**:
```java
if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;
if (this.predecessor() == null || createOpen(this.predecessor().id(), this.id()).contains(nprime.id())) {
    this.setPredecessor(nprime);
}
```

**解释**:
- 如果没有前驱，或者 nprime 在 (前驱, 自己) 区间内，则更新前驱

---

### 10. **lookupNodeForItem(String key)** - 查找数据存储位置

**目的**: 确定数据应该存储在哪个节点

**实现逻辑**:
```java
Identifier identifier = getNetwork().getIdentifierCircle().getIdentifierAt(Integer.parseInt(key));
if (predecessor() != null) {
    return this.findSuccessor(this, identifier);
}
return this;
```

**解释**:
- 将 key 转换为标识符
- 找到该标识符的后继节点
- 数据存储在其后继节点上

---

## 重要的数据结构和方法

### IdentifierCircularInterval 方法

- `createLeftOpen(a, b)`: 创建 (a, b] 区间
- `createRightOpen(a, b)`: 创建 [a, b) 区间
- `createOpen(a, b)`: 创建 (a, b) 区间
- `contains(id)`: 检查 id 是否在区间内

### FingerTable 方法

- `start(i)`: 第 i 个手指的起始标识符
- `node(i)`: 获取第 i 个手指指向的节点
- `setNode(i, node)`: 设置第 i 个手指

---

## 可能的考试问题

### 理论问题

1. **Chord 的基本原理是什么?**
   - 答: 使用一致性哈希将节点和数据映射到一个圆形标识符空间，每个节点维护一个手指表用于快速路由

2. **为什么需要手指表?**
   - 答: 手指表使得查询时间复杂度从 O(n) 降低到 O(log n)

3. **静态模式和动态模式的区别?**
   - 答: 静态模式在加入时一次性更新所有信息；动态模式通过定期稳定化逐步修复网络

4. **为什么 closestPrecedingFinger 从大到小遍历?**
   - 答: 大的手指指向更远的节点，能更快地接近目标

5. **数据重新分配的原理?**
   - 答: 新节点加入后，原来属于它的数据需要从后继节点转移过来

### 代码问题

1. **findPredecessor 中为什么使用左开右闭区间?**
   - 答: 确保每个标识符恰好属于一个节点的责任范围

2. **updateFingerTable 为什么要递归调用?**
   - 答: 因为如果前驱节点也需要更新，它的前驱可能也需要更新

3. **stabilize 中为什么要检查 successor().predecessor()?**
   - 答: 因为可能有新节点加入到自己和后继之间

4. **joinAndUpdate 中为什么要先删除再存储?**
   - 答: 确保数据的一致性，避免重复

---

## 测试场景

### 基本测试 (testFingerTableNodeZero)

3 个节点 (0, 1, 3) 加入网络：
- Node 0 的手指表: [1, 3, 0]
- 这表示: finger[1]=1, finger[2]=3, finger[3]=0

### 动态加入测试 (testJoinOnThree)

Node 6 加入后，所有节点的手指表都会更新

---

## 关键参数和变量解释

| 变量 | 含义 |
|------|------|
| `m` | 标识符空间的位数 (2^m 个节点) |
| `i` | 手指表的索引 (1 到 m) |
| `fingerTable.start(i)` | 第 i 个手指的起始标识符 = (this.id + 2^(i-1)) mod 2^m |
| `nprime` | 已在网络中的参考节点 |
| `caller` | 调用者（用于模拟） |
| `interval` | 圆形标识符空间中的区间 |

---

## 汇报建议

1. **从整体架构开始**: 解释 Chord 的基本概念
2. **逐个讲解核心方法**: 从简单到复杂
3. **用具体例子**: 用 3 节点网络的例子说明
4. **强调关键设计**: 为什么这样设计，有什么优势
5. **准备应对深入问题**: 理解每行代码的含义

祝你汇报顺利！

