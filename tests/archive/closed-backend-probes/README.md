# 已闭合的 C500 backend probes

本目录保存一次性后端能力、fragment、codegen、shuffle、barrier 和历史集成诊断。它们不是日常回归，也不是默认的新优化起点；保留源码是为了让 `notes.md` 中的反证可复现。

只有当编译器/目标架构、线程布局、fragment ownership、状态契约或流水依赖等关键前提明确改变时，才可基于 changed-precondition 重开。重开时从本目录复制出新的语义化 probe 到 `tests/` 根层，不直接修改历史证据。
