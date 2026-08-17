# Goal：MetaX C500 FlashAttention 打榜前三

持续优化本仓库的 XPUOJ Contest 11 FlashAttention paged KV-cache decode CUDA/MACA 实现，直到有一份 14/14 Accepted 提交达到或超过 leadboard.md 记录的第三名总分。

## 当前起点

| 项目 | 当前值 |
|---|---|
| 结构性 control | #113889 / exp559 / 66.00 / 14/14 Accepted |
| control SHA-256 | a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972 |
| 历史最高 timing 样本 | #115574 / 66.14；不是结构性 control |
| 最新终态 | #115744 / exp578 / 66.07；target case 未跨档，已拒绝 |
| 当前 OJ | 无在途提交 |
| 第三名门槛 | 69.64 |

详细 OJ 事实见 results/cuda_result.md；本地实验和关闭依据见 notes.md。不要在本文件追加逐实验过程。

## 执行权限与方法

- 先完整阅读 AGENTS.md，并将其中的真值优先级、正确性门禁、OJ 闭环、文件边界和多 agent 规则视为强制要求。
- 本 goal 授权主 agent：对通过 AGENTS.md 规定安全门禁、拥有明确机制和预注册 target case 的候选，串行执行一次 OJ probe。该权限不授予 subagent。
- 主 agent 选择和管理实验方向；最多四个、单层 subagent 仅做边界清晰的探索或隔离执行。主 agent 独占工作文件集成、真实 C500 benchmark、OJ、归档和项目记录更新。
- OJ 是性能和 display tier 的最终真值；本地性能是辅助证据，不能因中性、轻微回退或噪声阻止合格候选的一次 OJ probe。只有明显、可重复且覆盖范围一致的系统性本地回退才可暂缓。
- 排名只读取用户维护的 leadboard.md，不主动联网刷新。

## 终止条件

只有 14/14 Accepted 且总分达到或超过当时 leadboard.md 第三名门槛，才可将本 goal 标记为完成。分数暂时不升、候选失败、OJ 排队或本地环境受限都不是终止条件；仍有安全、独立的研究或验证工作时继续推进。
