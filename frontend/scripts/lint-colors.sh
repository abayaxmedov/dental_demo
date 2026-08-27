#!/usr/bin/env bash
# Off-brand rang literalini taqiqlaydi (ADR-004/012 — reskin uchun). Ruxsat: slate/gray/
# zinc/neutral/stone (neytral), amber (warning), red (danger), brand/accent (token).
set -e
PALETTE="orange|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose"
PREFIX="bg|text|border|ring|from|via|to|fill|stroke|outline|divide|shadow|caret|placeholder|decoration|ring-offset"
if grep -rEn "(${PREFIX})-(${PALETTE})-[0-9]" src/app src/components 2>/dev/null; then
  echo "✗ Off-brand rang literal topildi — token ishlating (bg-brand-600, text-accent-700)."
  exit 1
fi
# xom hex (globals.css dan tashqari)
if grep -rEn "#[0-9a-fA-F]{3,8}" src/app src/components --include="*.tsx" 2>/dev/null; then
  echo "✗ Xom hex rang topildi .tsx da — token ishlating."
  exit 1
fi
echo "✓ rang literallari toza"
