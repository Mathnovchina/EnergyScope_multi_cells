"""Baseline integrity check — Step 3 of diagnostics phase."""
import json, hashlib, os, re
import pandas as pd

print("=" * 60)
print("  FROZEN BASELINE INTEGRITY CHECK")
print("=" * 60)

# CHECK 1: Frozen baseline run folder still valid
print("\n=== CHECK 1: Frozen baseline run folder ===")
meta_path = "case_studies/FI/manual_runs/20260310_095416__stageA_verify/run_metadata.json"
with open(meta_path) as f:
    m = json.load(f)
code = m["solve_info"]["code"]
score = m["score"]
status = m["solve_info"]["status"]
print(f"  Run: stageA_verify")
print(f"  code={code}, status={status}, score={score}")
assert code == 0, f"FAIL: code is {code}"
assert status == "OK", f"FAIL: status is {status}"
# Check outputs exist
out_dir = "case_studies/FI/manual_runs/20260310_095416__stageA_verify/outputs"
assert os.path.isdir(out_dir), "FAIL: outputs/ directory missing"
# Check .dat snapshot exists
snap_dir = "case_studies/FI/manual_runs/20260310_095416__stageA_verify/input_snapshot"
assert os.path.isdir(snap_dir), "FAIL: input_snapshot/ directory missing"
assert os.path.exists(os.path.join(snap_dir, "reg_technologies.dat")), "FAIL: reg_technologies.dat missing"
print("  CHECK 1: PASS")

# CHECK 2: Frozen backup matches baseline notes
print("\n=== CHECK 2: Frozen baseline file integrity ===")
frozen = "Data/2017/FI/Technologies.csv.frozen_baseline_20260310"
current = "Data/2017/FI/Technologies.csv"
h_frozen = hashlib.md5(open(frozen, "rb").read()).hexdigest()
h_current = hashlib.md5(open(current, "rb").read()).hexdigest()
sz_frozen = os.path.getsize(frozen)
sz_current = os.path.getsize(current)
print(f"  Frozen backup: {sz_frozen} bytes, md5={h_frozen}")
print(f"  Current file:  {sz_current} bytes, md5={h_current}")
# Expected from baseline_notes.md: 426 bytes, md5=cf915a9e5487e0ea1d6c0aaa584470f9
expected_md5 = "cf915a9e5487e0ea1d6c0aaa584470f9"
assert h_frozen == expected_md5, f"FAIL: frozen md5={h_frozen}, expected {expected_md5}"
assert sz_frozen == 426, f"FAIL: frozen size={sz_frozen}, expected 426"
assert h_frozen == h_current, f"FAIL: current file differs from frozen backup"
df = pd.read_csv(current, encoding="utf-8-sig")
print(f"  Content: {len(df)} rows")
assert len(df) == 20, f"FAIL: expected 20 rows, got {len(df)}"
print(f"  MD5 matches baseline_notes.md: {expected_md5}")
print("  CHECK 2: PASS")

# CHECK 3: Stage A disabling is correct in run script
print("\n=== CHECK 3: Stage A disabling in run_calib_manual.py ===")
with open("scripts/run_calib_manual.py") as f:
    src = f.read()

# Check list exists and has 34 techs
assert "DISABLED_TECH_STAGE_A" in src, "FAIL: DISABLED_TECH_STAGE_A not found"
list_block = src.split("DISABLED_TECH_STAGE_A = [")[1].split("]")[0]
techs = re.findall(r'"([A-Z][A-Z0-9_]+)"', list_block)
print(f"  DISABLED_TECH_STAGE_A: {len(techs)} technologies")
assert len(techs) == 34, f"FAIL: expected 34, got {len(techs)}"

# Check function is called
assert "apply_fi2017_disabling(my_model)" in src, "FAIL: apply_fi2017_disabling not called"
print("  apply_fi2017_disabling() called in main: YES")

# Check fmin_perc/fmax_perc handling
func_body = src.split("def apply_fi2017_disabling")[1].split("\ndef ")[0]
assert "fmin_perc" in func_body, "FAIL: fmin_perc not zeroed"
assert "fmax_perc" in func_body, "FAIL: fmax_perc not zeroed"
print("  fmin_perc/fmax_perc zeroed in disabling: YES")

# Check constraint diff function exists
assert "def generate_constraint_diff" in src, "FAIL: generate_constraint_diff not found"
print("  generate_constraint_diff() present: YES")

# Check infeasibility diagnostics function exists
assert "def _build_infeasibility_diagnostics" in src, "FAIL: diagnostics not found"
print("  _build_infeasibility_diagnostics() present: YES")

print("  CHECK 3: PASS")

print("\n" + "=" * 60)
print("  ALL CHECKS PASSED")
print("=" * 60)
