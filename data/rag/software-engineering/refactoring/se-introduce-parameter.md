---
id: "se-introduce-parameter"
concept: "引入参数对象"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: false
tags: ["参数"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.481
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 引入参数对象

## 概述

引入参数对象（Introduce Parameter Object）是一种重构手法，专门用于处理函数签名中出现多个相关参数反复同时传递的情况。其核心操作是：将这些在多处代码中成群出现的参数，提取为一个新的数据类或结构体，用单一对象替代原本的参数列表。这一手法由 Martin Fowler 在1999年出版的《重构：改善既有代码的设计》（第一版）中正式命名和系统化描述，属于"简化函数调用"类别下的经典重构之一。

当一个函数需要传入如 `startDate`、`endDate`、`minAmount`、`maxAmount` 这样两两相关的参数时，这些参数实际上共同描述了一个"日期范围"或"金额范围"的概念，却被人为地拆散在参数列表中。引入参数对象的价值在于：它不仅仅是语法上的合并，更是对隐藏领域概念的显式化——将散落的数据聚合成一个有名字的概念实体，使代码更贴近业务语言。

## 核心原理

### 识别参数群（Parameter Cluster）

引入参数对象的前提是发现"参数群"，即在多个函数的参数列表中反复出现的同一组参数。Martin Fowler 将这种现象称为**数据泥团（Data Clumps）**代码坏味道。判断标准是：如果删掉这组参数中的某一个，其余的参数就失去了意义，那么这组参数就构成一个天然的聚合单元，适合提取为参数对象。例如，函数 `calculateDiscount(price, customerSince, customerLevel)` 中，`customerSince` 和 `customerLevel` 共同描述客户信息，可以聚合为 `CustomerInfo` 对象。

### 参数对象的结构设计

新创建的参数对象通常设计为**值对象（Value Object）**，即不可变（immutable）的数据持有者。以 Java 为例，一个日期范围对象可定义为：

```java
public class DateRange {
    private final LocalDate startDate;
    private final LocalDate endDate;

    public DateRange(LocalDate startDate, LocalDate endDate) {
        if (endDate.isBefore(startDate)) {
            throw new IllegalArgumentException("结束日期不能早于开始日期");
        }
        this.startDate = startDate;
        this.endDate = endDate;
    }

    public boolean includes(LocalDate date) {
        return !date.isBefore(startDate) && !date.isAfter(endDate);
    }
}
```

注意此处在构造函数中加入了约束校验（`endDate` 不能早于 `startDate`），这是参数对象带来的额外收益——原本分散在各调用处的隐式约束，现在集中在对象内部统一管理。

### 重构的完整步骤

Martin Fowler 描述的标准操作步骤为：①创建新的参数对象类；②在原函数上新增一个接受该对象的重载版本，旧参数列表版本暂时保留；③逐一修改每个调用方，将传参方式切换为新对象；④确认所有调用方迁移完毕后，删除旧的参数列表版本；⑤在新类上寻找可迁移的行为逻辑（如范围判断、格式化等），将其从调用方挪入参数对象内部。步骤⑤是这一重构手法真正展现威力的阶段——参数对象开始"生长"为一个完整的领域概念类。

## 实际应用

**电商订单筛选场景**：假设系统中多个查询函数都接受 `(Date fromDate, Date toDate, String status, String region)` 这四个参数，可以将 `fromDate`/`toDate` 提取为 `OrderDateRange`，将 `status`/`region` 提取为 `OrderFilter`，最终函数签名从四个参数缩减为一个 `OrderFilter` 对象（内含 `OrderDateRange`）。原本在 `OrderService`、`ReportService`、`ExportService` 三处各自复制的"开始日期必须早于结束日期"校验，统一收归到 `OrderDateRange` 构造器中。

**地理坐标传递场景**：地图类应用中频繁出现 `(double latitude, double longitude)` 的参数对，将其提取为 `GeoPoint` 类后，不仅简化了 `findNearby(GeoPoint center, double radiusKm)` 等函数的签名，还可以在 `GeoPoint` 内部实现 `distanceTo(GeoPoint other)` 方法，利用 Haversine 公式计算球面距离，彻底消除散落在各处的重复计算代码。

## 常见误区

**误区一：把任意多参数函数都用参数对象包装**。引入参数对象的适用条件是参数之间存在内在的语义关联，并在多个地方成群出现。若一个函数的三个参数各自独立、彼此无关，强行打包进一个对象只会制造一个无意义的"参数袋（Parameter Bag）"，使代码更难理解，这与 Fowler 本意相违背。

**误区二：创建了参数对象但不迁移行为**。许多开发者将引入参数对象仅视为"把几个参数换成一个对象"的语法替换，完成替换后便停手。这样的参数对象只是一个哑数据结构，没有发挥出聚合领域逻辑的潜力。真正完整的重构应该审视调用方中所有针对这组数据的操作（格式化、比较、校验），将其逐步迁移到参数对象内部。

**误区三：在参数对象中使用可变状态**。将参数对象设计为可变对象（提供 setter 方法）会导致函数的实际入参可能在执行过程中被外部修改，产生难以追踪的副作用。参数对象应当遵循值对象语义，一旦构造即不可变，并通过重写 `equals` 和 `hashCode`（在 Java 中）保证基于值的相等性比较。

## 知识关联

引入参数对象与"提取类（Extract Class）"重构手法高度相关：当参数对象在重构过程中被赋予越来越多的行为时，它实际上已经演变为通过"提取类"得到的完整领域类，两个手法之间存在自然的演进路径。它直接治理的代码坏味道是**数据泥团（Data Clumps）**，同时也缓解了**过长参数列表（Long Parameter List）**这一坏味道——后者的另一种治理方式是"以查询替换参数（Replace Parameter with Query）"，两者可配合使用。在领域驱动设计（DDD）的语境下，通过引入参数对象显式化的概念往往对应值对象（Value Object）模式，是从重构走向 DDD 建模的常见入口之一。