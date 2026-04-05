---
id: "vfx-fb-distortion-tex"
concept: "扭曲序列帧"
domain: "vfx"
subdomain: "flipbook"
subdomain_name: "序列帧特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 扭曲序列帧

## 概述

扭曲序列帧是一种通过播放预渲染的Distortion（扭曲）纹理序列来模拟空间形变效果的特效技术，典型用途包括热浪扭曲、爆炸冲击波扩散、瞬移传送门边缘等视觉效果。与普通颜色序列帧不同，扭曲序列帧本身并不输出可见颜色，而是通过偏移屏幕UV坐标来"扭曲"背后的场景像素，产生折射或波动感。

该技术在游戏特效领域的普及与GrabPass（屏幕抓取通道）和后处理Distortion Buffer的引入密切相关。Unreal Engine 3时代（约2007年起）开始将Distortion Pass作为标准渲染流水线的独立通道处理，Unity则在2012年左右通过GrabPass支持将扭曲效果引入移动端工作流。现代项目中，扭曲序列帧通常以16×16或8×8的sprite sheet布局存储，每帧分辨率多为256×256或512×512像素。

扭曲序列帧的核心价值在于用极低的性能代价模拟折射物理现象。一个仅有16帧的扭曲序列配合Distortion Shader，可以逼真还原热空气因折射率随温度变化（折射率n约从1.000至1.003变化）而产生的视觉扭曲，而无需实际模拟流体或光线弯曲计算。

## 核心原理

### Distortion纹理的编码方式

扭曲序列帧的纹理通常将UV偏移量编码进RG通道，其中R通道控制水平方向（U轴）偏移，G通道控制垂直方向（V轴）偏移。标准编码规则为：像素值0.5（即灰色128）表示零偏移，大于0.5表示正方向偏移，小于0.5表示负方向偏移。偏移量计算公式为：

**offset = (texColor.rg - 0.5) × distortionStrength**

其中`distortionStrength`是材质中可调的偏移强度参数，典型取值范围为0.02至0.15（以UV空间单位计）。最终屏幕采样UV为：

**screenUV_final = screenUV_original + offset**

B通道和A通道可用于存储遮罩信息，控制扭曲效果的边缘衰减，避免扭曲区域产生硬边。

### 序列帧动画的帧驱动机制

扭曲序列帧的帧切换逻辑与自发光序列帧完全一致——通过将时间参数映射到sprite sheet的行列索引来偏移UV采样区域。假设sprite sheet为4×4共16帧，每帧UV宽高为0.25。当前帧索引frame_index由以下公式计算：

**frame_index = floor(Time × FPS) mod TotalFrames**

然后将frame_index拆分为行（row = floor(frame_index / cols)）和列（col = frame_index mod cols），最终UV偏移为(col × frameWidth, row × frameHeight)。关键区别在于：扭曲序列帧采样到的值不作为颜色输出，而是作为UV扰动量叠加到屏幕采样坐标上。

### 渲染顺序与GrabPass的依赖关系

扭曲序列帧必须在不透明物体渲染完成之后才能抓取有效的屏幕内容。在Unity中，使用GrabPass的材质渲染队列通常设置为Transparent（3000）或更高。渲染流程为：①渲染所有Opaque物体 → ②GrabPass抓取当前屏幕到_GrabTexture → ③扭曲Shader用扭曲序列帧偏移后的UV从_GrabTexture采样 → ④输出扭曲后的像素。若扭曲特效的渲染队列值低于2000（Opaque阶段），GrabPass抓取到的内容为空帧，扭曲效果完全失效。

## 实际应用

**热浪效果**：在沙漠场景或火焰上方放置扭曲序列帧粒子，纹理使用频率约2-4Hz的低强度翻腾噪声序列（strength值约0.03-0.06）。热浪通常使用垂直方向偏移幅度大于水平方向的非对称扭曲纹理，配合粒子由下至上的运动轨迹，模拟热气流上升效果。

**爆炸冲击波**：冲击波需要由内向外快速扩展的环形扭曲图案。序列帧帧率设为24fps，总帧数16帧，播放一次性不循环。纹理的扭曲强度从第1帧（strength≈0.12，强烈中心聚集）到第16帧（strength≈0.01，边缘消散）呈指数衰减，配合粒子缩放曲线在0.3秒内从0扩展至爆炸半径。

**传送门边缘折射**：传送门使用循环播放的旋转涡旋扭曲序列，帧率8fps，共16帧。扭曲强度保持恒定约0.08，A通道遮罩控制边缘羽化宽度约为传送门半径的15%，避免传送门外的场景发生意外扭曲。

## 常见误区

**误区一：将扭曲强度设置过大导致画面撕裂**。distortionStrength超过0.2时，UV偏移量可能将采样点移出屏幕边界（UV超出0-1范围），导致采样到错误像素或出现黑边。正确做法是对最终screenUV_final执行clamp(0,1)操作，或将strength严格限制在0.15以内，热浪和冲击波效果在0.05-0.12范围内已足够真实。

**误区二：把扭曲序列帧的RG通道误当法线贴图使用**。法线贴图的RG通道编码方式也是将0.5作为零值，外观上与扭曲纹理相似，但法线贴图的偏移量在切线空间中用于光照计算，直接代入扭曲UV偏移公式会因坐标空间不匹配产生错误的扭曲方向。扭曲纹理必须专门制作或在DCC软件中将向量场以RG格式导出，不能复用法线贴图资产。

**误区三：在移动端不加限制地使用GrabPass**。GrabPass每次调用都会完整复制一次当前帧缓冲（在1080p分辨率下约为8MB的纹理传输），多个扭曲粒子同时触发多次GrabPass会导致严重的带宽压力。移动端优化方案是统一使用一个全局GrabPass（在Shader中声明`GrabPass { "_GlobalDistortionTex" }`），所有扭曲材质共享同一次抓取结果，将带宽消耗从O(n)降至O(1)。

## 知识关联

扭曲序列帧建立在**自发光序列帧**的sprite sheet采样机制之上——两者的帧索引计算公式完全相同，区别仅在于采样结果的用途：自发光序列帧将颜色值输出到emission通道，扭曲序列帧将RG值转换为UV偏移量。掌握自发光序列帧的行列UV计算后，理解扭曲序列帧只需额外学习Distortion通道的编码解码规则。

学习扭曲序列帧之后，进阶方向是**序列帧Shader**的完整实现——在Shader代码层面手动编写帧索引计算、GrabPass采样、UV扰动的完整逻辑，而不依赖材质编辑器的节点拼接。序列帧Shader还会引入对扭曲强度随粒子生命周期动态调节的顶点色读取技术，使冲击波的强度衰减曲线可以由美术直接在粒子系统的颜色曲线中控制，而无需修改Shader参数。