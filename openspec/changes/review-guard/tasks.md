# Tasks: review-guard

## 1. Code

- [x] `_review_guard` after the review call: header restored, a review that
      adds a bound defect is rejected (`graph.py`).
- [x] Unit tests on the measured texts (`tests/unit/test_review_guard.py`).
- [x] `make check` green; snapshots unchanged.

## 2. Measure

- [x] Chapter 7 with M, three seeds: rejections and restorations counted
      (2026-11-16, `experiments/runs/20261116-review-guard/report.md`):
      entry-1 review rejected 3/3 (quotation + over 2 sentences each time),
      0 header restored; served entry 1 bounded on all three.
- [ ] Entry 1 read by the owner (closes `entry1-notebook-checks` task 3).
