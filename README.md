# Morad's Persian–English Dictionary

[![Latest release](https://img.shields.io/github/v/release/aghamorad/morads-persian-english-dictionary)](https://github.com/aghamorad/morads-persian-english-dictionary/releases/latest)

A Persian → English lookup dictionary for Kindle, built from three reusable lexical sources and indexed for Persian as it is actually written.

**79,511 canonical entries, indexed under 920,512 unique lookup terms.**

**[Download the latest release →](https://github.com/aghamorad/morads-persian-english-dictionary/releases/latest)**

![Cover](build/cover.png)

## What is in the release

| | |
|---|---|
| Version | 1.1.0 |
| Canonical entries | 79,511 |
| Indexed lookup terms | 920,512 |
| Direction | Persian → English |
| Format | MOBI7 Kindle dictionary |
| File size | 34,606,581 bytes |
| Required lookup tests | 23/23 passing |
| Build date | September 21, 2026 |

The entries are merged by Kindle-equivalent Persian spelling, so Arabic/Persian character variants, combining marks, and zero-width non-joiners do not create competing duplicate entries.

## Sources

The release combines three explicitly reusable sources. Their counts overlap and therefore do not add up to the final entry count.

| Source | Entries contributing definitions | Licence | Role |
|---|---:|---|---|
| HMT Persian–English Apple Dictionary | 41,433 | MIT | Broad Persian headword coverage and concise English glosses |
| English Wiktionary via Kaikki | 17,378 | CC BY-SA 4.0 / GFDL | Human-edited senses, parts of speech, and recorded inflected forms |
| Dehkhoda-Lexicon by Maani | 40,768 | CC BY-SA 4.0 | Rare vocabulary, synonyms, and English translations derived from Dehkhoda |

Every displayed definition is labelled by source. Dehkhoda-Lexicon's English translations were produced through a human/AI-assisted process; they are presented as that dataset's translations, not as original English text written by Ali-Akbar Dehkhoda.

Exact source URLs, byte sizes, retrieval date, and SHA-256 checksums are pinned in [`sources.lock.json`](sources.lock.json). The installed HMT `Body.data` used for this build is byte-for-byte identical to the MIT-licensed public repository artifact.

See [`LICENSE-NOTICE.md`](LICENSE-NOTICE.md) for complete attribution and licence terms.

## Lookup design

Kindle's Persian index treats some characters as zero-weight while storing others literally. Naively indexing every spelling can disorder the index and make forms unreachable even when they are present.

This build therefore:

- keeps one canonical entry for Kindle-equivalent spellings;
- stores connected index labels instead of literal ZWNJ duplicates;
- uses real inflected forms recorded by Wiktionary where available;
- adds conservative attachment aliases for plurals, possessives, and adjectival forms;
- adds the plural indefinite (`کتاب‌هایی`), the plural carrying a singular possessive (`کتاب‌هایم`, `کتاب‌هایت`, `کتاب‌هایش`), and the space-separated indefinite after a silent heh (`خانه ای`), which is a separate on-device label because the device folds ZWNJ away before searching but does not fold a space;
- adds Arabic kaf/yeh, final alef maqsura, and ezāfeh variants;
- refuses an alias only when it would be the same lookup string as another canonical headword, so recorded alternative spellings such as `مسأله` stay reachable alongside their folded forms;
- converts imported HMT markup to escaped text, eliminating malformed source HTML and broken cross-links.

## Verified lookups

The following all resolve in the published candidate using `kindling-cli lookup`:

| Query | Coverage |
|---|---|
| `هنگفت` | formerly missing HMT headword |
| `هنگفتی` | attached `ی` |
| `ممتحن` | formerly missing HMT headword |
| `گفت` `رفت` `خورد` `اقتدار` | ordinary source words |
| `کتاب` | standard Persian spelling |
| `كتاب` | Arabic kaf |
| `خانۀ` | ezāfeh ligature U+06C0 |
| `خانهٔ` | combining hamza above U+0654 |
| `کتابی` | attached `ی` |
| `کتاب‌ها` | ZWNJ plural |
| `فارسى` | final Arabic alef maqsura U+0649 |
| `کتاب‌هایی` `روزهایی` `خانه‌هایی` `مشکل‌هایی` | plural indefinite `-هایی` |
| `کتاب‌هایم` `کتاب‌هایت` `کتاب‌هایش` | plural with a singular possessive |
| `خانه ای` `جلسه ای` | space-separated indefinite after a silent heh |

Kindling's final MOBI self-check reports **18 P0 checks passed and 0 P1 warnings**.

## Browser edition for macOS, Windows, Android and iPhone

The same sourced lexicon can now be exported as a **static browser dictionary**, with no central lookup server, API subscription, or account required. It provides a responsive Persian search field, exact matches, spelling normalization, prefix suggestions, distinct source definitions, and one-click saving of the full data for offline use in a modern browser. It also includes a web app manifest and service worker, so users can add it to their home screen where supported.

The cross-platform exporter, browser application, source updates and editorial candidate vocabulary were merged into `main` on November 16, 2026. GitHub Actions now builds and deploys the browser edition. The statistics and Kindle download above still describe the existing 1.1.0 Kindle release; the MOBI itself has not yet been rebuilt or replaced.

The deployment workflow builds and tests the site on every push. If GitHub Pages is enabled, it deploys automatically. If Pages is not yet enabled or the workflow token cannot access its settings, the build still succeeds and uploads the complete site as a `persian-dictionary-web` Actions artifact; deployment is skipped rather than failing. To publish, open **Settings → Pages → Build and deployment → Source: GitHub Actions**, save, then rerun the workflow or push a later commit. Do not advertise a live URL until a deployment run succeeds.

### Installing the browser edition

The browser edition is a Progressive Web App (PWA). It uses the same dictionary data on desktop and mobile:

- **macOS (Safari 17 / macOS Sonoma 14 or newer):** open the published dictionary in Safari, choose **File → Add to Dock**, and launch it from the Dock like an app. In Chrome, use the install icon in the address bar or the browser menu's **Install app** command.
- **Windows:** open it in Chrome or Edge and choose **Install** from the address bar or browser menu. It then opens in its own app window.
- **Android:** open it in Chrome, choose **Install app** or **Add to Home screen**, and launch it from the home screen. On browsers that support PWA share targets, you can also share selected text to the installed dictionary.
- **iPhone and iPad:** open it in Safari, tap **Share → Add to Home Screen**, then launch the saved icon. Search works inside the app; iOS does not provide the Android-style share-target integration here.

On every platform, open the app once while online and press **Save for offline use**. Wait for the confirmation before disconnecting. This downloads the full lookup index and definitions into that browser's local storage. Browser storage can still be cleared by the user or the operating system.

This is a browser-based lookup app, not a native macOS Dictionary.app dictionary, Windows system dictionary, or system-wide text-selection service. It requires no account, subscription, lookup API, or always-on dictionary server.

To build the web edition locally (after running fetch_sources.py):

```bash
python export_web.py \
  --hmt-body data/hmt-body.data \
  --dehkhoda data/dehkhoda-lexicon.json \
  --kaikki data/kaikki-persian.jsonl \
  --cover build/cover.png --out site
python -m http.server --directory site 8000
```

Open http://localhost:8000. The browser downloads only the needed first-letter lookup shard and definition shard for ordinary queries. The offline button explicitly caches the whole dictionary, subject to device storage limits.

### New editorial vocabulary and quality

- New candidate idioms, slang, rude expressions, and conversational terms are maintained in lexicon/idioms.json, labelled **Editorial** to distinguish them from sourced lexicons.
- Wiktionary sense labels such as *archaic*, *rare*, *literary*, *figurative*, *colloquial*, and *vulgar* are now retained when supplied by the input data.
- Editorial senses are **not independently lexicographically reviewed**. Do not treat their proposed definitions as authoritative until they have been audited. See CONTRIBUTING.md.
- HMT and Dehkhoda retain their existing verified snapshots. Kaikki was refreshed to the October 2026 Wiktionary extraction on November 16, with the exact new SHA-256 and byte size pinned in sources.lock.json. Full-export verification checks the merged dataset.
- Some generated inflected forms may still be linguistically unnatural. Lookup aliases must always be distinguished from independent sourced definitions.


## Installing on a Kindle

1. Download `Morads-Persian-English-Dictionary.mobi` from the Releases page.
2. Connect the Kindle over USB.
3. Copy the file into the Kindle's `documents` folder.
4. Eject the Kindle and disconnect it.
5. Open **Settings → Language & Dictionaries → Dictionaries** and select it for Persian if your firmware exposes Persian there.

Use USB rather than Send to Kindle. Amazon's conversion service can strip the MOBI dictionary index and turn the file into an ordinary book.

Some Kindle firmware does not list Persian as a selectable default dictionary language. In that case, open a Persian book, tap a word, tap the dictionary name in the lookup panel, and choose this installed dictionary manually.

## Keeping it current

A Kindle cannot tell you that a newer dictionary exists. There is no popup, no in-app notice, and no update check — a lookup panel shows whatever `.mobi` was last copied onto the device, forever, until you replace it.

So the version number in the table above is the whole mechanism. The badge at the top of this page and the download link both track the newest release. Compare that number against the build on your Kindle, and if yours is older, download the file again and follow the install steps with it. Replacing `Morads-Persian-English-Dictionary.mobi` in `documents` is the entire update; there is nothing to uninstall first.

The number changes only when the built dictionary changes, so a newer number is always the signal to re-download.

## Rebuilding

Requirements:

- Python 3.11 or newer;
- `kindling-cli` v0.45.5 in `tools/`;
- approximately 120 MB for pinned source snapshots.

For a Linux rebuild, install the exact CI compiler first:

```bash
mkdir -p tools
curl -fL https://github.com/ciscoriordan/kindling/releases/download/v0.46.2/kindling-cli-linux -o tools/kindling-cli
echo 'b61c883104c1f139313992d72e87e7c61617c31e59f5fe84748451b5cc6b11b0  tools/kindling-cli' | sha256sum -c -
chmod +x tools/kindling-cli
```

The upstream project also publishes native Apple Silicon and Intel macOS binaries. The release workflow uses the pinned Linux binary above so builds are reproducible.

Download and checksum the exact source snapshots:

```bash
python3 fetch_sources.py
```

Generate strictly escaped Kindle source:

```bash
python3 make_source.py \
  --hmt-body data/hmt-body.data \
  --dehkhoda data/dehkhoda-lexicon.json \
  --kaikki data/kaikki-persian.jsonl \
  --cover build/cover.png \
  --out build/source
```

Validate and build:

```bash
./tools/kindling-cli validate build/source/content.opf
./tools/kindling-cli build build/source/content.opf \
  -o build/Morads-Persian-English-Dictionary.mobi
```

Verify the required lookup suite and print the release checksum:

```bash
python3 verify_build.py build/Morads-Persian-English-Dictionary.mobi
```

## Repository layout

```text
extract_apple.py    decode Apple Dictionary Body.data chunks correctly
fetch_sources.py    download and checksum the pinned source snapshots
make_source.py      merge sources and generate Kindle-safe XHTML/OPF/NCX
verify_build.py     run the required Kindle lookup suite
sources.lock.json   source URLs, licences, byte sizes, and SHA-256 hashes
build/cover.png     cover artwork
build/source/       generated source, ignored by Git
data/               downloaded source snapshots, ignored by Git
LICENSE-NOTICE.md   attribution and redistribution terms
```

## Limitations

- The lookup simulator and MOBI structural checks pass, but final behavior should still be confirmed on physical Kindle hardware.
- Source glosses can disagree or reflect different senses; source labels are retained so readers can distinguish them.
- There is no pronunciation audio.
- The release is intended for USB sideloading as a MOBI dictionary, not as KFX or a Send to Kindle conversion.
- Arabic sound plurals are not generated mechanically. A rule attaching `-ین` or `-ات` to every consonant-final stem would produce junk (`مشکلین`, `کتابات`) alongside the real forms, so entries such as `ملاحظات`, `مهندسین`, `مورخین`, and `بازرسین` resolve only where a source records them. Several that do (`مورخان`, `معلمین`, `مشکلات`, `حوادث`) are covered.
- The plural possessive series stops at the singular (`کتاب‌هایم`, `کتاب‌هایت`, `کتاب‌هایش`). The `-هایمان`, `-هایتان`, `-هایشان` forms were measured at roughly 4 MB of index for forms rarely typed, and were left out.

This is a community release, not an Amazon dictionary.
