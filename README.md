# Morad's Persian–English Dictionary

[![Latest release](https://img.shields.io/github/v/release/aghamorad/morads-persian-english-dictionary)](https://github.com/aghamorad/morads-persian-english-dictionary/releases/latest)

A Persian → English lookup dictionary for Kindle, built from three reusable lexical sources and indexed for Persian as it is actually written.

**79,511 canonical entries, indexed under 737,619 unique lookup terms.**

**[Download the latest release →](https://github.com/aghamorad/morads-persian-english-dictionary/releases/latest)**

![Cover](build/cover.png)

## What is in the release

| | |
|---|---|
| Canonical entries | 79,511 |
| Indexed lookup terms | 737,619 |
| Direction | Persian → English |
| Format | MOBI7 Kindle dictionary |
| File size | 29,020,005 bytes |
| Required lookup tests | 14/14 passing |
| Build date | September 19, 2026 |

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

Kindling's final MOBI self-check reports **18 P0 checks passed and 0 P1 warnings**.

## Installing on a Kindle

1. Download `Morads-Persian-English-Dictionary.mobi` from the Releases page.
2. Connect the Kindle over USB.
3. Copy the file into the Kindle's `documents` folder.
4. Eject the Kindle and disconnect it.
5. Open **Settings → Language & Dictionaries → Dictionaries** and select it for Persian if your firmware exposes Persian there.

Use USB rather than Send to Kindle. Amazon's conversion service can strip the MOBI dictionary index and turn the file into an ordinary book.

Some Kindle firmware does not list Persian as a selectable default dictionary language. In that case, open a Persian book, tap a word, tap the dictionary name in the lookup panel, and choose this installed dictionary manually.

## Rebuilding

Requirements:

- Python 3.11 or newer;
- `kindling-cli` v0.45.5 in `tools/`;
- approximately 120 MB for pinned source snapshots.

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

This is a community release, not an Amazon dictionary.
