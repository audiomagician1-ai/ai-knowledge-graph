# SSL/TLS与HTTPS

## 概述

SSL（Secure Sockets Layer，安全套接字层）由网景公司（Netscape）的工程师于1994年首次发布SSL 1.0（未公开发布）、1995年发布SSL 2.0，用于解决HTTP明文传输导致的数据窃听和篡改问题。SSL 3.0（1996年）之后，IETF在1999年将其标准化并更名为TLS（Transport Layer Security，传输层安全协议），发布了TLS 1.0（RFC 2246）。目前广泛使用的版本是TLS 1.2（2008年，RFC 5246，作者Dierks & Rescorla）和TLS 1.3（2018年，RFC 8446，作者Rescorla），而SSL 2.0、SSL 3.0及TLS 1.0/1.1已因安全漏洞（如POODLE、BEAST攻击）被正式弃用。根据Rescorla（2018）的标准文档，TLS 1.3相比前代版本删除了超过20种被认为不安全的密码套件，将握手往返时间从2-RTT缩减至1-RTT，是迄今为止最精简且安全的主流TLS版本。

HTTPS（HyperText Transfer Protocol Secure）本质上是HTTP运行在TLS层之上的协议组合，默认使用443端口，而HTTP使用80端口。当浏览器地址栏显示锁形图标时，意味着当前连接经过TLS加密保护。对于AI工程中的模型API调用、数据传输管道和微服务通信，HTTPS是防止模型推理请求被中间人拦截或篡改的基础安全机制。

HTTPS的意义在于同时提供三种安全保证：**机密性**（加密传输内容）、**完整性**（防止内容被篡改）、**身份验证**（通过数字证书确认服务器身份）。缺少任何一项，系统都存在可利用的安全漏洞。在2023年的安全统计中，超过95%的Chrome浏览器流量已通过HTTPS加密，但仍有大量内部微服务和MLOps管道未正确配置TLS，留下潜在攻击面。

> **思考问题**：如果一个AI推理API的训练数据管道使用了自签名证书并关闭了证书验证（`verify=False`），在什么攻击场景下这会导致训练数据被悄无声息地替换，从而引发模型投毒（Model Poisoning）？关闭证书验证与不使用TLS在安全性上有何本质区别？

---

## 核心原理：TLS握手过程（Handshake）

TLS建立安全连接的核心是握手协议。握手的目标是：在不安全信道上协商出一个只有通信双方知道的对称会话密钥，同时完成服务器（以及可选的客户端）身份验证。

### TLS 1.3握手流程（1-RTT）

以TLS 1.3为例，握手仅需**1个往返时间（1-RTT）**，相比TLS 1.2的2-RTT效率更高。握手步骤如下：

1. **ClientHello**：客户端发送支持的TLS版本、加密套件列表（如`TLS_AES_256_GCM_SHA384`、`TLS_CHACHA20_POLY1305_SHA256`）和随机数 $R_c$，以及客户端的ECDHE公钥份额（Key Share）。
2. **ServerHello + 证书**：服务器选定加密套件，返回数字证书（含公钥）和自己的随机数 $R_s$，以及服务器的ECDHE公钥份额。
3. **密钥交换**：双方通过ECDHE（椭圆曲线Diffie-Hellman临时密钥交换）算法协商出**会话密钥（Session Key）**，整个交换过程中私钥不在网络上传输。TLS 1.3中ECDHE密钥份额在ClientHello中一同发送，服务器收到后即可立即完成密钥协商，因此握手仅需1-RTT。
4. **Finished**：双方用会话密钥验证握手完整性，随后正式通信使用对称加密（如AES-256-GCM）。

### TLS 1.2与TLS 1.3握手对比

| 特性 | TLS 1.2 | TLS 1.3 |
|------|---------|---------|
| 握手往返次数 | 2-RTT | 1-RTT（支持0-RTT会话恢复） |
| 密钥交换算法 | RSA、DHE、ECDHE（可选） | 仅ECDHE（强制前向保密） |
| 支持的最大密码套件数 | 37种（含RC4、3DES等弱算法） | 5种（全部为AEAD） |
| 前向保密 | 可选 | 强制 |
| 最早标准化时间 | 2008年（RFC 5246） | 2018年（RFC 8446） |

### 密钥派生公式

TLS 1.3的密钥派生过程使用HKDF（基于HMAC的密钥派生函数，RFC 5869），最终会话密钥的生成公式可表示为：

$$K_{session} = \text{HKDF-Expand}\!\left(\text{HKDF-Extract}(R_c \,\|\, R_s,\; \text{DHE\_secret}),\; \text{label},\; L\right)$$

其中：
- $R_c$：客户端随机数（ClientHello中的32字节随机值）
- $R_s$：服务器随机数（ServerHello中的32字节随机值）
- $\text{DHE\_secret}$：ECDHE协商后的共享密钥（椭圆曲线上两个公钥份额的乘积在私钥方向的投影）
- $\text{label}$：上下文标签字符串，用于区分不同用途的派生密钥（如握手密钥、应用数据密钥）
- $L$：所需密钥长度（字节数，例如AES-256需要32字节）

这一设计保证了即使长期私钥泄露，过去的会话记录也无法被解密，即**前向保密（Forward Secrecy，PFS）**。

**例如**，当一个AI推理服务客户端（如Python的`httpx`库或`requests`库）向`https://api.yourmodel.com/v1/predict`发起POST请求时，底层TLS 1.3握手在建立TCP连接后仅需约一个网络往返（典型延迟10–50ms）即可完成，之后的推理数据全程以AES-256-GCM加密传输。在局域网内，这一延迟可低至1–2ms，对高频推理调用影响极小。

---

## 数字证书与PKI体系

TLS的身份验证依赖**X.509数字证书**，证书中包含域名（Subject Alternative Name，SAN字段）、公钥、有效期、颁发机构（CA，Certificate Authority）签名等字段。证书信任链由根CA → 中间CA → 服务器证书三级构成，浏览器和操作系统内置了约150个受信任的根CA公钥（截至2024年，Chrome根存储包含约140个根CA，Mozilla NSS存储包含约130个）。

### 证书验证级别

证书按验证级别分为三类：

- **DV（域名验证，Domain Validation）**：仅验证域名所有权（通过HTTP文件验证或DNS TXT记录验证），Let's Encrypt免费提供，签发时间约数分钟到数小时。全球超过3亿个活跃证书由Let's Encrypt签发（2023年数据），是MLOps平台和AI API服务最常见的证书类型。
- **OV（组织验证，Organization Validation）**：额外验证企业工商注册信息，适合企业级API服务，签发周期通常为1–3个工作日，年费约50–300美元。
- **EV（扩展验证，Extended Validation）**：最严格的验证，需人工审核企业法律实体（含营业执照核验），适合金融支付和高安全性场景，签发周期可达1–2周，年费约200–1000美元。EV证书在早期浏览器中会以绿色地址栏显示企业名称，但自2019年Chrome 77起已取消该视觉区别。

### 证书有效期与自动续期

自2020年9月起，公开受信CA签发的TLS证书最长有效期被限制为398天（约13个月），此前最长可达825天。Let's Encrypt证书有效期仅**90天**，需通过`certbot renew`的cron任务配置自动续期。Apple更于2023年提议将最大有效期缩短至45天，预计未来几年内将成为行业标准，届时自动化证书管理（ACME协议，RFC 8555）将成为生产环境的必备配置。

证书验证失败（如域名不匹配、证书过期、信任链断裂）将导致握手立即终止，客户端收到致命警报（fatal alert，错误码`certificate_expired`或`unknown_ca`），连接无法建立（Dierks & Rescorla, 2008）。

---

## 关键公式与加密模型

### 混合加密分工

TLS并非全程使用非对称加密（如RSA-2048或ECDSA P-256），因为非对称加密计算开销约是对称加密的**100–1000倍**。在2048位RSA下，典型服务器每秒可完成约1000次RSA签名操作，而AES-256-GCM在现代CPU上每秒可处理数十GB数据。TLS的设计是：用非对称加密在握手阶段安全地交换密钥，之后使用对称加密（AES-GCM）加密实际数据流，实现安全性与性能的最优平衡。

### AEAD加密模型

AEAD（Authenticated Encryption with Associated Data）模式（如AES-256-GCM）在加密同时生成认证标签（Authentication Tag，128位），一次操作同时保证机密性和完整性：

$$C,\; Tag = \text{AES-256-GCM}(K_{session},\; Nonce,\; P,\; AAD)$$

其中：
- $P$：明文数据（如模型推理请求的JSON体）
- $C$：密文（与明文等长，不泄露数据长度以外的任何信息）
- $AAD$：附加认证数据（Additional Authenticated Data），如TLS记录头，不加密但受完整性保护
- $Nonce$：每次加密唯一的随机数（96位，TLS 1.3中通过序列号与初始向量XOR生成，防止重放攻击）
- $Tag$：128位认证标签，接收方验证此标签以确认数据未被篡改

TLS 1.3强制使用AEAD算法，废弃了RC4、3DES、CBC模式（易受BEAST和Lucky13攻击）等脆弱算法。接收方验证Tag失败时，立即丢弃整条记录并终止连接，防止填充提示攻击（Padding Oracle Attack）。

**例如**，在GPU集群中传输100GB的模型训练数据时，现代服务器CPU（如Intel Xeon Sapphire Rapids）通过AES-NI硬件加速指令和AVX-512向量化，AES-256-GCM的加密吞吐量可超过**40 GB/s**（单核），远超任何网络带宽上限，几乎不产生可感知的性能损失。

### 前向保密的数学基础

ECDHE基于椭圆曲线离散对数问题（ECDLP）的困难性。设椭圆曲线群的生成元为 $G$，曲线为P-256（NIST P-256，即secp256r1），客户端私钥为随机数 $a$，公钥为 $A = aG$；服务器私钥为 $b$，公钥为 $B = bG$。双方共享密钥为：

$$S = aB = a(bG) = b(aG) = bA$$

攻击者即使截获 $A$ 和 $B$，在椭圆曲线离散对数困难假设下，无法在多项式时间内求解 $a$ 或 $b$，因而无法还原 $S$。由于 $a$ 和 $b$ 在每次握手后即销毁（"临时"密钥），历史会话密钥无法被事后破解。

---

## 证书吊销机制

当证书私钥泄露时，需要立即吊销证书。TLS有两种吊销检查机制：

- **CRL（Certificate Revocation List，证书吊销列表）**：CA定期发布吊销列表（通常每24小时更新），客户端下载后本地校验，但列表可能较大（某些CA的CRL文件超过1MB）且存在时效性延迟（最长24小时）。
- **OCSP（Online Certificate Status Protocol，在线证书状态协议）**：实时查询CA的OCSP Responder服务器，响应时间通常在100–500ms，但会引入额外的网络请求延迟，并向CA暴露用户正在访问的站点信