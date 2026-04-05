---
id: "qa-pt-thermal-testing"
concept: "热量测试"
domain: "game-qa"
subdomain: "performance-testing"
subdomain_name: "性能测试(Profiling)"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---




# 热量测试

## 概述

热量测试（Thermal Testing）是针对移动设备长时间运行游戏时，系统性地测量设备表面温度、处理器结温、电池温度，以及由此引发的 CPU/GPU 降频行为和续航损耗的专项性能测试方法。其核心关注点不是瞬时帧率，而是设备在持续热负荷下的**稳态性能表现**（Sustained Performance）。

热量测试的必要性源于移动芯片的散热物理限制。高通骁龙 8 Gen 2 的 TDP（热设计功耗）约为 10W，而典型智能手机铝合金中框的散热能力仅能持续散发 3～4W。这意味着长时间高负载必然触发芯片内部的 Thermal Throttling（热节流）机制——当结温超过阈值（通常 85°C～95°C）时，CPU 或 GPU 主频被强制降低，帧率随之下跌。测试人员必须捕捉这一动态过程，而非只看冷启动时的峰值性能。

在游戏质量保证中，热量测试能够暴露游戏引擎的功耗优化缺陷、定位导致异常发热的渲染管线瓶颈（例如过度绘制 Overdraw 导致 GPU 长时间满载），以及预测玩家在夏季户外、密闭地铁等高温环境下实际游戏体验的性能降级幅度。Google 在 Android 文档中专门指出，未通过 Sustained Performance 测试的游戏，在旗舰机型上 30 分钟后帧率下跌超过 30% 的情况普遍存在（参见 *Android Performance Patterns*, Google Developers, 2022）。

---

## 核心原理

### 热节流（Thermal Throttling）触发机制

移动 SoC 内部集成了 Thermal Management Unit（TMU），实时采样多个热区（Thermal Zone）的温度传感器数值。以安卓平台为例，`/sys/class/thermal/thermal_zone*/temp` 节点以毫摄氏度（m°C）为单位上报各热区温度。当温度超过 `trip_point_0_temp`（通常为 Trip type = passive，约 80°C）时，CPU/GPU 频率被限制到某个功耗包络内的更低档位；超过 `trip_point_1_temp`（Trip type = hot，约 90°C）时降频幅度进一步扩大；若超过临界阈值（Critical Trip，约 105°C），设备将触发自动关机保护。

整个降频过程遵循 PID 控制逻辑：TMU 根据当前温度与目标温度的差值，动态调整 CPU 调度器（schedutil/cpufreq）允许的最高频率。联发科天玑 9200 的 TMU 采样频率为 10ms，即每 10 毫秒修正一次频率上限，这也是为何频率曲线在热节流阶段会出现高频震荡（而非单调下降）。

热量测试的核心记录指标包括：

- **T_throttle**：从冷启动到首次触发降频的时间（分钟）
- **F_stable**：降频后 CPU/GPU 稳定运行的频率（MHz）
- **帧率衰减率**：定义如下

$$
\text{帧率衰减率} = \frac{FPS_{\text{冷启动}} - FPS_{\text{稳态}}}{FPS_{\text{冷启动}}} \times 100\%
$$

业界通常要求游戏在 30 分钟测试周期内帧率衰减率不超过 **15%**。若使用 Android 官方 Sustained Performance API（`Window.setSustainedPerformanceMode(true)`），部分 OEM（如 Google Pixel 系列）会将 CPU 频率锁定在可持续档位，主动牺牲约 10% 峰值性能，以换取 0% 的热节流衰减。

### 设备表面温度与用户体验阈值

表面温度直接影响玩家握持舒适度。IEC 62368-1 标准规定手持设备"抓握部位"持续接触温度上限为 **48°C**。实际测试中，测试人员使用红外热成像仪（如 FLIR ONE Pro，热灵敏度 0.07°C）拍摄设备背面热图，同时用热电偶贴片（K 型，精度 ±0.5°C）在以下三个固定位置采集温度曲线，采样间隔设为 10 秒：

1. **电池区域中心**（通常在设备背面下 1/3 处）
2. **SoC 正对应背面**（主板热源最集中区域）
3. **摄像头模组附近**（次级热区，兼顾充电状态下的发热）

超过 **43°C** 时玩家通常开始感到烫手不适，这是游戏厂商内部实际警戒线，比 IEC 标准严格 5°C。《PUBG Mobile》在 2021 年针对骁龙 888 机型的热量专项优化（降低角色渲染粒子数 30%）将 SoC 背面最高温度从 46°C 压降至 41°C，T_throttle 从 8 分钟延长至 22 分钟。

### 续航与功耗的关联测量

热量测试期间同步记录电池电量下降曲线，通过计算**放电斜率**（%/分钟）来估算整机功耗。更精确的做法是使用外部电流计（如 Monsoon Power Monitor，采样率 5kHz）替代电池供电，直接测量毫瓦级别的实时功耗，配合 Android 的 `dumpsys batterystats` 命令交叉验证。

游戏场景下高性能移动设备的典型整机功耗为 6W～12W，热节流场景下功耗往往突破 12W，此时电池温度本身也会上升。锂离子电池在 45°C 以上长期工作，每充放电循环容量损失速率是 25°C 时的 **2.3 倍**（参见 《锂离子电池原理与关键技术》，吴宇平等，2012，化学工业出版社）。因此，测试报告需同时给出"游戏 30 分钟电量消耗百分比"、"电池最高温度"和"稳态功耗（W）"三项结论。

---

## 关键流程与工具链

### 测试环境标准化

将被测设备置于 **25°C ± 1°C** 的恒温实验室中，静置 30 分钟至设备温度稳定（判断条件：电池温度与室温差值 < 2°C），关闭 Wi-Fi/蓝牙/后台进程（仅保留游戏与数据采集 App），屏幕亮度固定为最大值的 **60%**（模拟实际游戏亮度均值），电池电量充至 100% 后拔除充电线再开始测试。不标准化这些变量会导致同一设备两次测试的 T_throttle 差异超过 5 分钟，结论失去可复现性。

### Android 端数据采集脚本

使用以下 Shell 脚本每 5 秒采集一次温度与 CPU 频率，输出为 CSV 供后续绘图分析：

```bash
#!/bin/bash
# thermal_log.sh — 热量测试数据采集脚本
OUTPUT="thermal_$(date +%Y%m%d_%H%M%S).csv"
echo "timestamp,cpu0_freq_mhz,gpu_freq_mhz,zone0_temp_c,zone1_temp_c,battery_temp_c" > $OUTPUT

while true; do
    TS=$(date +%s)
    CPU_FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null | awk '{printf "%.0f", $1/1000}')
    GPU_FREQ=$(cat /sys/class/kgsl/kgsl-3d0/gpuclk 2>/dev/null | awk '{printf "%.0f", $1/1000000}')
    ZONE0=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{printf "%.1f", $1/1000}')
    ZONE1=$(cat /sys/class/thermal/thermal_zone1/temp 2>/dev/null | awk '{printf "%.1f", $1/1000}')
    BAT_TEMP=$(cat /sys/class/power_supply/battery/temp 2>/dev/null | awk '{printf "%.1f", $1/10}')
    echo "$TS,$CPU_FREQ,$GPU_FREQ,$ZONE0,$ZONE1,$BAT_TEMP" >> $OUTPUT
    sleep 5
done
```

执行时需 `adb shell` 权限或 root 权限。采集结束后，将 CSV 导入 Python（pandas + matplotlib）绘制温度-频率-帧率的三轴时序图，直观定位 T_throttle 时刻与帧率跌落节点的对应关系。

### iOS 端测试工具

iOS 设备不开放 `/sys/class/thermal` 节点，需借助 **Instruments** 的 Energy Log 模板或第三方工具 **iStatistica** 获取 SoC 热状态（Thermal State：Nominal / Fair / Serious / Critical，对应 `ProcessInfo.thermalState` API）。Serious 状态下 A16 Bionic 的 GPU 频率通常被限制到峰值的 65%，Critical 状态下降至 40%。测试人员需在游戏中埋点调用 `NotificationCenter.default.addObserver(forName: ProcessInfo.thermalStateDidChangeNotification)` 实时记录状态变化时间戳，与帧率日志合并分析。

---

## 实际应用案例

**案例：某 MMORPG 骁龙 8 Gen 1 热量问题排查**

2022 年初，骁龙 8 Gen 1 因采用台积电 4nm 工艺良率问题导致功耗异常偏高，多款游戏出现"发布即降频"现象。某 MMORPG 测试团队在标准热量测试中发现：冷启动 FPS 均值为 58，6 分 30 秒后触发首次热节流（T_throttle = 6.5 分钟），20 分钟后稳态 FPS 跌至 34，帧率衰减率 = (58 - 34) / 58 × 100% ≈ **41.4%**，远超 15% 红线。

通过 Snapdragon Profiler 的 Timeline 模式，测试人员定位到大地图区域的**级联阴影（Cascaded Shadow Maps，4 级联，2048×2048 分辨率）**是主要 GPU 热源，每帧 GPU 渲染时间占比 38%。将阴影级联数降至 2 级、分辨率改为 1024×1024 后，整机功耗从 13.2W 降至 9.8W，T_throttle 延长至 18 分钟，稳态帧率回升至 49，衰减率降为 **15.5%**，基本达标。

---

## 常见误区

**误区 1：在充电状态下进行热量测试**
充电过程本身会产生 1W～3W 额外热量（取决于充电协议，100W PD 充电产热更高），导致设备比实际游戏时更早触发热节流，测试结论偏悲观。标准做法是拔除充电线、满电开始测试。

**误区 2：只测一台设备就下结论**
同一型号不同批次设备（因芯片良率差异）的 T_throttle 可相差 3～8 分钟。热量测试应至少覆盖 **3 台同型号设备**，取平均值与最差值分别作为结论，防止因单台设备的硬件偶然因素误导优化方向。

**误区 3：忽视环境温度对测试结果的放大效应**
在 35°C 室温（模拟夏季户外）与 25°C 室温下，同一游戏的 T_throttle 差异可达 **50% 以上**。若只在实验室标准温度下测试，无法预警玩家在高温环境下的实际体验。建议额外增加一组 35°C 环境的测试作为极端场景对照。

**误区 4：把帧率衰减等同于热节流**
帧率下降还可能来自内存 GC 卡顿、加载资源的 IO 阻塞或逻辑线程 CPU 竞争。必须与温度曲线、CPU/GPU 频率曲线三者联动比对，才能确认帧率下降的根本原因是热节流而非其他性能瓶颈。

---

## 知识关联

热量测试与**长时间运行测试**（Long Session Testing）的关系：长时间运行测试关注内存泄漏、逻辑 Bug 的时间累积暴露，热量测试则专注于同一时间维度内的物理散热约束。两者通常合并为单次 60 分钟的综合测试 Session，同时采集帧率、内存、温度、频率四条曲线，一次跑完