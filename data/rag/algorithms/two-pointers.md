---
id: "two-pointers"
concept: "双指针"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 4
is_milestone: false
tags: ["技巧"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 双指针

## 概述

双指针（Two Pointers）是一种使用两个索引变量同时遍历数组或链表的算法技巧，通过控制两个指针的移动方向和速度，将原本需要 $O(n^2)$ 的暴力枚举降低至 $O(n)$ 或 $O(n \log n)$ 的时间复杂度。两个指针可以从同一端出发（快慢指针），也可以从两端向中间收拢（对撞指针），具体选择取决于问题的约束条件。

双指针技巧最早在算法竞赛领域被系统总结，与荷兰国旗问题（Dutch National Flag Problem）密切相关——该问题由 Edsger W. Dijkstra 于1976年在其著作《A Discipline of Programming》中正式提出，其三路划分解法（将数组分为小于、等于、大于枢轴三段）正是双指针思想的经典体现。Floyd 判圈算法（Floyd's Cycle Detection Algorithm）由 Robert W. Floyd 于1967年独立提出，早期记录见于 Donald E. Knuth 的《The Art of Computer Programming, Volume 2》（1969年，第3.1节），是快慢指针在链表场景下的奠基性工作。LeetCode 平台上标注为"Two Pointers"的题目超过 150 道，是技术面试高频考点之一，也是滑动窗口（Sliding Window）、快速排序分区（Partition）等高级技巧的直接前身。

双指针的核心价值在于利用数据的有序性或特定约束消除冗余计算。以在长度为 $n$ 的有序数组中寻找两数之和为例：暴力枚举需要检查所有 $\binom{n}{2} = \frac{n(n-1)}{2}$ 个候选对，当 $n = 10^4$ 时约需 5000 万次操作；而对撞指针每一步都能根据当前和与目标值的大小关系确定性地排除至少一个元素，使总操作次数严格不超过 $n$ 次，时间复杂度从 $O(n^2)$ 压缩至 $O(n)$，且额外空间消耗为 $O(1)$，两项指标均达到同类问题的理论下界。

## 核心原理

### 对撞指针（左右指针）

对撞指针将左指针 `left` 初始化为 0，右指针 `right` 初始化为 `n-1`，两者向中间移动直到相遇。其正确性依赖于**单调性**：当 `arr[left] + arr[right] > target` 时，右移左指针只会让和变大，因此必须左移右指针；反之右移左指针。每次操作必然使搜索空间缩小至少 1，故循环至多执行 $n$ 次。

形式化描述如下：设有序数组 $A[0..n-1]$，目标值为 $T$。对撞指针在任意时刻维护不变式：若满足条件的下标对 $(i, j)$ 存在，则必有 $\text{left} \leq i < j \leq \text{right}$。每次移动均保持此不变式成立，当 `left == right` 时搜索结束。

典型场景：**两数之和（有序数组，LeetCode 167）**。给定升序数组 `nums` 和目标值 `target`，对撞指针的判断逻辑为：
- `nums[left] + nums[right] == target`：返回 `[left+1, right+1]`（题目下标从1开始）
- `nums[left] + nums[right] < target`：`left++`，因为 `nums[left]` 与任何 `right` 以右的元素配对和只会更大，但当前 right 已是最右，故需增大左端
- `nums[left] + nums[right] > target`：`right--`

时间复杂度 $O(n)$，空间复杂度 $O(1)$，相比哈希表解法节省了 $O(n)$ 的额外空间。

例如，给定 `nums = [2, 7, 11, 15]`，`target = 9`：初始 `left=0, right=3`，`nums[0]+nums[3]=17>9`，故 `right--`；此时 `left=0, right=2`，`nums[0]+nums[2]=13>9`，故 `right--`；此时 `left=0, right=1`，`nums[0]+nums[1]=9==9`，返回 `[1,2]`。整个过程仅 3 步，而暴力枚举需要枚举 $\binom{4}{2}=6$ 对。

### 快慢指针（同向指针）

快慢指针中，快指针 `fast` 每步前进更快或负责"探路"，慢指针 `slow` 负责"记录"合法位置。两者始终同向移动，不会出现交叉。

**原地去重**是最典型的快慢指针应用：`slow` 指向已处理区间的末尾，`fast` 扫描新元素，当 `nums[fast] != nums[slow]` 时执行 `nums[++slow] = nums[fast]`。对于长度为 $n$ 的数组，`fast` 遍历一次即完成，时间复杂度严格为 $O(n)$，`slow` 最终指向去重后数组的最后一个有效元素的下标。

**链表找环**（Floyd 判圈算法）也属于快慢指针：令 `fast` 每次走 2 步，`slow` 每次走 1 步。若链表有环，`fast` 和 `slow` 必然在环内相遇。设链表头到环入口的距离为 $a$，环的长度为 $c$，相遇时 `slow` 走了 $s$ 步，则 `fast` 走了 $2s$ 步，差值 $s$ 必为 $c$ 的整数倍，由此可得 $a \equiv -b \pmod{c}$（其中 $b$ 为环入口到相遇点的距离），利用此等式可以精确计算环的入口节点位置：相遇后令一个指针回到头节点，两者以相同速度前进，再次相遇时即为环入口（LeetCode 142）。

**找链表倒数第 $k$ 个节点**是另一种快慢指针变体：先让 `fast` 领先 `slow` 恰好 $k$ 步，然后两者以相同速度（均为1步/次）前进，当 `fast` 到达链表末尾时，`slow` 恰好指向倒数第 $k$ 个节点。GitHub 上的 neetcode 系列和《剑指 Offer》第22题均以此为例，是链表类面试题的必考模式。

### 关键复杂度公式

设数组长度为 $n$，对撞指针的时间复杂度可以严格表达为：

$$T(n) = O(n), \quad S(n) = O(1)$$

对于三数之和（LeetCode 15），外层循环固定一个元素需要 $O(n)$，内层对撞指针为 $O(n)$，总体：

$$T(n) = O(n^2), \quad S(n) = O(1) \text{（不计输出空间）}$$

相比暴力枚举的 $O(n^3)$，节省了整整一个数量级。当 $n = 1000$ 时，暴力枚举约需 $10^9$ 次操作，双指针方案仅需 $10^6$ 次，在现代 CPU 上的运行时间差距约为 1 秒对比 1 毫秒。Floyd 判圈算法的时间复杂度为 $O(n)$，其中 $n$ 为链表节点总数，空间复杂度为 $O(1)$，而基于哈希集合的判环方法需要 $O(n)$ 的额外空间。

### 指针移动的合法性证明

双指针正确性的核心在于每次指针移动都是"无损"的——被跳过的候选组合可以被证明不满足条件。以三数之和（LeetCode 15）为例：外层固定一个数 `nums[i]`，内层用对撞指针在 `[i+1, n-1]` 区间寻找剩余两数。当遇到重复元素时需要跳过，因此循环中包含 `while (left < right && nums[left] == nums[left+1]) left++` 的去重逻辑，这一步骤不会导致遗漏，因为相同值的左指针产生的所有组合已经在第一次匹配时被记录。

对于去重跳跃操作的严格无损性：设当前已记录了三元组 $(A[i], A[l], A[r])$，若 $A[l] = A[l+1]$，则三元组 $(A[i], A[l+1], A[r])$ 与之完全相同，跳过不会产生遗漏；同理对右指针的重复跳跃亦然。此论证将"去重的正确性"从直觉转化为可验证的循环不变式，是算法竞赛标准证明框架中的典型范式（Skiena, 2008）。

## 关键公式与模型

对撞指针的搜索空间缩减模型：设每次迭代后搜索区间从 $[l, r]$ 变为 $[l+1, r]$ 或 $[l, r-1]$，区间长度严格减少 1，故最多经过 $n-1$ 次迭代必然终止。这一性质可以形式化为：

$$\sum_{k=0}^{n-1} 1 = n$$

即指针移动次数上界恰好为 $n$，是双指针 $O(n)$ 复杂度的严格证明基础。

快慢指针的追及模型：设 `fast` 速度为 $v_f$，`slow` 速度为 $v_s$，且 $v_f > v_s$。进入环后，`fast` 相对 `slow` 的追及速度为 $v_f - v_s$，环长为 $c$，则最多经过：

$$t_{\max} = \left\lceil \frac{c}{v_f - v_s} \right\rceil$$

步后两者必然相遇。当 $v_f = 2, v_s = 1$ 时，$t_{\max} = c$，即最多绕环一圈即相遇。

容器盛水问题的容积公式：

$$\text{Volume}(l, r) = \min\!\left(\text{height}[l],\ \text{height}[r]\right) \times (r - l)$$

其中 $l$ 为左指针下标，$r$ 为右指针下标，每次移动较矮一侧指针，全程最多执行 $n-1$ 次指针移动，总时间复杂度 $O(n)$。

三数之和的总组合数上界（暴力方案参照基准）：

$$C_{\text{brute}} = \binom{n}{3} = \frac{n(n-1)(n-2)}{6} = O(n^3)$$

双指针方案将其压缩为 $O(n^2)$，在 $n = 3000$（LeetCode 数据规模）时，暴力方案约 $4.5 \times 10^9$ 次操作，双指针约 $9 \times 10^6$ 次，差距约 500 倍。

## 实际应用

**例如，容器盛水问题（LeetCode 11）**：给定 $n$ 个高度值组成的数组 `height`，需要找出两根柱子使其围成的容积最大。对撞指针从两端向内收缩，每次移动**较矮**一侧的指针。理由是当前容积受限于较矮一侧，若移动较高一侧，宽度 $(r - l)$ 必然减少，而高度上限 $\min(\text{height}[l], \text{height}[r])$ 不可能超过已被移走的那根柱子，故新容积必然不优于当前值。此贪心论证保证对撞指针在 $O(n)$ 内得出全局最优解，而暴力枚举需要 $O(n^2)$。

例如，给定 `height = [1, 8, 6, 2, 5, 4, 8, 3, 7]`（$n=9$），暴力枚举需要