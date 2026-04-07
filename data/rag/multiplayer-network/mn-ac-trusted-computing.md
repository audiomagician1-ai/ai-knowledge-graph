# 可信计算

## 概述

可信计算（Trusted Computing）是一种通过专用硬件模块建立不可篡改的信任根（Root of Trust），从而以密码学方式证明计算环境完整性的安全技术体系。在网络多人游戏反作弊领域，它从根本上解决了客户端不可信问题：游戏服务器无法仅凭软件手段验证客户端是否运行在干净、未被篡改的环境中，而可信计算硬件可以在软件层无法触及的物理层面生成加密证明。

可信计算联盟（TCG，Trusted Computing Group）于1999年由Intel、IBM、HP、Compaq、Microsoft联合成立，2003年发布TPM 1.1规范，2016年TPM 2.0成为ISO/IEC 11889国际标准。目前绝大多数出厂于2016年后的PC主板均内置了TPM 2.0芯片。Intel于2015年在第六代酷睿（Skylake）处理器中正式商用Software Guard Extensions（SGX），提供了与TPM互补但机制完全不同的可信执行环境。2021年微软宣布Windows 11将TPM 2.0列为强制硬件需求，这一政策直接将TPM渗透率推向主流PC市场的95%以上，为游戏反作弊系统大规模部署可信计算扫清了覆盖率障碍。

可信计算的核心价值在于将信任根从"软件逻辑"迁移到"物理硅片"。作弊工具即使绕过了驱动级内存扫描防护，也几乎无法伪造TPM芯片发出的硬件签名或SGX飞地（Enclave）内的计算结果，因为这需要对物理硬件进行克隆或实施微架构级别的侧信道攻击，成本远超普通作弊者的能力边界。

---

## 核心原理

### TPM远程证明（Remote Attestation via TPM）

TPM芯片内部维护着一组名为**平台配置寄存器（PCR，Platform Configuration Register）**的256位哈希寄存器，TPM 2.0规范定义了至少24个PCR槽位，各槽位有固定的语义分配：PCR 0–7记录固件（UEFI/BIOS）度量值，PCR 8–9记录Bootloader，PCR 10记录操作系统内核，PCR 12–14记录引导配置。系统从上电开始，每一层软件组件的度量哈希依次通过"扩展（Extend）"操作写入对应PCR，扩展公式为：

$$\text{PCR}[n]_{\text{new}} = \text{SHA-256}\!\left(\text{PCR}[n]_{\text{old}} \;\|\; \text{MeasuredValue}\right)$$

由于SHA-256的单向性，攻击者无法在不重置TPM的情况下将PCR伪造为任意指定目标值。游戏反作弊服务器向客户端发出随机挑战值（nonce），TPM使用内嵌的唯一Attestation Identity Key（AIK）对当前PCR快照（Quote）与nonce联合签名，服务器验证签名即可确认：① 签名来自真实TPM硬件（通过厂商签发的EK证书链验证）；② 客户端当前的引导链哈希与白名单一致，未注入恶意驱动。

Riot Games工程师在2022年公开技术分享中详述了Vanguard反作弊系统的TPM集成方向，明确指出基于PCR Quote的远程证明可有效阻止作弊者通过Type-1 Hypervisor（如自定义KVM）隐藏内核模块的存在，因为Hypervisor层本身会被PCR 0记录。

### SGX可信执行环境（Trusted Execution Environment via Intel SGX）

Intel SGX（Software Guard Extensions）通过扩展x86指令集（ENCLS/ENCLU系列指令）创建称为**飞地（Enclave）**的隔离内存区域，其核心数据结构为**ELRANGE（Enclave Linear Address Range）**和驻留在CPU片上缓存中的**EPC（Enclave Page Cache）**。飞地内的代码和数据即使对操作系统内核（Ring 0）、虚拟机监控器（VMM，Ring -1）乃至通过DMA进行的物理内存读取攻击均不可见。SGX飞地内存通过CPU内置的**MEE（Memory Encryption Engine）**以AES-128 CTR模式实时加密，加密密钥（称为MEK）仅在CPU封装内部存在，永不暴露于外部总线。

SGX提供两类证明机制：**本地证明（Local Attestation）**用于同一平台上两个飞地间的相互认证，**远程证明（Remote Attestation）**用于向外部服务器证明飞地身份。远程证明流程中，CPU通过Quoting Enclave（QE）生成包含飞地测量值（MRENCLAVE，飞地代码/数据的SHA-256哈希）和签名者身份（MRSIGNER）的Quote结构体，再由Intel Attestation Service（IAS）或Intel DCAP（Data Center Attestation Primitives）颁发可验证的证书。

在反作弊应用中，反作弊模块的核心检测逻辑（如行为特征向量计算、输入时序分析算法）封装在SGX飞地中运行。作弊工具即使拥有内核级Ring-0权限，也无法读取飞地内的检测算法代码或篡改上报数据流，因为CPU硬件本身会拒绝所有来自飞地外部的非授权内存访问（触发#PF异常）。

### 度量启动与信任链（Measured Boot & Chain of Trust）

可信计算的完整性保障依赖从硬件到应用层的**信任链传递**。以TPM 2.0 + UEFI安全启动为例，信任链如下：

1. **CRTM（Core Root of Trust for Measurement）**：主板固件中固化的最小可信代码，负责度量UEFI固件本体并写入PCR 0。
2. **UEFI固件**：度量Option ROM、Bootloader（如Windows Boot Manager）并写入PCR 2/4。
3. **Windows Boot Manager**：度量winload.exe和内核ntoskrnl.exe写入PCR 8/10。
4. **Early Launch Anti-Malware（ELAM）驱动**：反作弊驱动可以注册为ELAM驱动，在第三方内核模块加载前最先运行，其度量值写入PCR 12。

若链条中任意环节的度量哈希偏离白名单（例如注入了rootkit驱动），该变化将通过PCR扩展公式传播到最终PCR值，使远程证明失败，反作弊服务器拒绝该客户端连接。

---

## 关键方法与公式

### PCR扩展链的不可逆性证明

设攻击者希望将PCR[n]的值伪造为目标值$T$，而当前PCR值为$P_k$，则需要找到输入$M$使得：

$$\text{SHA-256}(P_k \| M) = T$$

这等价于对SHA-256构造第二原像（Second Preimage），计算复杂度为$O(2^{256})$，在当前计算能力下不可行。这也是PCR设计选择SHA-256而非CRC等非密码学哈希的原因。

### SGX飞地度量值（MRENCLAVE）计算

飞地的度量值MRENCLAVE在飞地构建（ECREATE/EADD/EEXTEND指令序列）过程中逐步计算：

$$\text{MRENCLAVE} = \text{SHA-256}\!\left(\bigoplus_{i=1}^{N} \text{EEXTEND}(page_i)\right)$$

其中每个256字节内存页块通过EEXTEND指令将其内容哈希折叠进MRENCLAVE累积状态。相同代码在不同平台上编译出相同二进制文件时，MRENCLAVE值完全一致，这保证了远程证明的确定性。

### 密封存储（Sealing）与反作弊状态持久化

TPM提供**密封（Sealing）**功能：将数据加密绑定到特定PCR状态，只有当平台处于相同PCR配置时才能解密。反作弊系统可利用此功能存储玩家设备的硬件指纹、封禁令牌等敏感数据。密封操作使用TPM内部的Storage Root Key（SRK）加密，并在加密元数据中记录授权解封的PCR值组合，若系统被篡改导致PCR变化，封禁令牌无法解封，封禁绕过成本大幅提高。

---

## 实际应用

### Riot Vanguard的硬件绑定封禁

Riot Games的Vanguard反作弊系统自2020年随《Valorant》上线以来，已演进出基于TPM的硬件封禁机制（HWID Ban）。传统HWID封禁依赖读取MAC地址、硬盘序列号等软件可见的标识符，作弊者可以通过虚拟化或修改注册表绕过。TPM方案利用EK（Endorsement Key）——一个在芯片出厂时写入、永久不可修改的RSA-2048私钥——作为硬件身份标识。EK本身不直接暴露，但服务器可通过证书链验证EK的真实性。配合TPM PCR Quote，Vanguard可以同时验证"这是真实硬件"和"硬件运行环境未被篡改"两个维度。

### 《幻兽帕鲁》服务器验证与客户端证明

部分AAA级游戏和竞技游戏在服务端加入了要求客户端提交SGX远程证明报告（Quote）的验证步骤。服务器通过Intel DCAP验证Quote中的MRENCLAVE值是否与官方发布版本一致，并检查Quote中嵌入的nonce是否与本次会话匹配（防止重放攻击）。这一流程使得即使作弊者能够修改游戏内存，只要飞地内的反作弊逻辑未被篡改，检测流程就能正常执行并上报异常。

### 案例：Valve VAC与可信计算的结合方向

Valve的VAC（Valve Anti-Cheat）系统传统上基于签名扫描和行为分析，其局限性在于检测延迟（通常在封禁波中批量处理）。在研究层面，Shieh等人（2017）在论文《Leveraging Trusted Execution Environments for Game Anti-Cheat》中提出将SGX用于隔离游戏核心逻辑渲染调用，使服务器可验证客户端渲染数据的真实性，防止通过修改渲染管线实现透视外挂。该方案的核心数据通路完全在飞地内完成，外部内存中只保存加密后的帧数据。

---

## 常见误区

### 误区一：TPM可以阻止所有作弊行为

TPM远程证明仅能验证**引导链的完整性**，即系统从上电到操作系统加载这一过程中没有注入未授权代码。它无法检测操作系统正常运行后通过用户态API（如WriteProcessMemory）进行的内存修改，也无法检测硬件外挂（如将FPGA设备接入USB读取帧缓冲）。TPM证明通过的客户端仍可能运行用户态作弊工具，因此TPM必须与运行时检测机制（如驱动级内存扫描）配合使用，而非作为单一防线。

### 误区二：SGX飞地是绝对安全的黑盒

SGX自发布以来已遭受多种有影响力的攻击，包括：**Foreshadow/L1TF攻击**（Van Bulck等，2018，USENIX Security）通过预测执行漏洞泄露SGX飞地内存；**Plundervolt攻击**（Murdock等，2020，IEEE S&P）通过CPU电压故障注入篡改飞地计算结果；**SGAxe**（2020）利用微架构侧信道恢复飞地密钥。这些攻击大多需要内核权限或物理访问，但表明SGX并非无懈可击。Intel已通过微码更新和新一代TDX（Trust Domain Extensions）架构逐步修复这些问题，但游戏反作弊工程师需要意识到SGX飞地需要持续更新，不能部署后一劳永逸。

### 误区三：所有玩家硬件都支持TPM/SGX

尽管TPM 2.0在主流PC上的覆盖率因Windows 11需求已大幅提升，但Intel SGX的情况更为复杂：Intel在2021年宣布从第12代酷睿（Alder Lake）消费级处理器中移除SGX支持，仅在数据中心级Xeon平台保留。这意味着如果游戏强依赖SGX客户端飞地，将面临大量无法运行的玩家群体。当前反作弊系统的实际做法是将SGX/TPM验证作为**增强层**而非