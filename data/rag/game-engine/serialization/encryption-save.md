---
id: "encryption-save"
concept: "存档加密"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 3
is_milestone: false
tags: ["安全"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 存档加密

## 概述

存档加密（Save File Encryption）是游戏引擎序列化系统中用于保护玩家存档数据免遭篡改、作弊和非法修改的一套技术手段。其核心目标是确保存档文件的完整性（Integrity）和机密性（Confidentiality），使得即便玩家拥有本地文件的读写权限，也无法轻易修改金币数量、角色属性或游戏进度等关键数据。

存档加密作为反作弊体系的本地端防线，最早在单机游戏领域受到重视。2005年前后，随着《魔兽世界》等网络游戏的普及，外挂与存档修改工具（如Cheat Engine）横行，越来越多的单机游戏开发者也开始在离线存档中引入加密与校验机制。Unity引擎在2018年的Addressables系统更新后，将存档保护纳入了推荐的最佳实践文档，进一步推动了该技术在独立游戏开发中的普及。

对于竞技类、肉鸽（Roguelite）以及带有排行榜系统的游戏而言，存档加密直接影响公平性体验。若玩家可用十六进制编辑器直接修改`.sav`文件中的整数值，则所有基于本地存档的成就、排行榜数据都将失去公信力。因此，存档加密不仅是技术问题，也是游戏设计完整性的保障。

---

## 核心原理

### 哈希校验（Integrity Check）

最轻量级的存档保护方式是在存档文件末尾附加一段哈希摘要。常用算法为SHA-256，其输出固定为256位（32字节）的摘要值。游戏启动加载存档时，对文件内容重新计算哈希值，若与存储的摘要不匹配，则判定存档被篡改。

公式如下：

```
digest = SHA256(file_content + secret_key)
```

其中`secret_key`是编译进游戏可执行文件中的固定字符串（通常称为"盐值"，Salt）。单纯使用`SHA256(file_content)`而不加盐的做法存在严重缺陷——攻击者在修改内容后可重新计算并替换摘要，加盐后则必须知道密钥才能伪造合法摘要。这种方案被称为HMAC（Hash-based Message Authentication Code），是目前单机游戏存档校验的主流方案。

### 对称加密（Symmetric Encryption）

对存档进行加密（而非仅校验）需要使用加密算法将明文序列化数据转换为密文。AES（Advanced Encryption Standard）是最常用的选择，通常采用AES-128或AES-256配合CBC（Cipher Block Chaining）或GCM（Galois/Counter Mode）模式。

GCM模式的优势在于同时提供加密和认证，即一次操作完成机密性与完整性保护，适合存档这类读写频率较低但安全要求较高的场景。加密时需要一个随机生成的初始向量（IV，Initialization Vector），每次保存存档时IV应重新生成并与密文一同存储：

```
(ciphertext, auth_tag) = AES_GCM_Encrypt(key, iv, plaintext)
stored = iv + auth_tag + ciphertext
```

密钥（key）的管理是此方案的核心难题，详见"常见误区"部分。

### 混淆与反逆向策略

纯粹的加密仍存在密钥提取风险。进阶方案包括：将密钥分散存储在可执行文件的多个位置（Key Splitting）、使用硬件指纹（如CPU序列号或主板UUID）动态派生密钥，以及将存档格式设计为二进制混淆格式而非直接序列化的JSON/XML。Unity的PlayerPrefs默认以明文键值对存储，正是因此被视为不安全的存档方式；改用自定义二进制格式配合AES-GCM是常见的替代方案。

---

## 实际应用

**Unity + AES-GCM实现示例**：开发者通常使用.NET内置的`System.Security.Cryptography.AesGcm`类（.NET 5+）对`BinaryFormatter`或`JsonUtility`序列化后的字节数组进行加密，再写入持久化路径`Application.persistentDataPath`下的`.dat`文件。密钥可通过`PBKDF2`算法从玩家账号ID和固定盐值派生，使不同玩家的存档加密密钥各不相同，防止"通用破解工具"的出现。

**排行榜防作弊场景**：《Hades》（地狱之门）等肉鸽游戏本地存储最高连杀数等统计数据，若不加密，玩家可轻松用HxD等十六进制编辑器定位并修改对应的4字节整数值。引入HMAC-SHA256后，任何字节级修改都会导致加载时校验失败，游戏将回滚至上一次合法存档或重置该数据。

**云存档与本地加密的协同**：Steam云存档（Steam Cloud）本身不对文件内容加密，仅提供传输层TLS保护。因此即便使用云存档，本地加密仍是必要的，两者分别负责传输安全和数据安全，职责不重叠。

---

## 常见误区

**误区一：将密钥硬编码为明文字符串即可**

许多初学者直接在代码中写`string key = "MyGameSecretKey123"`，这类密钥可通过IDA Pro或dnSpy等逆向工具在5分钟内从可执行文件中提取。正确做法是将密钥拆分存储，或使用代码混淆工具（如Dotfuscator）配合字符串加密插件对密钥字符串进行保护。完全无法逆向的方案不存在，但提高破解成本本身即是目标。

**误区二：加密等同于校验，有加密就不必做哈希校验**

加密保证机密性，哈希校验保证完整性，两者解决不同问题。AES-CBC模式加密的密文在解密后，若密钥正确但中间字节被篡改，会得到乱码而非报错——游戏可能因此崩溃而非优雅地检测到作弊。AES-GCM的认证标签（auth_tag）解决了这一问题，但若使用CBC模式，则必须额外附加HMAC校验。

**误区三：存档加密对网络游戏没有意义**

即便是以服务器权威验证为主的网络游戏，客户端本地仍可能缓存离线进度、操作录像或设置文件，这些数据若未加密，可被恶意玩家修改后上传，绕过部分服务器校验逻辑。存档加密在多人游戏中作为客户端防线，与服务器验证形成纵深防御（Defense in Depth）。

---

## 知识关联

存档加密以**存档系统**（Save System）为直接前提，需要先掌握序列化格式（JSON、二进制、Protocol Buffers等）的选择与实现。理解序列化输出的字节结构是正确施加加密的基础——加密操作的输入必须是确定性的字节序列，而非含有不稳定内存地址的原始对象图。

在扩展方向上，存档加密与**反作弊系统**（Anti-Cheat，如EAC、BattlEye的本地端组件）在技术上存在交叉，后者在进程内存层面拦截Cheat Engine类工具的实时内存写入，而存档加密则在文件持久化层面提供保护，两者共同构成完整的反作弊体系。对于需要跨设备同步的游戏，存档加密还需与**云存档同步**机制协调设计，确保密钥派生策略与账号系统绑定而非与设备绑定。