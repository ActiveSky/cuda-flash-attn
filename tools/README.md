# XPUOJ 自动提交脚本

脚本：[tools/xpuoj_submit.py](tools/xpuoj_submit.py)

## 职责边界

脚本只做三件事：**提交 → 轮询 → 输出结果数据**。它**不负责**生成任何人类可读的报告/Markdown——结果文件的格式化、分析、归档由 agent（Claude）读取脚本输出后自行完成。这样脚本保持简单，报告格式的演进不需要改脚本。

## 安全说明

不要把真实密码写入脚本、`.env`、Markdown 结果或命令行参数。推荐使用短期 API token；如果必须使用密码，用环境变量或运行时交互输入。

```bash
export XPUOJ_EMAIL='your-email@example.com'
export XPUOJ_PASSWORD='your-password'
```

也可以直接使用已有 Bearer token：

```bash
export XPUOJ_API_TOKEN='your-api-token'
```

脚本不会打印密码，也不会保存密码。建议提交完成后清理当前 shell 中的环境变量：

```bash
unset XPUOJ_PASSWORD XPUOJ_API_TOKEN
```

## 凭据自动加载

脚本会自动加载 `tools/.env`（`XPUOJ_EMAIL` / `XPUOJ_PASSWORD` 或 `XPUOJ_API_TOKEN`），无需手动 `source`；已有环境变量优先，不会被 `.env` 覆盖。

## 使用方式

默认是 dry-run，只检查文件和参数，不会创建提交：

```bash
python tools/xpuoj_submit.py solutions/cuda_maca_version.cpp
```

确认代码无误后，显式增加 `--submit` 才会真实提交：

```bash
python tools/xpuoj_submit.py solutions/cuda_maca_version.cpp --submit
```

题目默认配置为比赛 #11 的第 1 题、`cuda.maca-c500`。如需切换：

```bash
python tools/xpuoj_submit.py path/to/solution.cu \
  --contest-id 11 \
  --problem-order 1 \
  --language cuda.maca-c500 \
  --submit
```

### 输出产物

1. **stdout 精简摘要**：提交编号、状态、总分、以及每个测试点的 SPJ 解析结果
   （Baseline / User kernel / Speedup / Score ratio / Display score），JSON 格式，可直接被 agent 读取。
2. **完整结果归档**：`results/raw/cuda_<id>_raw.json` —— 评测接口返回的完整 JSON
   （含 `raw_detail` 与 OJCHAL/OJRESULT 原始协议文本），供 agent 深度分析。

agent 拿到这两份数据后，自行决定如何更新 `results/cuda_result.md` 等报告文件。

### 其他模式

```bash
# 列出最近 N 条自己的比赛提交（默认 10）
python tools/xpuoj_submit.py --list 8

# 持续监控：自动发现新提交，终态后自动归档 JSON 并输出摘要
# （首次运行只建立基线，不会重复归档历史提交；Canceled 跳过归档）
python tools/xpuoj_submit.py --monitor

# 跟踪已有提交（不创建新提交，避免重复提交）
python tools/xpuoj_submit.py --watch 103918

# 取消 pending 提交
python tools/xpuoj_submit.py --cancel 103922

# 提交但不保存 JSON 归档（只输出 stdout 摘要）
python tools/xpuoj_submit.py solutions/cuda_maca_version.cpp --submit --no-archive

# 自定义归档目录
python tools/xpuoj_submit.py solutions/cuda_maca_version.cpp --submit --archive-dir /tmp/oj-archives

# 跳过样例执行
python tools/xpuoj_submit.py solutions/cuda_maca_version.cpp --submit --skip-samples
```

## 轮询行为

- 提交后每 3 秒轮询 `submission/getSubmissionDetail`（POST，`submissionId` 为字符串），
  直到进入终态或超过 `--timeout-seconds`（默认 900 秒）。
- 仅当状态/进度变化时打印一行，避免刷屏。
- 网络请求带 2 次重试（指数退避），评测中途断网不会立刻丢失结果。

## 当前题目参数

脚本默认提交到：

- API：XPUOJ 官方 API
- 比赛：`contestId=11`
- 题目序号：`problemOrder=1`
- 语言：`cuda.maca-c500`（沐曦 C500 的 CUDA 环境）

脚本使用 `contest/play/submit` 提交，因此适用于当前比赛题目页面。若 OJ 前端 API 发生变化，需要同步更新 API 路径或请求字段。
