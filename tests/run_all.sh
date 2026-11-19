#!/usr/bin/env bash
# Führt alle Browser-Tests aus / runs all browser tests.  Voraussetzung / requires: pip install -r tests/requirements.txt
set -u
cd "$(dirname "$0")"
fail=0
for t in t1_rig t2_edit t3_play t4_more t5_sync t6_mobile t8_robust t9_i18n t10_audio t11_music t12_motion t13_bubbles t14_women; do
  echo "=== $t"
  out=$(python3 "$t.py" 2>&1); echo "$out" | tail -4
  echo "$out" | grep -q "^FAILS: \[\]" || { echo "!!! $t has failures"; fail=1; }
done
exit $fail
