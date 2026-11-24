#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
NAME="Morad's Persian-English Dictionary"
BUILD="$ROOT/build"
DDK="$BUILD/ddk"
OBJ="$BUILD/objects"
DIST="$ROOT/dist"

if [[ "$(uname -s)" != Darwin ]]; then
  echo 'ERROR: Apple Dictionary bundles must be compiled on macOS.' >&2
  exit 2
fi
for c in python3 git xmllint plutil ditto zip shasum; do
  command -v "$c" >/dev/null || { echo "Missing $c. Try xcode-select --install." >&2; exit 2; }
done
mkdir -p "$BUILD" "$DIST"

# The native .dictionary is built from the published web data shards, so the
# native bundle and the browser edition always index the same lookup terms.
if [[ ! -d "$BUILD/webdata/data/entries" ]]; then
  echo 'ERROR: build/webdata missing. Run export_web.py (or place the published web shards) first.' >&2
  exit 2
fi

echo 'Generating Apple Dictionary XML from the published web shards...'
python3 export_apple.py \
  --entries "$BUILD/webdata/data/entries" \
  --index "$BUILD/webdata/data/index" \
  --out "$BUILD/ddksrc" --version "${VERSION:-1.3.0}"

xmllint --noout "$BUILD/ddksrc/Morads-Dictionary.xml"
plutil -lint "$BUILD/ddksrc/Morads.plist"

if [[ ! -x "$DDK/bin/build_dict.sh" ]]; then
  echo 'Fetching Apple Dictionary Development Kit mirror...'
  git clone --depth 1 'https://github.com/ikey4u/macddk.git' "$DDK"
fi
export DICT_DEV_KIT_OBJ_DIR="$OBJ"
rm -rf "$OBJ"
echo 'Compiling native macOS dictionary (Apple DDK)...'
sh "$DDK/bin/build_dict.sh" -v 10.11 "$NAME" \
  "$BUILD/ddksrc/Morads-Dictionary.xml" "$BUILD/ddksrc/Morads.css" "$BUILD/ddksrc/Morads.plist"

BUNDLE="$OBJ/$NAME.dictionary"
test -d "$BUNDLE" || { echo "ERROR: DDK did not create $BUNDLE" >&2; exit 1; }
for artifact in Body.data KeyText.index EntryID.index; do
  find "$BUNDLE" -name "$artifact" -type f -print -quit | grep -q . || {
    echo "ERROR: Compiled bundle is missing $artifact" >&2; exit 1;
  }
done
rm -rf "$DIST/$NAME.dictionary"
ditto "$BUNDLE" "$DIST/$NAME.dictionary"
(
  cd "$DIST"
  rm -f "$NAME.dictionary.zip"
  ditto -c -k --sequesterRsrc --keepParent "$NAME.dictionary" "$NAME.dictionary.zip"
  shasum -a 256 "$NAME.dictionary.zip" > SHA256SUMS.txt
)
echo "SUCCESS: $DIST/$NAME.dictionary.zip"
if [[ "${INSTALL:-0}" == 1 ]]; then
  DEST="$HOME/Library/Dictionaries/$NAME.dictionary"
  mkdir -p "$HOME/Library/Dictionaries"
  if [[ -e "$DEST" ]]; then
    mv "$DEST" "$DEST.backup.$(date +%Y%m%d-%H%M%S)"
  fi
  ditto "$DIST/$NAME.dictionary" "$DEST"
  touch "$HOME/Library/Dictionaries"
  open -a Dictionary
  echo "Installed to $DEST. Open Dictionary > Settings and enable \"$NAME\"."
fi