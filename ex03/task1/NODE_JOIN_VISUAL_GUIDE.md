# Chord 节点加入可视化指南

## 初始网络可视化

### 标识符圆

```
        0
    7       1
  6           2
    5       3
        4

节点位置: 1, 2, 3
```

### 初始拓扑图

```
Node1 ←→ Node2 ←→ Node3 ←→ Node1
  ↑                           ↓
  └───────────────────────────┘

前驱指针:
Node1 ← Node3
Node2 ← Node1
Node3 ← Node2
```

### 初始手指表矩阵

```
┌─────────────────────────────────────┐
│ 节点  │ finger[1] │ finger[2] │ finger[3] │
├─────────────────────────────────────┤
│ Node1 │  Node2   │  Node3   │  Node1   │
│ Node2 │  Node3   │  Node1   │  Node1   │
│ Node3 │  Node1   │  Node1   │  Node1   │
└─────────────────────────────────────┘
```

---

## 加入过程可视化

### 阶段 1: initFingerTable

#### 1.1 查询 finger[1] (后继)

```
Node6 查询: "谁是 7 的后继?"

Node6 → Node1.findSuccessor(7)
  ↓
Node1.findPredecessor(7)
  ↓
Node1 检查: 7 在 (1, 2] 吗? 不在
  ↓
Node1 查找最接近的手指
  ↓
Node1.closestPrecedingFinger(7)
  检查 finger[3]=Node1: 1 在 (1,7) 吗? 不在
  检查 finger[2]=Node3: 3 在 (1,7) 吗? 是!
  ↓
返回 Node3
  ↓
Node3 检查: 7 在 (3, 1] 吗? 是!
  ↓
返回 Node3 (7 的前驱)
  ↓
返回 Node3.successor() = Node1

结果: Node6.finger[1] = Node1
```

#### 1.2 设置前驱指针

```
Node6.predecessor = Node1.predecessor = Node3
Node1.predecessor = Node6 (已更新)

拓扑变化:
Node3 → Node6 → Node1 → Node2 → Node3
```

#### 1.3 初始化 finger[2]

```
Node6 检查: start(2) = (6 + 2) mod 8 = 0

检查: [6, 1) 包含 0 吗?
在圆形中: 6 → 7 → 0 → 1
所以 [6, 1) = {6, 7, 0}
0 在其中吗? 是!

可以复用 finger[1]:
Node6.finger[2] = Node6.finger[1] = Node1
```

#### 1.4 初始化 finger[3]

```
Node6 检查: start(3) = (6 + 4) mod 8 = 2

检查: [6, 1) 包含 2 吗?
[6, 1) = {6, 7, 0}
2 在其中吗? 不在!

需要查询:
Node6 → Node1.findSuccessor(2)
  ↓
Node1.findPredecessor(2)
  ↓
Node1 检查: 2 在 (1, 2] 吗? 是!
  ↓
返回 Node1 (2 的前驱)
  ↓
返回 Node1.successor() = Node2

结果: Node6.finger[3] = Node2
```

#### 1.5 initFingerTable 完成

```
Node6 的手指表:
┌──────────────────────┐
│ finger[1] = Node1    │
│ finger[2] = Node1    │
│ finger[3] = Node2    │
└──────────────────────┘

Node6 的前驱: Node3
```

### 阶段 2: 转移数据

```
Node1 原本负责的数据: {4, 5, 6, 7, 0, 1}

转移到 temp_storage:
temp_storage = {4, 5, 6, 7, 0, 1}

Node1 现在为空
```

### 阶段 3: updateOthers - 通知其他节点

#### 3.1 更新 finger[1]

```
计算: ident = (6 - 2^0) mod 8 = 5

查询: findPredecessor(5)
  ↓
从 Node6 开始
Node6 检查: 5 在 (3, 6] 吗? 是!
  ↓
返回 Node6

Node6.updateFingerTable(Node6, 1)
  检查: (6, 1] 包含 6 吗? 不在
  不更新
```

#### 3.2 更新 finger[2]

```
计算: ident = (6 - 2^1) mod 8 = 4

查询: findPredecessor(4)
  ↓
从 Node6 开始
Node6 检查: 4 在 (3, 6] 吗? 是!
  ↓
返回 Node6

Node6.updateFingerTable(Node6, 2)
  检查: (6, 1] 包含 6 吗? 不在
  不更新
```

#### 3.3 更新 finger[3]

```
计算: ident = (6 - 2^2) mod 8 = 2

查询: findPredecessor(2)
  ↓
从 Node6 开始
Node6 检查: 2 在 (3, 6] 吗? 不在
  ↓
Node6.closestPrecedingFinger(2)
  检查 finger[3]=Node2: 2 在 (6, 2) 吗? 是!
  ↓
返回 Node2
  ↓
Node2 检查: 2 在 (2, 3] 吗? 不在
  ↓
Node2.closestPrecedingFinger(2)
  检查 finger[3]=Node1: 1 在 (2, 2) 吗? 不在
  检查 finger[2]=Node1: 1 在 (2, 2) 吗? 不在
  检查 finger[1]=Node3: 3 在 (2, 2) 吗? 不在
  ↓
返回 Node2
  ↓
返回 Node2

Node2.updateFingerTable(Node6, 3)
  检查: (2, 1] 包含 6 吗? 是!
  ↓
  Node2.finger[3] = Node6 (已更新!)
  ↓
  Node2.predecessor().updateFingerTable(Node6, 3)
  Node1.updateFingerTable(Node6, 3)
    检查: (1, 1] 包含 6 吗? 不在 (空区间)
    不更新
```

### 阶段 4: 重新分配数据

```
Node6 的责任范围: (3, 6] = {4, 5, 6}

temp_storage = {4, 5, 6, 7, 0, 1}

分配过程:
┌─────────────────────────────────────┐
│ key │ 在 (3,6] 吗? │ 目标节点 │ 结果 │
├─────────────────────────────────────┤
│  4  │     是      │ Node6   │ ✓   │
│  5  │     是      │ Node6   │ ✓   │
│  6  │     是      │ Node6   │ ✓   │
│  7  │     不在    │ Node1   │ ✓   │
│  0  │     不在    │ Node1   │ ✓   │
│  1  │     不在    │ Node1   │ ✓   │
└─────────────────────────────────────┘

最终分配:
Node6: {4, 5, 6}
Node1: {7, 0, 1}
```

---

## 最终状态可视化

### 最终拓扑图

```
Node3 → Node6 → Node1 → Node2 → Node3
  ↑                               ↓
  └───────────────────────────────┘

前驱指针:
Node1 ← Node6
Node2 ← Node1
Node3 ← Node2
Node6 ← Node3
```

### 最终手指表矩阵

```
┌─────────────────────────────────────┐
│ 节点  │ finger[1] │ finger[2] │ finger[3] │
├─────────────────────────────────────┤
│ Node1 │  Node6   │  Node3   │  Node6   │
│ Node2 │  Node3   │  Node1   │  Node6   │
│ Node3 │  Node1   │  Node1   │  Node1   │
│ Node6 │  Node1   │  Node1   │  Node2   │
└─────────────────────────────────────┘
```

### 最终数据分配

```
标识符圆:
        0
    7       1
  6           2
    5       3
        4

数据分配:
Node1: (6, 1] = {7, 0, 1}
Node2: (1, 2] = {2}
Node3: (2, 3] = {3}
Node6: (3, 6] = {4, 5, 6}

验证:
- 每个数据恰好由一个节点负责 ✓
- 所有数据都被覆盖 ✓
- 没有重叠 ✓
```

---

## 关键计算详解

### 手指表 start 计算

```
对于 Node6 (m=3):

finger[1].start = (6 + 2^(1-1)) mod 8 = (6 + 1) mod 8 = 7
finger[2].start = (6 + 2^(2-1)) mod 8 = (6 + 2) mod 8 = 0
finger[3].start = (6 + 2^(3-1)) mod 8 = (6 + 4) mod 8 = 2
```

### 区间判断

```
左开右闭区间 (a, b]:
- 包含 a 和 b 之间的所有元素
- 不包含 a，包含 b
- 在圆形中处理

例子 (m=3):
(3, 6] = {4, 5, 6}
(6, 1] = {7, 0, 1}
(1, 2] = {2}
(2, 3] = {3}

验证: 所有元素都被覆盖，没有重叠
```

### 圆形距离

```
在圆形中，从 a 到 b 的距离:
distance(a, b) = (b - a) mod 2^m

例子:
distance(6, 1) = (1 - 6) mod 8 = -5 mod 8 = 3
distance(1, 6) = (6 - 1) mod 8 = 5

所以 6 到 1 的距离是 3，1 到 6 的距离是 5
```

---

## 对比表

### 加入前后的变化

```
┌──────────────────────────────────────────────────────┐
│ 项目 │ 加入前 │ 加入后 │ 变化 │
├──────────────────────────────────────────────────────┤
│ 节点数 │ 3 │ 4 │ +1 │
│ Node1.finger[1] │ Node2 │ Node6 │ 更新 │
│ Node1.finger[3] │ Node1 │ Node6 │ 更新 │
│ Node1.predecessor │ Node3 │ Node6 │ 更新 │
│ Node2.finger[3] │ Node1 │ Node6 │ 更新 │
│ Node1 数据 │ {4,5,6,7,0,1} │ {7,0,1} │ -3 │
│ Node6 数据 │ 无 │ {4,5,6} │ +3 │
└──────────────────────────────────────────────────────┘
```

---

## 常见问题

### Q1: 为什么 finger[2] 可以复用 finger[1]?

```
因为 start(2) = 0 在 [6, 1) 范围内

[6, 1) 表示从 6 开始到 1 (不包括 1) 的范围
在圆形中: {6, 7, 0}

0 在其中，所以 finger[2] 可以指向同一个节点
```

### Q2: 为什么 updateOthers 需要递归?

```
当 Node2.finger[3] 更新为 Node6 时，
需要通知 Node2 的前驱 Node1 也检查是否需要更新

这样可以确保所有受影响的节点都被更新
```

### Q3: 为什么数据要先删除再存储?

```
避免数据重复:
1. 如果直接复制，可能导致数据在两个节点上
2. 先删除确保数据只在一个地方
3. 然后根据责任范围重新分配
```

### Q4: 为什么使用左开右闭区间?

```
确保每个数据恰好由一个节点负责:
- (3, 6] 包含 4, 5, 6
- (6, 1] 包含 7, 0, 1
- 没有重叠，没有遗漏
```

---

## 总结

### 加入的 5 个关键步骤

1. **initFingerTable** - 初始化手指表
   - 查询后继
   - 设置前驱
   - 初始化手指 (可复用)

2. **转移数据** - 从后继获取数据
   - 删除后继的数据
   - 存储到临时缓冲区

3. **updateOthers** - 通知其他节点
   - 对每个手指位置
   - 找到应该被更新的节点
   - 调用 updateFingerTable

4. **递归更新** - 传播更新
   - 检查是否应该更新
   - 递归通知前驱

5. **重新分配数据** - 分配给正确的节点
   - 属于新节点的数据存在新节点
   - 其他数据转发给后继

### 关键概念

- **手指表复用**: 减少查询次数
- **递归更新**: 确保一致性
- **区间判断**: 确保数据分配正确
- **圆形拓扑**: 自然处理边界情况

