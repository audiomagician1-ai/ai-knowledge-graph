---
id: "mn-lb-ready-check"
concept: "准备确认"
domain: "multiplayer-network"
subdomain: "lobby-system"
subdomain_name: "大厅系统"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 准备确认（Ready Check）

## 概述

准备确认（Ready Check）是网络多人游戏大厅系统在匹配算法完成配对之后、游戏服务器正式分配房间之前的一道"在线验证"关口。其核心逻辑是：匹配服务将若干玩家分配至同一对局后，系统向每位玩家的客户端推送一个弹窗确认请求，要求他们在规定倒计时内点击"接受"（Accept）；只有当会话中全部玩家均点击接受，游戏服务器才会被实际分配并进入载入流程。

该机制最早以弹出式对话框的形式出现在《魔兽世界》（World of Warcraft，2004年）的地下城组队系统"地下城寻访者"（Dungeon Finder，2009年3.3版本正式引入自动匹配）中，随后被MOBA和FPS品类广泛借鉴。《英雄联盟》（League of Legends）将其确认窗口定为 **12秒** 倒计时，《Dota 2》定为 **30秒**，《Valorant》定为 **12秒**，《Overwatch》定为 **20秒**，这四款游戏的参数差异折射出不同品类对"玩家响应速度"与"网络容忍度"的不同取舍。

准备确认机制的存在使匹配算法可以更激进地扩大搜索范围——因为即使匹配到一名临时离开键盘（AFK）的玩家，后续还有一道"人是否在场"的过滤，从而降低了"僵尸玩家进入对局"的风险，改善整体对局质量。

---

## 核心原理

### 有限状态机模型

服务端的每一次准备确认会话（Ready Check Session）都是一个明确定义的有限状态机（Finite State Machine，FSM）。会话级别的状态集合为：

| 状态 | 含义 |
|------|------|
| `PENDING` | 等待所有玩家响应，倒计时进行中 |
| `ALL_READY` | 所有玩家已确认，触发游戏分配 |
| `DECLINED` | 至少一名玩家主动点击拒绝 |
| `TIMEOUT` | 倒计时归零时仍有玩家未响应 |

每位玩家在会话内拥有独立的个人状态：`WAITING → READY`（点击接受）或 `WAITING → REJECTED`（点击拒绝）。服务器在收到每一条状态变更事件后立即检查全局条件：若所有玩家均为 `READY`，则无需等到计时结束，立即转入 `ALL_READY`；若任意玩家为 `REJECTED` 或定时器触发，则转入终止态。

这种"早退出"（Early Exit）设计减少了对局分配的平均延迟——在《英雄联盟》的10人5v5场景中，实测平均确认时间约为 **4.2秒**，远短于12秒的上限（Riot Engineering Blog, 2016）。

### 超时时长的量化设计

超时时间 $T$ 并非拍脑袋决定，而是基于以下公式估算：

$$T = \text{RTT}_{P95} + T_{\text{UI}} + T_{\text{reaction}}$$

其中：
- $\text{RTT}_{P95}$：目标服务区域玩家群体的第95百分位网络往返延迟，北美服务器典型值约为 **80ms**，东南亚区域可达 **200ms**；
- $T_{\text{UI}}$：客户端从收到服务器推送到完成弹窗渲染的时间，现代引擎下约为 **200～400ms**；
- $T_{\text{reaction}}$：用户从看到弹窗到点击确认的人类反应时间，心理学研究中对于预期视觉刺激的平均响应时间约为 **250ms**，但游戏场景下玩家可能正在看其他窗口，工程上通常取 **8～10秒**。

代入典型值：$T \approx 0.08 + 0.3 + 9 \approx 9.4\text{秒}$，向上取整后《英雄联盟》选择 **12秒** 留有约2.6秒的安全余量。《Dota 2》的30秒更多是出于对国际玩家群体高延迟环境的兼容，而非反应时间需求。

### 拒绝与超时后的重排队策略

当确认会话以 `DECLINED` 或 `TIMEOUT` 结束时，系统需要决定哪些玩家重新进入匹配队列、是否附加惩罚。主流策略分为三类：

**① 全体重排（Full Re-queue）**：所有玩家的等待时间重置为0，一视同仁。实现简单，但对已接受的"无辜玩家"不公平，容易引发差评。

**② 无辜方时间保留（Innocent-First）**：已点击接受的玩家保留其此前的等待时间加成（Priority Score），未确认玩家从头计时。《Dota 2》的匹配系统采用此策略，已接受玩家在下一次匹配中会获得一定的优先权重。

**③ 惩罚队列（Penalty Queue）**：超时或拒绝的玩家被强制进入冷却期，禁止匹配。《英雄联盟》的初次超时惩罚为 **5分钟** 禁队，第二次为 **10分钟**，第三次起为 **30分钟**；反复拒绝的玩家还会被放入"低优先级队列"（Low Priority Queue），匹配等待时间人为拉长至正常的3～5倍（Riot Games Support, 2021）。

三种策略的核心权衡体现在一个设计目标上：**降低"无辜玩家"因他人不接受而额外等待的期望时间**。设 $n$ 为每场参与玩家数，每位玩家不接受的概率为 $p$，则一场配对被取消的概率为：

$$P_{\text{cancel}} = 1 - (1-p)^n$$

当 $n=10$，$p=0.03$ 时，$P_{\text{cancel}} \approx 26\%$——即约四分之一的配对会因至少一人不接受而失败。这一数字说明了为何惩罚策略对于大房间游戏（10人、12人）尤为关键。

### 队伍内部的确认同步

当参与匹配的玩家存在预组队伍（Pre-made Party）时，确认逻辑会引入额外复杂度。主要有两种处理方式：

- **个人确认模式（Per-Player）**：队伍中每位成员独立点击接受，任意一人拒绝或超时均导致整个配对取消。《英雄联盟》和《Valorant》均采用此模式，优点是精准过滤AFK成员；缺点是队伍越大，整体被取消的概率越高（$P_{\text{cancel}}$ 随 $n$ 线性增加）。

- **队长代理模式（Captain Proxy）**：队长一人代表全队点击确认，队员无需操作。《魔兽世界》的团队副本在某些版本中采用此方式，优点是减少配对取消率；缺点是队长AFK会拖累整队。

混合方案是在队长确认后向队员发送简短通知（非强制确认），允许队员在5秒内行使"一票否决"，超过5秒则视为同意。这种方案在减少交互负担的同时保留了成员的退出权利。

---

## 关键实现：服务端伪代码

```python
import asyncio
from enum import Enum

class SessionState(Enum):
    PENDING = "PENDING"
    ALL_READY = "ALL_READY"
    DECLINED = "DECLINED"
    TIMEOUT = "TIMEOUT"

class ReadyCheckSession:
    def __init__(self, session_id: str, players: list, timeout: float = 12.0):
        self.session_id = session_id
        # player_id -> bool | None  (None=未响应, True=接受, False=拒绝)
        self.responses = {pid: None for pid in players}
        self.timeout = timeout
        self.state = SessionState.PENDING
        self._timer_task = None

    async def start(self, on_result_callback):
        """启动倒计时并推送弹窗给所有玩家"""
        await self._push_popup_to_all()
        self._timer_task = asyncio.create_task(
            self._timeout_handler(on_result_callback)
        )

    async def _timeout_handler(self, callback):
        await asyncio.sleep(self.timeout)
        if self.state == SessionState.PENDING:
            self.state = SessionState.TIMEOUT
            # 超时未响应者 = response is None
            afk_players = [pid for pid, r in self.responses.items() if r is None]
            await callback(self.state, afk_players)

    async def on_player_response(self, player_id: str, accepted: bool, callback):
        if self.state != SessionState.PENDING:
            return  # 已终止，忽略迟到响应
        self.responses[player_id] = accepted
        if not accepted:
            self.state = SessionState.DECLINED
            self._timer_task.cancel()
            await callback(self.state, [player_id])
        elif all(r is True for r in self.responses.values()):
            self.state = SessionState.ALL_READY
            self._timer_task.cancel()
            await callback(self.state, [])

    async def _push_popup_to_all(self):
        for pid in self.responses:
            # 通过WebSocket/gRPC向客户端推送确认弹窗
            await push_notification(pid, {
                "type": "READY_CHECK",
                "session_id": self.session_id,
                "timeout_seconds": self.timeout
            })
```

上述实现中，`on_player_response` 每次调用的时间复杂度为 $O(n)$（全体检查是否 ALL_READY），对于 $n \leq 20$ 的典型游戏房间可以接受；若房间规模扩大至百人（如大型MMO副本），应改用计数器替代遍历，将复杂度降至 $O(1)$。

---

## 实际应用案例

**案例1：《英雄联盟》段位匹配中的超时惩罚效果**

Riot Games于2016年发布的匹配系统技术博文披露：引入累计惩罚冷却机制后，连续两局均发生确认失败的概率从 **8.7%** 下降至 **3.1%**，即"连续倒霉"的体验发生率降低了约64%。这表明惩罚策略对高频AFK玩家产生了有效抑制（Riot Engineering Blog, 2016）。

**案例2：超时时长A/B测试**

某款移动MOBA游戏（5v5，10人场）在灰度测试阶段将确认超时从15秒缩短至10秒，观测到配对取消率从 **21%** 上升至 **29%**，主要原因是移动端玩家的屏幕切换延迟更高（平均约3.2秒才能看到弹窗）。最终该团队改为：移动端15秒、PC端10秒的差异化超时配置。

例如，若某玩家使用4G网络且信号不稳定，RTT P95可达500ms，则其有效反应窗口在10秒超时下仅剩 $10 - 0.5 - 0.3 \approx 9.2$ 秒，勉强够用；但若该玩家同时在外卖平台下单，9秒内回到游戏的概率显著下降，这正是移动端需要更长超时的根本原因。

---

## 常见误区

**误区1："拒绝"和"超时"应该受到相同惩罚**

事实上，主动拒绝（Decline）与被动超时（Timeout）代表两种截然不同的用户意图。主动拒绝表示玩家有意识地选择不进入这局游戏，通常是因为看到了不满意的队友信息或临时有事；被动超时则更多意味着网络问题或真实AFK。《Dota 2》对二者施加相同惩罚，而《英雄联盟》在特定版本中对"主动拒绝"的惩罚略重于"被动超时"，体现了对玩家意图的区分。

**误区2：确认窗口应显示对手阵容信息**

部分早期游戏在确认窗口中展示了匹配到的对手段位或队友列表，结果导致"阵容挑选型拒绝"（Lobby Dodging）率激增——玩家看到不满意的阵容后故意拒绝以重新匹配，直接导致匹配系统负荷增加。《英雄联盟》明确不在12秒确认窗口中显示任何队友/对手信息，仅在全员确认进入英雄选择界面后才公开阵容，正是为了遏制这种行为。

**误区3：准备确认可以替代心跳检