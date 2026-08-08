#!/usr/bin/env python3
"""验证 cuda-maca-version.cpp 的算法逻辑（CPU 模拟重放，无需 GPU）。

用 numpy 精确重放 kernel 的实现逻辑：
  - GQA 分组：query head h 使用 kv_head = h // gqa_ratio
  - page 索引：token t -> block_table[b, t//16]，页内偏移 t%16
  - split-KV：按 pages_per_split 切分区间，在线 softmax 局部统计，
    log-sum-exp 合并（与归约 kernel 相同的公式）
  - 按 cache_seqlens[b] 截断，padding 槽位不读取

与直接 softmax 参考实现对比，覆盖题目中的各类边界 case。
"""

import argparse

import numpy as np

from c500_case_manifest import CASES, CaseConfig, split_policy

HEAD_DIM = 128
PAGE_SIZE = 16
SM_SCALE = 1.0 / np.sqrt(HEAD_DIM)


def split_kernel_sim(q, k_cache, v_cache, cache_seqlens, block_table,
                     num_heads, num_heads_k, seqlen_k, n_split=None):
    """重放 cuda-maca-version.cpp 的主 kernel + 归约 kernel 逻辑。"""
    batch = len(cache_seqlens)
    gqa = num_heads // num_heads_k
    max_pages = (seqlen_k + PAGE_SIZE - 1) // PAGE_SIZE
    pages_per_batch = block_table.shape[1]

    # 与 run_kernel 相同的通用 split 配置。真实 OJ case 的 override 由
    # split_kernel_sim_case() 经 c500_case_manifest.split_policy() 提供。
    if n_split is None:
        n_split = (seqlen_k + 127) // 128
        target_splits = (1024 + batch * num_heads_k - 1) // (batch * num_heads_k)
        n_split = max(1, min(n_split, target_splits))
    pages_per_split = (max_pages + n_split - 1) // n_split

    partial_m = np.full((n_split, batch, num_heads), -np.inf)
    partial_l = np.zeros((n_split, batch, num_heads))
    partial_acc = np.zeros((n_split, batch, num_heads, HEAD_DIM))

    for b in range(batch):
        seqlen = cache_seqlens[b]
        valid_pages = (seqlen + PAGE_SIZE - 1) // PAGE_SIZE
        for kv_head in range(num_heads_k):
            for split in range(n_split):
                p_beg = split * pages_per_split
                p_end = min(p_beg + pages_per_split, valid_pages)
                # 每个 warp 一个 query head（每线程 4 dims，这里用全向量）
                for warp in range(gqa):
                    h = kv_head * gqa + warp
                    m, l = -np.inf, 0.0
                    acc = np.zeros(HEAD_DIM)
                    q_reg = q[b, 0, h, :].astype(np.float64)
                    for p in range(p_beg, p_end):
                        pid = block_table[b, p]
                        t_base = p * PAGE_SIZE
                        for tt in range(PAGE_SIZE):
                            t = t_base + tt
                            if t >= seqlen:      # 末页不满/单 token 截断
                                break
                            kk = k_cache[pid, tt, kv_head, :].astype(np.float64)
                            vv = v_cache[pid, tt, kv_head, :].astype(np.float64)
                            logit = np.dot(q_reg, kk) * SM_SCALE
                            m_new = max(m, logit)
                            alpha = np.exp(m - m_new)
                            pv = np.exp(logit - m_new)
                            m, l = m_new, l * alpha + pv
                            acc = acc * alpha + pv * vv
                    partial_m[split, b, h] = m
                    partial_l[split, b, h] = l
                    partial_acc[split, b, h, :] = acc

    # 归约 kernel
    out = np.zeros((batch, num_heads, HEAD_DIM))
    for b in range(batch):
        for h in range(num_heads):
            ms = partial_m[:, b, h]
            m = ms.max()
            w = np.exp(ms - m)
            l = np.sum(partial_l[:, b, h] * w)
            acc = np.sum(partial_acc[:, b, h, :] * w[:, None], axis=0)
            out[b, h, :] = acc / l if l > 0 else 0.0
    return out


def mma_qk_split_kernel_sim(q, k_cache, v_cache, cache_seqlens, block_table,
                            num_heads, num_heads_k, seqlen_k):
    """重放候选 64-lane MMA-QK + FP32 scalar-PV 的 page/split 语义。

    每页显式构造 Q[16, 128]（未使用 GQA 行置零）和 K^T[128, 16]，
    模拟 8 个 m16n16k16 片段相加后的 score[query_head, token]。随后保持
    candidate 的 ``exp(logit - m_new)`` 形式在线 LSE，与 reduce kernel 的
    ``exp(partial_m - global_m)`` 合并约定严格对应。
    """
    batch = len(cache_seqlens)
    gqa = num_heads // num_heads_k
    max_pages = (seqlen_k + PAGE_SIZE - 1) // PAGE_SIZE

    n_split = (seqlen_k + 127) // 128
    target_splits = (1024 + batch * num_heads_k - 1) // (batch * num_heads_k)
    n_split = max(1, min(n_split, target_splits))
    pages_per_split = (max_pages + n_split - 1) // n_split

    partial_m = np.full((n_split, batch, num_heads), -np.inf, dtype=np.float64)
    partial_l = np.zeros((n_split, batch, num_heads), dtype=np.float64)
    partial_acc = np.zeros((n_split, batch, num_heads, HEAD_DIM), dtype=np.float64)

    for b in range(batch):
        seqlen = int(cache_seqlens[b])
        valid_pages = (seqlen + PAGE_SIZE - 1) // PAGE_SIZE
        for kv_head in range(num_heads_k):
            q_tile = np.zeros((PAGE_SIZE, HEAD_DIM), dtype=np.float64)
            q_tile[:gqa] = q[b, 0, kv_head * gqa:(kv_head + 1) * gqa].astype(np.float64)
            for split in range(n_split):
                p_beg = split * pages_per_split
                p_end = min(p_beg + pages_per_split, valid_pages)
                m = np.full(gqa, -np.inf, dtype=np.float64)
                l = np.zeros(gqa, dtype=np.float64)
                acc = np.zeros((gqa, HEAD_DIM), dtype=np.float64)

                for p in range(p_beg, p_end):
                    pid = block_table[b, p]
                    # Equivalent to eight 16x16x16 tiles Q @ K.T. The tile
                    # decomposition is explicit so a transpose/orientation
                    # mistake cannot be hidden by the reference implementation.
                    scores = np.zeros((PAGE_SIZE, PAGE_SIZE), dtype=np.float64)
                    for kt in range(8):
                        q_fragment = q_tile[:, kt * 16:(kt + 1) * 16]
                        k_fragment_t = k_cache[pid, :, kv_head,
                                               kt * 16:(kt + 1) * 16].astype(np.float64).T
                        scores += q_fragment @ k_fragment_t

                    t_base = p * PAGE_SIZE
                    nvalid = max(0, min(PAGE_SIZE, seqlen - t_base))
                    logits = scores[:gqa, :nvalid] * SM_SCALE
                    m_page = logits.max(axis=1)
                    m_new = np.maximum(m, m_page)
                    alpha = np.exp(m - m_new)
                    weights = np.exp(logits - m_new[:, None])
                    vv = k_cache[pid, :nvalid, kv_head, :]  # shape sentinel only
                    del vv
                    v_page = v_cache[pid, :nvalid, kv_head, :].astype(np.float64)
                    acc = acc * alpha[:, None] + weights @ v_page
                    l = l * alpha + weights.sum(axis=1)
                    m = m_new

                for qh in range(gqa):
                    h = kv_head * gqa + qh
                    partial_m[split, b, h] = m[qh]
                    partial_l[split, b, h] = l[qh]
                    partial_acc[split, b, h] = acc[qh]

    out = np.zeros((batch, num_heads, HEAD_DIM), dtype=np.float64)
    for b in range(batch):
        for h in range(num_heads):
            ms = partial_m[:, b, h]
            m = ms.max()
            w = np.exp(ms - m)
            l = np.sum(partial_l[:, b, h] * w)
            acc = np.sum(partial_acc[:, b, h, :] * w[:, None], axis=0)
            out[b, h] = acc / l if l > 0 else 0.0
    return out


def run_mma_tile_case(name, rng, batch, seqlen_k, num_heads_k, tol=1e-4):
    """Compare the candidate's tiled-QK online-LSE path to direct attention."""
    q, k_cache, v_cache, cache_seqlens, block_table, _ = gen_case(
        rng, batch, seqlen_k, num_heads_k)
    sim = mma_qk_split_kernel_sim(q, k_cache, v_cache, cache_seqlens, block_table,
                                  32, num_heads_k, seqlen_k)
    ref = reference(q, k_cache, v_cache, cache_seqlens, block_table, 32, num_heads_k)
    diff = np.abs(sim - ref)
    max_err = diff.max()
    ok = max_err < tol
    print(f"[{'PASS' if ok else 'FAIL'}] {name:28s} batch={batch:4d} seqlen_k={seqlen_k:6d} "
          f"kv={num_heads_k} | max_err={max_err:.3e} "
          f"| seqlen 范围 [{cache_seqlens.min()},{cache_seqlens.max()}]")
    return ok


def bf16_round_to_float32(x):
    """Round float32 values to BF16 then return their exact float32 values."""
    x32 = np.asarray(x, dtype=np.float32)
    bits = x32.view(np.uint32).copy()
    # Round-to-nearest-even, matching CUDA __float2bfloat16 for finite inputs.
    bits += np.uint32(0x7fff) + ((bits >> np.uint32(16)) & np.uint32(1))
    bits &= np.uint32(0xffff0000)
    return bits.view(np.float32)


def mma_pv_bf16_split_kernel_sim(q, k_cache, v_cache, cache_seqlens, block_table,
                                 num_heads, num_heads_k, seqlen_k):
    """Model QK MMA with BF16 P x BF16 V MMA and FP32 output accumulation.

    The LSE denominator is intentionally retained in FP32; only the matrix-PV
    numerator follows the proposed hardware path by rounding unnormalized
    page weights to BF16 before each FP32 MMA accumulation.
    """
    batch = len(cache_seqlens)
    gqa = num_heads // num_heads_k
    max_pages = (seqlen_k + PAGE_SIZE - 1) // PAGE_SIZE
    n_split = (seqlen_k + 127) // 128
    target_splits = (1024 + batch * num_heads_k - 1) // (batch * num_heads_k)
    n_split = max(1, min(n_split, target_splits))
    pages_per_split = (max_pages + n_split - 1) // n_split

    partial_m = np.full((n_split, batch, num_heads), -np.inf, dtype=np.float64)
    partial_l = np.zeros((n_split, batch, num_heads), dtype=np.float64)
    partial_acc = np.zeros((n_split, batch, num_heads, HEAD_DIM), dtype=np.float64)

    for b in range(batch):
        seqlen = int(cache_seqlens[b])
        valid_pages = (seqlen + PAGE_SIZE - 1) // PAGE_SIZE
        for kv_head in range(num_heads_k):
            q_tile = np.zeros((PAGE_SIZE, HEAD_DIM), dtype=np.float32)
            q_tile[:gqa] = q[b, 0, kv_head * gqa:(kv_head + 1) * gqa]
            for split in range(n_split):
                p_beg = split * pages_per_split
                p_end = min(p_beg + pages_per_split, valid_pages)
                m = np.full(gqa, -np.inf, dtype=np.float64)
                l = np.zeros(gqa, dtype=np.float64)
                acc = np.zeros((gqa, HEAD_DIM), dtype=np.float64)

                for p in range(p_beg, p_end):
                    pid = block_table[b, p]
                    scores = np.zeros((PAGE_SIZE, PAGE_SIZE), dtype=np.float64)
                    for kt in range(8):
                        q_fragment = q_tile[:, kt * 16:(kt + 1) * 16].astype(np.float64)
                        k_fragment_t = k_cache[pid, :, kv_head,
                                               kt * 16:(kt + 1) * 16].astype(np.float64).T
                        scores += q_fragment @ k_fragment_t
                    t_base = p * PAGE_SIZE
                    nvalid = max(0, min(PAGE_SIZE, seqlen - t_base))
                    logits = scores[:gqa, :nvalid] * SM_SCALE
                    m_page = logits.max(axis=1)
                    m_new = np.maximum(m, m_page)
                    alpha = np.exp(m - m_new)
                    weights = np.exp(logits - m_new[:, None])
                    weights_bf16 = bf16_round_to_float32(weights).astype(np.float64)
                    v_page_bf16 = bf16_round_to_float32(
                        v_cache[pid, :nvalid, kv_head, :]).astype(np.float64)
                    # This matrix product represents eight 16x16 PV MMA tiles.
                    acc = acc * alpha[:, None] + weights_bf16 @ v_page_bf16
                    l = l * alpha + weights.sum(axis=1)
                    m = m_new

                for qh in range(gqa):
                    h = kv_head * gqa + qh
                    partial_m[split, b, h] = m[qh]
                    partial_l[split, b, h] = l[qh]
                    partial_acc[split, b, h] = acc[qh]

    out = np.zeros((batch, num_heads, HEAD_DIM), dtype=np.float64)
    for b in range(batch):
        for h in range(num_heads):
            ms = partial_m[:, b, h]
            m = ms.max()
            weights = np.exp(ms - m)
            l = np.sum(partial_l[:, b, h] * weights)
            acc = np.sum(partial_acc[:, b, h, :] * weights[:, None], axis=0)
            out[b, h] = acc / l if l > 0 else 0.0
    return out


def run_mma_pv_quantization_case(name, rng, batch, seqlen_k, num_heads_k,
                                  v_scale=1.0):
    """Apply the actual OJ allclose/99%-and-no-outlier acceptance envelope."""
    q, k_cache, v_cache, cache_seqlens, block_table, _ = gen_case(
        rng, batch, seqlen_k, num_heads_k)
    q = bf16_round_to_float32(q)
    k_cache = bf16_round_to_float32(k_cache)
    v_cache = bf16_round_to_float32(v_cache * v_scale)
    sim = mma_pv_bf16_split_kernel_sim(q, k_cache, v_cache, cache_seqlens,
                                       block_table, 32, num_heads_k, seqlen_k)
    ref = reference(q, k_cache, v_cache, cache_seqlens, block_table, 32, num_heads_k)
    diff = np.abs(sim - ref)
    element_tol = 1.6e-2 + 1.6e-2 * np.abs(ref)
    within_tol = diff <= element_tol
    no_outlier = np.all(diff <= 8.0 * element_tol)
    pass_rate = np.mean(within_tol)
    ok = pass_rate >= 0.99 and no_outlier
    print(f"[{'PASS' if ok else 'FAIL'}] {name:28s} batch={batch:4d} seqlen_k={seqlen_k:6d} "
          f"kv={num_heads_k} | max_err={diff.max():.3e} pass={pass_rate:.5f} "
          f"outlier={'none' if no_outlier else 'present'}")
    return ok


def verify_mma_u4_page_staging(rng):
    """Verify the exact uint4-indexed load/transposition used by task #9."""
    num_heads_k = 8
    kv_head = 5
    page = rng.standard_normal((PAGE_SIZE, num_heads_k, HEAD_DIM)).astype(np.float32)

    # Source view is token-major with a full num_heads_k*128 BF16 stride.
    # Build the destination with the same d8 / e mapping as CUDA, then check
    # the row-major WMMA B tile and scalar-PV V aliases independently.
    staged_k = np.empty((8, 16, 16), dtype=np.float32)
    staged_v = np.empty((PAGE_SIZE, HEAD_DIM), dtype=np.float32)
    for token in range(PAGE_SIZE):
        for d8 in range(HEAD_DIM // 8):
            values = page[token, kv_head, d8 * 8:(d8 + 1) * 8]
            for e in range(8):
                staged_k[d8 >> 1, (d8 & 1) * 8 + e, token] = values[e]
                staged_v[token, d8 * 8 + e] = values[e]

    expected_k = np.empty_like(staged_k)
    for kt in range(8):
        expected_k[kt] = page[:, kv_head, kt * 16:(kt + 1) * 16].T
    ok = np.array_equal(staged_k, expected_k) and np.array_equal(
        staged_v, page[:, kv_head, :])
    print(f"[{'PASS' if ok else 'FAIL'}] mma u4 K/V page staging")
    return ok


def grouped_kv8_pv_split_kernel_sim(q, k_cache, v_cache, cache_seqlens, block_table,
                                    seqlen_k, n_split=None):
    """Model the case-local KV8/GQA4 grouped-V scalar-PV kernel.

    The four Q rows retain distinct logits, max, denominator and accumulator.
    Each page instead materializes one V[16, 128] view which is multiplied by
    all four row-weight vectors, matching the CUDA candidate's ownership: one
    V dimension-pair owner updates every GQA row.
    """
    batch = len(cache_seqlens)
    num_heads, num_heads_k, gqa = 32, 8, 4
    max_pages = (seqlen_k + PAGE_SIZE - 1) // PAGE_SIZE
    if n_split is None:
        n_split = (seqlen_k + 127) // 128
        target_splits = (1024 + batch * num_heads_k - 1) // (batch * num_heads_k)
        n_split = max(1, min(n_split, target_splits))
    pages_per_split = (max_pages + n_split - 1) // n_split

    partial_m = np.full((n_split, batch, num_heads), -np.inf, dtype=np.float64)
    partial_l = np.zeros((n_split, batch, num_heads), dtype=np.float64)
    partial_acc = np.zeros((n_split, batch, num_heads, HEAD_DIM), dtype=np.float64)

    for b in range(batch):
        seqlen = int(cache_seqlens[b])
        valid_pages = (seqlen + PAGE_SIZE - 1) // PAGE_SIZE
        for kv_head in range(num_heads_k):
            q_rows = q[b, 0, kv_head * gqa:(kv_head + 1) * gqa].astype(np.float64)
            for split in range(n_split):
                p_beg = split * pages_per_split
                p_end = min(p_beg + pages_per_split, valid_pages)
                m = np.full(gqa, -np.inf, dtype=np.float64)
                l = np.zeros(gqa, dtype=np.float64)
                acc = np.zeros((gqa, HEAD_DIM), dtype=np.float64)
                for p in range(p_beg, p_end):
                    pid = block_table[b, p]
                    t_base = p * PAGE_SIZE
                    nvalid = max(0, min(PAGE_SIZE, seqlen - t_base))
                    k_page = k_cache[pid, :nvalid, kv_head, :].astype(np.float64)
                    # This is deliberately one page view shared by all Q rows.
                    v_page = v_cache[pid, :nvalid, kv_head, :].astype(np.float64)
                    logits = q_rows @ k_page.T * SM_SCALE
                    m_page = logits.max(axis=1)
                    m_new = np.maximum(m, m_page)
                    alpha = np.exp(m - m_new)
                    weights = np.exp(logits - m_new[:, None])
                    l = l * alpha + weights.sum(axis=1)
                    acc = acc * alpha[:, None] + weights @ v_page
                    m = m_new
                for qh in range(gqa):
                    h = kv_head * gqa + qh
                    partial_m[split, b, h] = m[qh]
                    partial_l[split, b, h] = l[qh]
                    partial_acc[split, b, h] = acc[qh]

    out = np.zeros((batch, num_heads, HEAD_DIM), dtype=np.float64)
    for b in range(batch):
        for h in range(num_heads):
            m = partial_m[:, b, h].max()
            weights = np.exp(partial_m[:, b, h] - m)
            l = np.sum(partial_l[:, b, h] * weights)
            acc = np.sum(partial_acc[:, b, h, :] * weights[:, None], axis=0)
            out[b, h] = acc / l if l > 0 else 0.0
    return out


def run_grouped_kv8_pv_case(name, rng, batch, seqlen_k, n_split, tol=1e-4):
    """Check GQA4 V reuse, online rescaling, split combine and page tails."""
    q, k_cache, v_cache, cache_seqlens, block_table, _ = gen_case(
        rng, batch, seqlen_k, 8)
    sim = grouped_kv8_pv_split_kernel_sim(q, k_cache, v_cache, cache_seqlens,
                                          block_table, seqlen_k, n_split)
    ref = reference(q, k_cache, v_cache, cache_seqlens, block_table, 32, 8)
    diff = np.abs(sim - ref)
    ok = diff.max() < tol
    print(f"[{'PASS' if ok else 'FAIL'}] {name:28s} batch={batch:4d} seqlen_k={seqlen_k:6d} "
          f"kv=8 gqa=4 | max_err={diff.max():.3e} "
          f"| seqlen 范围 [{cache_seqlens.min()},{cache_seqlens.max()}]")
    return ok


def reference(q, k_cache, v_cache, cache_seqlens, block_table, num_heads, num_heads_k):
    """直接 softmax 参考实现（题目数学定义）。"""
    batch = len(cache_seqlens)
    gqa = num_heads // num_heads_k
    out = np.zeros((batch, num_heads, HEAD_DIM))
    for b in range(batch):
        seqlen = cache_seqlens[b]
        for h in range(num_heads):
            kv = h // gqa
            kk = np.stack([
                k_cache[block_table[b, t // PAGE_SIZE], t % PAGE_SIZE, kv, :].astype(np.float64)
                for t in range(seqlen)])
            vv = np.stack([
                v_cache[block_table[b, t // PAGE_SIZE], t % PAGE_SIZE, kv, :].astype(np.float64)
                for t in range(seqlen)])
            logits = q[b, 0, h, :].astype(np.float64) @ kk.T * SM_SCALE
            logits -= logits.max()
            p = np.exp(logits)
            p /= p.sum()
            out[b, h, :] = p @ vv
    return out


def gen_case(rng, batch, seqlen_k, num_heads_k, num_blocks_per_seq=None):
    """构造题目格式的随机输入。padding 槽位填入随机合法 page id（陷阱值）。"""
    num_heads = 32
    max_pages = (seqlen_k + PAGE_SIZE - 1) // PAGE_SIZE
    pages_per_batch = max_pages if num_blocks_per_seq is None else num_blocks_per_seq

    q = rng.standard_normal((batch, 1, num_heads, HEAD_DIM)).astype(np.float32)
    k_cache = rng.standard_normal((batch * pages_per_batch, PAGE_SIZE, num_heads_k, HEAD_DIM)).astype(np.float32)
    v_cache = rng.standard_normal((batch * pages_per_batch, PAGE_SIZE, num_heads_k, HEAD_DIM)).astype(np.float32)

    cache_seqlens = rng.integers(1, seqlen_k + 1, size=batch)
    # 固定一种：让一半序列取 1（单 token），一半取满
    for i in range(batch):
        if i % 2 == 1:
            cache_seqlens[i] = 1

    block_table = np.zeros((batch, pages_per_batch), dtype=np.int32)
    for b in range(batch):
        valid = (cache_seqlens[b] + PAGE_SIZE - 1) // PAGE_SIZE
        # 有效页：随机分配；padding：随机合法 page id（陷阱，不应被读取）
        perm = rng.permutation(batch * pages_per_batch)
        block_table[b, :valid] = perm[:valid]
        block_table[b, valid:] = perm[valid:valid + (pages_per_batch - valid)]
    return q, k_cache, v_cache, cache_seqlens, block_table, pages_per_batch


def run_case(name, rng, batch, seqlen_k, num_heads_k, n_split=None, tol=1e-4):
    q, k_cache, v_cache, cache_seqlens, block_table, ppb = gen_case(
        rng, batch, seqlen_k, num_heads_k)
    num_heads = 32
    sim = split_kernel_sim(q, k_cache, v_cache, cache_seqlens, block_table,
                           num_heads, num_heads_k, seqlen_k, n_split=n_split)
    ref = reference(q, k_cache, v_cache, cache_seqlens, block_table,
                    num_heads, num_heads_k)
    diff = np.abs(sim - ref)
    max_err = diff.max()
    mean_err = diff.mean()
    ok = max_err < tol
    print(f"[{'PASS' if ok else 'FAIL'}] {name:28s} batch={batch:4d} seqlen_k={seqlen_k:6d} "
          f"kv={num_heads_k} split={n_split or 'generic':>7} | "
          f"max_err={max_err:.3e} mean_err={mean_err:.3e} "
          f"| seqlen 范围 [{cache_seqlens.min()},{cache_seqlens.max()}]")
    return ok


def run_manifest_case(case: CaseConfig, rng, max_seqlen_k=None):
    """Replay the production scalar split contract for an authoritative OJ case.

    CPU reference cost grows with B * L.  The default quick suite caps only the
    capacity while retaining the case's actual batch/KV-head/dispatch policy;
    ``--exhaustive`` uses the full OJ capacities.
    """
    seqlen_k = min(case.seqlen_k, max_seqlen_k) if max_seqlen_k else case.seqlen_k
    n_split, _, kernel = split_policy(case)
    if seqlen_k != case.seqlen_k:
        # Preserve the production split count to exercise empty partials even
        # when using a bounded capacity in the quick semantic suite.
        label = f"case{case.case_id}: {kernel} bounded"
    else:
        label = f"case{case.case_id}: {kernel}"
    return run_case(label, rng, case.batch_size, seqlen_k, case.num_heads_k,
                    n_split=n_split)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--exhaustive",
        action="store_true",
        help="run every OJ capacity, including the three 32K+ long cases",
    )
    parser.add_argument(
        "--quick-max-seqlen",
        type=int,
        default=64,
        help="capacity cap for the default fast semantic replay (default: 64)",
    )
    parser.add_argument(
        "--extended-candidates",
        action="store_true",
        help="run expensive historical MMA/PV candidate simulations",
    )
    args = parser.parse_args(argv)

    rng = np.random.default_rng(42)
    results = []
    # The manifest is parsed from an accepted OJ SPJ result, not problem.md.
    # The quick suite still runs every real batch/KV-head shape and its exact
    # split policy, while bounding only expensive CPU reference capacities.
    capacity_cap = None if args.exhaustive else args.quick_max_seqlen
    for case in CASES:
        results.append(run_manifest_case(case, rng, capacity_cap))

    # Candidate simulations are intentionally opt-in: they model historical
    # implementations at large capacities and are useful for design work, but
    # should not turn the normal semantic regression into a multi-minute job.
    if args.extended_candidates:
        # Candidate MMA-QK semantics: tile orientation, GQA row padding, tail
        # masking and split-LSE ownership are independent of C500 code generation.
        results.append(verify_mma_u4_page_staging(rng))
        results.append(run_mma_tile_case("mma QK: KV4 page tail", rng, 4, 17, 4))
        results.append(run_mma_tile_case("mma QK: KV8 page tail", rng, 4, 141, 8))
        results.append(run_mma_tile_case("mma QK: KV4 split", rng, 8, 4096, 4))
        results.append(run_mma_tile_case("mma QK: KV8 split", rng, 8, 4096, 8))
        results.append(run_mma_tile_case("mma QK: KV4 long split", rng, 2, 12251, 4))

        # Grouped KV8/GQA4 PV candidate: each V page is shared across four query
        # rows, while every row keeps independent online state and split partials.
        results.append(run_grouped_kv8_pv_case(
            "grouped PV: case9 split", rng, 32, 4096, 32))
        results.append(run_grouped_kv8_pv_case(
            "grouped PV: tail/empty", rng, 4, 141, 16))

        # MMA PV gate: P must be rounded to BF16 before P x V. These cover the
        # selective long-KV4 dispatch and deliberately amplified values so that a
        # favourable random case cannot conceal a tolerance failure.
        results.append(run_mma_pv_quantization_case("mma PV: KV4 split", rng, 4, 4096, 4))
        results.append(run_mma_pv_quantization_case("mma PV: KV4 long", rng, 2, 12251, 4))
        results.append(run_mma_pv_quantization_case("mma PV: KV8 long", rng, 2, 4096, 8))
        results.append(run_mma_pv_quantization_case("mma PV: scaled stress", rng, 2, 4096, 4,
                                                     v_scale=32.0))

    print(f"\n总计: {sum(results)}/{len(results)} 通过")
    return 0 if all(results) else 1


if __name__ == "__main__":
    exit(main())
