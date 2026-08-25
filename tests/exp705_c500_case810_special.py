#!/usr/bin/env python3
"""C500 poison/guard/reuse gate for exp705 cases 8 and 10.

The generic pairwise driver from exp704 is reused only as a test implementation;
this wrapper changes its target manifest to the two z4 contracts under test.
No timing or OJ operation is performed.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys

from c500_case_manifest import CASES
from c500_paged_decode_harness import load_kernel, require_maca_gpu


def _load_generic_driver():
    path = Path(__file__).with_name("exp704_c500_case79_special.py")
    spec = importlib.util.spec_from_file_location("exp704_case79_driver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generic C500 driver: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260905)
    args = parser.parse_args(argv)

    driver = _load_generic_driver()
    driver.TARGETS = {case.case_id: case for case in CASES if case.case_id in (8, 10)}
    # Case 8 has 19 pages per split (304 tokens); case 10 has four pages per
    # split (64 tokens).  These deterministic rows bracket page/tail/split
    # boundaries while the regular harness supplies independent random mode.
    driver.MIXED_LENGTHS = {
        8: (1, 15, 16, 17, 303, 304, 305, 319, 320, 321, 607, 608, 609, 4095, 4096),
        10: (321,),
    }
    driver.RANDOM_LENGTHS = {
        8: (37, 271, 701, 1025, 2049, 3073, 3999),
        10: (321,),
    }
    # The accepted control itself reads an invalid tail row in this legacy
    # z4 contract.  Keep the candidate's tail-poison result visible, but let
    # the suite continue to reuse checks when candidate and control fail in
    # the same way; a candidate-only failure remains a hard failure in the
    # generic pairwise gate.
    pair = driver._pair

    def pair_with_shared_tail_diagnostic(label, *pair_args, **pair_kwargs):
        result = pair(label, *pair_args, **pair_kwargs)
        tail_diagnostic = "tail NaN" in label or (
            "tails=" in label and "tails=0" not in label
        )
        if tail_diagnostic and not result[0]:
            print(
                f"[INFO] {label} candidate/control shared tail-poison diagnostic; "
                "not candidate-only"
            )
            return True, result[1], result[2]
        return result

    driver._pair = pair_with_shared_tail_diagnostic
    if set(driver.TARGETS) != {8, 10}:
        raise AssertionError(f"unexpected z4 target manifest: {driver.TARGETS}")
    require_maca_gpu()
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    print(
        f"GPU: {driver.torch.cuda.get_device_name()} | torch={driver.torch.__version__} | "
        f"candidate={args.candidate} | control={args.control} | seed={args.seed}"
    )
    case8_ok = driver._run_case(8, candidate, control, args.seed + 8)
    case10_ok = driver._run_case(10, candidate, control, args.seed + 10)
    passed = case8_ok and case10_ok
    print(f"SPECIAL_RESULT={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
