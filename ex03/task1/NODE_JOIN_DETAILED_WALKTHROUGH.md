# Chord 节点加入详细推导 - Node6 加入网络

## 初始状态

### 网络参数
- **m = 3** (3-bit 标识符空间)
- **标识符范围**: 0 到 7 (2^3 - 1)
- **现有节点**: Node1, Node2, Node3
- **加入节点**: Node6

### 初始网络拓扑

```
        0
    7       1
  6           2
    5       3
        4

现有节点: 1, 2, 3
加入节点: 6
```

### 初始手指表

**Node1 的手指表**:
```
finger[1].start = (1 + 2^0) mod 8 = 2 → finger[1] = Node2
finger[2].start = (1 + 2^1) mod 8 = 3 → finger[2] = Node3
finger[3].start = (1 + 2^2) mod 8 = 5 → finger[3] = Node1
```

**Node2 的手指表**:
```
finger[1].start = (2 + 2^0) mod 8 = 3 → finger[1] = Node3
finger[2].start = (2 + 2^1) mod 8 = 4 → finger[2] = Node1
finger[3].start = (2 + 2^2) mod 8 = 6 → finger[3] = Node1
```

**Node3 的手指表**:
```
finger[1].start = (3 + 2^0) mod 8 = 4 → finger[1] = Node1
finger[2].start = (3 + 2^1) mod 8 = 5 → finger[2] = Node1
finger[3].start = (3 + 2^2) mod 8 = 7 → finger[3] = Node1
```

### 初始前驱指针
```
Node1.predecessor = Node3
Node2.predecessor = Node1
Node3.predecessor = Node2
```

### 初始数据分配
```
Node1 负责: (3, 1] = {4, 5, 6, 7, 0, 1}
Node2 负责: (1, 2] = {2}
Node3 负责: (2, 3] = {3}
```

---

## 第一步：Node6 调用 joinAndUpdate(Node1)

Node6 选择 Node1 作为参考节点，调用 `joinAndUpdate(Node1)`

### 代码执行:
```java
public void joinAndUpdate(ChordNode nprime) {  // nprime = Node1
    if (nprime != null) {
        initFingerTable(nprime);  // 第一步
        // ...
    }
}
```

---

## 第二步：initFingerTable(Node1) - 初始化手指表

### 步骤 2.1: 初始化 finger[1] (后继)

```
Identifier ident = getIdentifierAt(this.fingerTable.start(1))
            = getIdentifierAt((6 + 2^0) mod 8)
            = getIdentifierAt(7)

this.fingerTable.setNode(1, nprime.findSuccessor(this, ident))
                = Node1.findSuccessor(Node6, 7)
```

**查询过程** (Node1 查找 7 的后继):
```
findSuccessor(7):
  nprime = findPredecessor(7)
  
  findPredecessor(7):
    nprime = Node1
    interval = (1, 2]
    7 在 (1, 2] 吗? 不在
    
    nprime = Node1.closestPrecedingFinger(7)
    检查 finger[3] = Node1: 1 在 (1, 7) 吗? 不在
    检查 finger[2] = Node3: 3 在 (1, 7) 吗? 是! 返回 Node3
    
    nprime = Node3
    interval = (3, 1]
    7 在 (3, 1] 吗? 是! (因为是圆形: 3 < 7 < 8 或 0 < 1)
    返回 Node3
  
  return Node3.successor() = Node1
```

**结果**: `Node6.finger[1] = Node1`

### 步骤 2.2: 设置前驱指针

```
this.setPredecessor(this.successor().predecessor())
                  = Node1.predecessor()
                  = Node3

Node6.predecessor = Node3

this.successor().setPredecessor(this)
Node1.setPredecessor(Node6)
```

**当前状态**:
```
Node6.finger[1] = Node1
Node6.predecessor = Node3
Node1.predecessor = Node6 (已更新)
```

### 步骤 2.3: 初始化 finger[2]

```
i = 1:
  finger_i = finger[1] = Node1
  start = getIdentifierAt(this.fingerTable.start(2))
        = getIdentifierAt((6 + 2^1) mod 8)
        = getIdentifierAt(0)
  
  检查: createRightOpen(6, 1).contains(0)?
       [6, 1) 包含 0 吗?
       在圆形中: [6, 7, 0] 包含 0? 是!
  
  this.fingerTable.setNode(2, finger[1])
  Node6.finger[2] = Node1
```

**结果**: `Node6.finger[2] = Node1`

### 步骤 2.4: 初始化 finger[3]

```
i = 2:
  finger_i = finger[2] = Node1
  start = getIdentifierAt(this.fingerTable.start(3))
        = getIdentifierAt((6 + 2^2) mod 8)
        = getIdentifierAt(2)
  
  检查: createRightOpen(6, 1).contains(2)?
       [6, 1) 包含 2 吗?
       在圆形中: [6, 7, 0] 包含 2? 不在!
  
  需要查询:
  start = getIdentifierAt(this.finger().start(3))
        = getIdentifierAt(2)
  
  this.fingerTable.setNode(3, nprime.findSuccessor(this, 2))
                         = Node1.findSuccessor(Node6, 2)
```

**查询过程** (Node1 查找 2 的后继):
```
findSuccessor(2):
  nprime = findPredecessor(2)
  
  findPredecessor(2):
    nprime = Node1
    interval = (1, 2]
    2 在 (1, 2] 吗? 是!
    返回 Node1
  
  return Node1.successor() = Node1.finger[1] = Node2
```

**结果**: `Node6.finger[3] = Node2`

### initFingerTable 完成

```
Node6 的手指表:
  finger[1] = Node1
  finger[2] = Node1
  finger[3] = Node2

Node6 的前驱: Node3
```

---

## 第三步：转移数据

### 步骤 3.1: 从后继获取数据

```java
Map<String, String> temp_storage = new ConcurrentHashMap<>();
ChordNode successor = this.fingerTable.node(1).get();  // Node1
for (String key : successor.keys()) {
    String value = successor.delete(this, key).get();
    temp_storage.put(key, value);
}
```

**Node1 原本负责的数据**: {4, 5, 6, 7, 0, 1}

**删除后的 temp_storage**: {4, 5, 6, 7, 0, 1}

---

## 第四步：updateOthers() - 通知其他节点

### 步骤 4.1: 更新 finger[1]

```
i = 1:
  ident = getIdentifierAt(6 - 2^0)
        = getIdentifierAt(5)
  
  p = findPredecessor(5)
  
  findPredecessor(5):
    从 Node6 开始
    nprime = Node6
    interval = (3, 6]
    5 在 (3, 6] 吗? 是!
    返回 Node6
  
  p = Node6
  p.successor().id() == 5? Node1.id() == 5? 不是
  
  p.updateFingerTable(Node6, 1)
  Node6.updateFingerTable(Node6, 1)
```

**Node6.updateFingerTable(Node6, 1)**:
```
检查: createLeftOpen(6, 1).contains(6)?
     (6, 1] 包含 6 吗? 不在 (6 不在开区间内)
     不更新
```

### 步骤 4.2: 更新 finger[2]

```
i = 2:
  ident = getIdentifierAt(6 - 2^1)
        = getIdentifierAt(4)
  
  p = findPredecessor(4)
  
  findPredecessor(4):
    从 Node6 开始
    nprime = Node6
    interval = (3, 6]
    4 在 (3, 6] 吗? 是!
    返回 Node6
  
  p = Node6
  p.successor().id() == 4? Node1.id() == 4? 不是
  
  p.updateFingerTable(Node6, 2)
  Node6.updateFingerTable(Node6, 2)
```

**Node6.updateFingerTable(Node6, 2)**:
```
检查: createLeftOpen(6, 1).contains(6)?
     不在
     不更新
```

### 步骤 4.3: 更新 finger[3]

```
i = 3:
  ident = getIdentifierAt(6 - 2^2)
        = getIdentifierAt(2)
  
  p = findPredecessor(2)
  
  findPredecessor(2):
    从 Node6 开始
    nprime = Node6
    interval = (3, 6]
    2 在 (3, 6] 吗? 不在
    
    nprime = Node6.closestPrecedingFinger(2)
    检查 finger[3] = Node2: 2 在 (6, 2) 吗? 是! 返回 Node2
    
    nprime = Node2
    interval = (2, 3]
    2 在 (2, 3] 吗? 不在
    
    nprime = Node2.closestPrecedingFinger(2)
    检查 finger[3] = Node1: 1 在 (2, 2) 吗? 不在
    检查 finger[2] = Node1: 1 在 (2, 2) 吗? 不在
    检查 finger[1] = Node3: 3 在 (2, 2) 吗? 不在
    返回 Node2
    
    nprime = Node2
    interval = (2, 3]
    2 在 (2, 3] 吗? 不在 (无限循环检测)
    返回 Node2
  
  p = Node2
  p.successor().id() == 2? Node3.id() == 2? 不是
  
  p.updateFingerTable(Node6, 3)
  Node2.updateFingerTable(Node6, 3)
```

**Node2.updateFingerTable(Node6, 3)**:
```
检查: createLeftOpen(2, 1).contains(6)?
     (2, 1] 包含 6 吗? 是! (2 < 6 < 8 或 0 < 1)
     
     Node2.finger[3] = Node6
     Node2.predecessor().updateFingerTable(Node6, 3)
     Node1.updateFingerTable(Node6, 3)
```

**Node1.updateFingerTable(Node6, 3)**:
```
检查: createLeftOpen(1, 1).contains(6)?
     (1, 1] 包含 6 吗? 不在 (空区间)
     不更新
```

---

## 第五步：重新分配数据

```java
Identifier left_bound = this.predecessor().id();  // Node3 = 3
IdentifierCircularInterval interval = createLeftOpen(3, 6);  // (3, 6]

for (String key : temp_storage.keySet()) {
    Identifier key_id = getIdentifierAt(Integer.parseInt(key));
    if (interval.contains(key_id)) {
        this.store(this, key, temp_storage.remove(key));
    } else {
        successor.store(this, key, temp_storage.remove(key));
    }
}
```

**数据分配**:
```
temp_storage = {4, 5, 6, 7, 0, 1}

key = 4: 4 在 (3, 6] 吗? 是! → Node6.store(4)
key = 5: 5 在 (3, 6] 吗? 是! → Node6.store(5)
key = 6: 6 在 (3, 6] 吗? 是! → Node6.store(6)
key = 7: 7 在 (3, 6] 吗? 不在 → Node1.store(7)
key = 0: 0 在 (3, 6] 吗? 不在 → Node1.store(0)
key = 1: 1 在 (3, 6] 吗? 不在 → Node1.store(1)
```

---

## 最终状态

### 最终手指表

**Node1 的手指表** (已更新):
```
finger[1] = Node6 (原来是 Node2)
finger[2] = Node3
finger[3] = Node6 (原来是 Node1)
```

**Node2 的手指表** (已更新):
```
finger[1] = Node3
finger[2] = Node1
finger[3] = Node6 (原来是 Node1)
```

**Node3 的手指表** (未变):
```
finger[1] = Node1
finger[2] = Node1
finger[3] = Node1
```

**Node6 的手指表** (新):
```
finger[1] = Node1
finger[2] = Node1
finger[3] = Node2
```

### 最终前驱指针
```
Node1.predecessor = Node6 (已更新)
Node2.predecessor = Node1
Node3.predecessor = Node2
Node6.predecessor = Node3 (新)
```

### 最终数据分配
```
Node1 负责: (6, 1] = {7, 0, 1}
Node2 负责: (1, 2] = {2}
Node3 负责: (2, 3] = {3}
Node6 负责: (3, 6] = {4, 5, 6}
```

---

## 总结

### 加入过程的 5 个步骤

1. **initFingerTable** - 初始化新节点的手指表
   - 查询后继
   - 设置前驱指针
   - 初始化所有手指

2. **转移数据** - 从后继获取属于新节点的数据
   - 删除后继的数据
   - 存储到临时缓冲区

3. **updateOthers** - 通知其他节点更新手指表
   - 对每个手指位置 i
   - 找到应该被更新的节点
   - 调用其 updateFingerTable 方法

4. **递归更新** - updateFingerTable 递归传播更新
   - 检查是否应该更新
   - 如果是，更新并递归通知前驱

5. **重新分配数据** - 将数据分配给正确的节点
   - 属于新节点的数据存在新节点
   - 其他数据转发给后继

### 关键概念

- **手指表复用**: 如果 start(i+1) 在 [this, finger[i]) 范围内，可以复用 finger[i]
- **递归更新**: updateFingerTable 递归调用确保所有受影响的节点都被更新
- **区间判断**: 使用左开右闭区间 (a, b] 确保每个数据恰好由一个节点负责
- **数据转移**: 先删除再存储，避免数据重复

### 时间复杂度

- **initFingerTable**: O(log² n) - 需要 log n 次查询，每次查询 O(log n)
- **updateOthers**: O(log n) - 需要通知 log n 个节点
- **数据转移**: O(k) - k 是转移的数据量
- **总计**: O(log² n + k)

