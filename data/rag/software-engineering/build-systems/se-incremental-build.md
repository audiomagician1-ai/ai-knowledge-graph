# 增量构建

## 概述

增量构建（Incremental Build）是构建系统中的核心优化机制：**仅重新编译、链接、打包自上次构建以来其输入集合发生变化的构建单元，跳过输入不变的单元**。其本质是将构建过程建模为一个带缓存的函数求值问题——若函数的所有输入未变，则直接复用上次的输出，无需重新计算。这一思想与纯函数（Pure Function）的语义完全吻合：相同输入必然产生相同输出，因此"重新计算"是冗余的。

增量构建思想的最早工程实现来自1977年 Stuart Feldman 为贝尔实验室 Unix 系统开发的 `make` 工具（Feldman, 1979）。Feldman 在论文《Make — A Program for Maintaining Computer Programs》中描述了基于文件修改时间戳的依赖检测算法，这一范式此后被 Ant、Maven、Gradle、Bazel、Buck2、Webpack、Vite、Turborepo 等工具沿用和扩展长达四十余年。

在实际工程规模下，增量构建的收益极为显著。以 Google 的 Bazel 为例，其内部数据显示在包含数百万行代码的单仓库（Monorepo）中，增量构建的平均构建时间比全量构建缩短 90%～98%。Facebook 的 Buck2 构建系统同样报告，在典型的日常开发场景中，95% 以上的构建节点可从缓存中直接命中，未命中节点才需执行实际编译动作。对前端开发而言，一个包含 500 个模块的 Webpack 5 项目，开启持久化缓存（Persistent Cache）后二次构建时间可从 40 秒压缩至 2 秒以内，提速比高达 20 倍。

增量构建的三大技术支柱——**文件时间戳检测、内容哈希比对、依赖图追踪**——并非彼此替代，而是在不同场景和精度需求下分层叠加使用，理解其差异是正确配置任何现代构建系统的前提。

---

## 核心原理

### 文件时间戳检测

时间戳检测是增量构建的历史起点，其判断规则可形式化为：

$$\text{stale}(T) = \exists P_i \in \text{deps}(T): \text{mtime}(P_i) > \text{mtime}(T)$$

即：若目标文件 $T$ 的任意依赖 $P_i$ 的修改时间戳（modification time，mtime）**晚于** $T$ 本身的修改时间戳，则 $T$ 被判定为"过期（stale）"，必须重新构建。系统通过 POSIX `stat()` 系统调用获取 mtime，单次调用开销通常在微秒量级，因此对于数千个文件的项目，扫描全部时间戳的总耗时通常不超过数十毫秒。

时间戳方法存在三个系统性弱点：

1. **误触发（False Positive）**：执行 `touch file.c` 后文件内容未变但 mtime 更新，触发不必要的重建；
2. **时钟偏差（Clock Skew）**：在 NFS 或跨时区分布式 CI 环境中，不同节点的系统时钟不一致，导致 mtime 比较结果不可信。Linux 内核文档（kernel.org）记录了 NFS v3 的时间戳精度仅为秒级，这在高频构建场景下会导致大量误判；
3. **版本切换陷阱**：`git checkout` 切换分支时，Git 会更新所有被修改文件的 mtime，即使切回原分支后内容与之前完全相同，`make` 也会将所有涉及文件标记为 stale，引发完整的无效重建。

### 内容哈希比对

现代构建系统以**文件内容的密码学哈希或高速非加密哈希**替代时间戳，彻底解决误判问题。失效判断公式变为：

$$\text{stale}(T) = \exists P_i \in \text{deps}(T): H(P_i^{\text{current}}) \neq H(P_i^{\text{cached}})$$

其中 $H$ 为选定的哈希函数。常用算法的性能对比如下：MD5（128位输出，速度约 600 MB/s，已不推荐用于安全场景）、SHA-1（160位输出，速度约 350 MB/s，Gradle 早期采用）、xxHash3（非加密，128位输出，速度可达 50 GB/s，由 Yann Collet 于2019年发布，被 Bazel 和 Buck2 采用）。对于超大文件，部分工具还采用**分块哈希（Chunked Hashing）**，仅对发生变化的数据块重新计算，进一步降低 I/O 开销。

Gradle 7.x 及以上版本在其官方文档（Gradle Inc., 2021）中明确说明，构建缓存键（Build Cache Key）由任务输入的归一化哈希（Normalized Hash）构成，包括：源文件内容哈希、编译器版本字符串哈希、JVM 参数哈希的组合摘要。只要任意一项改变，缓存键失效，任务重新执行。这使得 Gradle 在同一机器和不同 CI 节点之间均可共享远程构建缓存（Remote Build Cache），实现真正的跨机器增量。

Webpack 5 在2020年10月发布时引入的持久化缓存（Persistent Cache）正是基于内容哈希机制——构建系统将每个模块的内容哈希、loader 配置哈希、依赖模块哈希的组合值写入 `node_modules/.cache/webpack/` 下的快照数据库（基于 LevelDB 格式），下次构建时若所有组合哈希不变，直接反序列化缓存产物，跳过整个 loader 链的执行。

### 依赖图的构建与传播

仅检测直接输入文件是不够的——增量构建系统需要维护一张完整的**有向无环图（DAG）**，其中节点为构建单元（文件、模块、任务），有向边 $u \to v$ 表示"$v$ 依赖于 $u$"。

当节点 $u$ 被标记为失效时，系统需沿反向边执行**失效传播（Invalidation Propagation）**：

$$\text{Invalidate}(u) = \{u\} \cup \bigcup_{v:\, u \in \text{deps}(v)} \text{Invalidate}(v)$$

这是一个在依赖图上的递归标记过程，其时间复杂度为 $O(V + E)$，其中 $V$ 为节点数，$E$ 为依赖边数。在 Webpack 的实现中，`ModuleGraph` 类在内存中维护此 DAG，`HarmonyImportDependency` 负责记录 ES Module 的静态导入边；当 `--watch` 模式检测到文件系统变更时，`Compilation` 对象沿依赖反向边执行失效标记，仅将受影响模块加入重建队列（Rebuild Queue）。

依赖图的**精度（Precision）**直接决定增量构建的效率。粗粒度依赖（如"只要某目录下任意文件变化，就重建整个模块"）导致过度重建；细粒度依赖（如"仅追踪具体导入的符号级别"）能最小化重建集合，但需要更复杂的静态分析。Bazel 的 Starlark 规则要求开发者在 `BUILD` 文件中**显式声明依赖**，而非动态发现，正是为了保证依赖图的确定性，避免隐式依赖导致的缓存失效或缓存错误命中。

### 最小化重建集合的拓扑排序

确定失效节点集合后，构建系统需按依赖顺序重建它们。标准做法是对失效子图执行 **Kahn 算法**（Kahn, 1962）的拓扑排序：

$$\text{令 } L = [\ ],\ S = \{n \mid \text{in-degree}(n) = 0\}$$
$$\text{while } S \neq \emptyset:\ \text{取出 } n \in S,\ L.\text{append}(n),\ \text{更新邻居的入度}$$

最终序列 $L$ 即为合法的重建顺序。现代构建系统（如 Bazel、Ninja）在此基础上进一步引入**并行执行**：拓扑排序后入度为零的节点可同时调度到不同 CPU 核心，最大化吞吐量。Ninja（Evan Martin, 2012）正是因为将这一机制做到极致——专注于执行层、不负责依赖发现、依赖由 CMake/GN 等上游工具生成——才在 Chromium 这样拥有数万个编译单元的项目中实现了毫秒级的增量重建决策。

---

## 关键方法与公式

### 缓存键设计

构建缓存（Build Cache）的命中率取决于**缓存键（Cache Key）**的设计质量。一个完备的缓存键应包含所有影响输出的输入因素：

$$\text{CacheKey}(T) = H\bigl(\text{SourceHash}(T) \| \text{ToolchainHash} \| \text{FlagsHash} \| \text{EnvHash}\bigr)$$

其中 `‖` 表示拼接，`ToolchainHash` 包含编译器版本（如 `gcc 13.2.0`）、链接器版本；`FlagsHash` 包含编译参数（如 `-O2 -DDEBUG`）；`EnvHash` 包含影响构建行为的环境变量（如 `JAVA_HOME`）。

**缓存键设计错误**是实际工程中最常见的增量构建故障来源：遗漏某个输入因素会导致**缓存污染（Cache Poisoning）**——即用错误的缓存产物替代正确的构建结果，产生难以复现的 Bug。Bazel 通过沙箱执行（Sandboxed Execution）强制隔离构建动作，确保动作只能访问显式声明的输入，从根本上杜绝缓存键遗漏问题（Xu et al., 2020）。

### 增量编译中的符号级失效

对于编译型语言，源文件级别的失效粒度仍然偏粗。例如，修改一个 C++ 头文件 `utils.h` 中某个函数的**实现**（非声明），理论上所有包含该头文件的 `.cpp` 都需要重新编译，但若函数签名未变，依赖该头文件的其他头文件所包含的 `.cpp` 则无需重编。

Java 生态中，Gradle 的**增量编译（Incremental Compilation）**借助 `compileJava` 任务的 `--incremental` 参数实现了类级别的失效分析：Gradle 在 `build/tmp/compileJava/previous-compilation-data.bin` 中记录每个 `.class` 文件的 ABI（Application Binary Interface）哈希，若某个类的 ABI（即公开方法签名、字段类型）未发生变化，仅内部实现改变，则其下游依赖类无需重新编译，大幅减少重建范围。

---

## 实际应用

### Makefile 的增量构建实践

经典 `Makefile` 规则：

```makefile
main.o: main.c utils.h
    gcc -c main.c -o main.o
```

此规则声明 `main.o` 依赖 `main.c` 和 `utils.h`。`make` 在每次调用时比较三者的 mtime：若 `main.c` 或 `utils.h` 的 mtime 晚于 `main.o`，则执行 `gcc` 命令；否则打印 `main.o is up to date` 并跳过。对于包含数百个 `.o` 文件的项目，典型的增量构建仅需重编1～3个文件，耗时从分钟级降至秒级。

**例如**：Linux 内核源码树（约3000万行C代码）在开启 `ccache`（编译器缓存工具，通过哈希比对实现）的情况下，对单个驱动文件的修改触发的增量构建通常仅需 5～15 秒，而全量构建需要 30～90 分钟（取决于硬件配置），增量比约为200:1。

### Webpack 5 持久化缓存配置

在 `webpack.config.js` 中启用持久化缓存：

```javascript
module.exports = {
  cache: {
    type: 'filesystem',           // 使用文件系统缓存（而非默认内存缓存）
    buildDependencies: {
      config: [__filename],       // 将 webpack 配置文件纳入缓存键
    },
    version: '1.0',               // 手动版本号，用于强制失效
  },
};
```

`buildDepend