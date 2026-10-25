#!/usr/bin/env bash
# =============================================================================
#  IONITY GLOBAL / AEDI  ::  terminal intro
#  Author: Johan Wilhelm van Antwerp | Ionity (Pty) Ltd | Policy 986 AED
#  (c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
#  usage: ./ionity-intro.sh [60|100|160]
# =============================================================================
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLS="${1:-100}"
ART="$HERE/../logos/ionity-global-logo-${COLS}col.ans"
clear
[ -f "$HERE/../banners/ionity-global-banner.ans" ] && cat "$HERE/../banners/ionity-global-banner.ans"
echo
[ -f "$ART" ] && cat "$ART" || cat "$HERE/../logos/ionity-global-logo-100col.ans"
echo
printf '\033[38;5;51m  Building Tomorrow, Today.\033[0m   \033[38;5;245mAnything is Possible with God.\033[0m\n'
printf '\033[38;5;245m  www.ionity.today · Policy 986 AED · TM2\033[0m\n'
