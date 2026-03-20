---
domain: game-ui-ux
subdomain: ui-tech
concept_id: guiux-tech-layout-engine
title: 布局引擎
difficulty: 3
is_milestone: false
tags: ["ui-tech", "布局引擎"]
---

# 布局引擎

> **领域**: 游戏UI/UX > UI技术实现 | **难度**: ⭐⭐⭐ | **预计学习时间**: 29分钟

## 核心概念

Flexbox/网格/堆栈等自动布局算法的实现

## 主流UI框架

| 框架 | 引擎 | 模式 | 特点 |
|------|------|------|------|
| UMG | Unreal | Retained | 蓝图可视化, Slate底层 |
| UGUI | Unity | Retained | Canvas, EventSystem |
| UI Toolkit | Unity | Retained | CSS-like, 数据绑定 |
| Dear ImGui | 通用 | Immediate | 轻量, 适合Debug |

## 架构模式

1. **MVVM** — Model-View-ViewModel, 数据与视图解耦
2. **MVC** — Model-View-Controller, 经典三层分离
3. **响应式** — 数据变化自动驱动UI更新

## 性能优化重点

- **减少DrawCall** — Sprite Atlas打包、动静分离Canvas
- **减少Rebuild** — 避免频繁修改Layout属性
- **减少Raycast** — 对非交互元素关闭Raycast Target
- **虚拟滚动** — 长列表只渲染可见项

## 技术选型建议

- 简单2D游戏 → UGUI / HTML5 Canvas
- 3A大作 → UMG + Slate自定义
- 工具/编辑器 → ImGui
- 跨平台 → Flutter / React Native (非实时游戏)

## 关键术语

- **布局引擎**: Flexbox/网格/堆栈等自动布局算法的实现

## 学习建议

1. 先理解基本概念和设计原则
2. 分析优秀游戏中的实际案例
3. 尝试在自己的项目中实践
4. 收集用户反馈并迭代优化

## 参考资源

- Game UI Database (gameuidatabase.com) — 游戏UI截图参考库
- Laws of UX — UX设计法则集合
- GDC UI/UX Summit — 年度游戏UI/UX峰会演讲
