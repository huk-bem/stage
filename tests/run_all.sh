#!/usr/bin/env bash
# Führt alle Browser-Tests aus / runs all browser tests.  Voraussetzung / requires: pip install -r tests/requirements.txt
set -u
cd "$(dirname "$0")"
fail=0
for t in t1_rig t2_edit t3_play t4_more t5_sync t6_mobile t8_robust t9_i18n t10_audio t11_music t12_motion t13_bubbles t14_women t15_targets t16_media t17_project t18_overlay t19_export t20_playctl t21_scenes t22_translate t23_select_tight t24_flows; do
  echo "=== $t"
  if [ "$t" = "t19_export" ] && command -v xvfb-run >/dev/null 2>&1 && [ -z "${DISPLAY:-}" ]; then out=$(xvfb-run -a -s "-screen 0 1400x900x24" python3 "$t.py" 2>&1); else out=$(python3 "$t.py" 2>&1); fi; echo "$out" | tail -4
  echo "$out" | grep -q "^FAILS: \[\]" || { echo "!!! $t has failures"; fail=1; }
done
exit $fail
