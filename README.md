# Morad's Persian–English Dictionary

[![Latest release](https://img.shields.io/github/v/release/aghamorad/morads-persian-english-dictionary)](https://github.com/aghamorad/morads-persian-english-dictionary/releases/latest)

A Persian → English lookup dictionary for Kindle, built for Persian as it is actually written.

**53,055 entries, indexed under 1,019,648 lookup terms.**

**[Download the latest release →](https://github.com/aghamorad/morads-persian-english-dictionary/releases/latest)**

![Cover](build/cover.png)

---

## Why this exists

Kindle's dictionary lookup is an exact string match. You tap a word, the device asks its index for that exact label, and if the label is not there, the definition panel comes up empty. Persian does not cooperate with this, because the way a word appears on the page is often not the way it appears in a dictionary:

| On the page | What is different | Headword in the index |
|---|---|---|
| `كتاب` | Arabic kaf (U+0643) instead of Persian ک | `کتاب` |
| `آبانبار` | zero-width non-joiner dropped | `آبانبار` |
| `آتش بازی` | zero-width non-joiner typed as a space | `آتشبازی` |
| `کتابها` | plural clitic joined to the stem | `کتاب` |
| `میرود` | `می` progressive prefix joined | `میرود` |
| `کتابِ` | ezāfeh written as a trailing kasra | `کتاب` |

Each of these is a miss. In practice it means selecting an ordinary Persian word and getting nothing back.

This project takes a Persian–English dictionary compiled from [Wiktionary](https://www.wiktionary.org/) and repackages it as a proper Kindle dictionary, indexing it under those spellings as well. Every alias resolves to the real entry, so the definition you see is always the dictionary's own text. Nothing is fabricated and no inflected form is claimed to mean something it does not.

## What is in the release

| | |
|---|---|
| Headwords | 53,055 |
| Indexed lookup terms | 1,019,648 |
| Direction | Persian → English |
| Format | MOBI (Mobipocket 7), dictionary-indexed |
| File size | 33 MB |
| Source data | Wiktionary, Persian–English, CC BY-SA 3.0 |
| Licence | CC BY-SA 3.0 — see [LICENSE-NOTICE.md](LICENSE-NOTICE.md) |

This is a community release, not an Amazon dictionary.

## Installing on a Kindle

1. Download `Morads-Persian-English-Dictionary.mobi` from the [Releases page](https://github.com/aghamorad/morads-persian-english-dictionary/releases/latest).
2. Connect the Kindle over USB. It mounts as a drive.
3. Copy the file into the `documents` folder. Some models also accept a `documents/dictionaries` subfolder.
4. Eject the Kindle, then disconnect.
5. Select it as your Persian dictionary (below).

**Use USB, not Send to Kindle.** Dictionary lookup depends on a MOBI index that survives a direct file copy. Send to Kindle re-converts whatever you send it, and the index does not survive that trip — the file arrives as an ordinary book that cannot be selected as a dictionary.

### Selecting it on the device

Open **Settings → Language & Dictionaries → Dictionaries**. If the device lists Persian or فارسی, choose *Morad's Persian–English Dictionary* there.

Many Kindle models do not offer Persian in that list, because the set of selectable dictionary languages is fixed by the firmware. If Persian is not offered, you can still reach the dictionary while reading: open a Persian book, tap a word, then tap the dictionary name shown at the bottom of the definition panel and pick this one from the list of installed dictionaries.

Menu wording varies by model and firmware version. Verified working on a sideloaded Kindle.

## Lookup coverage

Every row below was checked against the built file with `kindling-cli lookup`, which simulates the on-device index search.

**Resolves:**

| Tapped word | Form |
|---|---|
| `آب` | plain headword |
| `کتاب` | plain headword |
| `كتاب` | Arabic kaf — opens the same entry as `کتاب` |
| `آبانبار` | ZWNJ dropped |
| `آتش بازی` | ZWNJ written as a space |
| `میرود` | `می` prefix joined, no ZWNJ |
| `نمیدانم` | `نمی` prefix joined, no ZWNJ |
| `کتابها` `کتابها` | plural, joined and with ZWNJ |
| `خانهام` | possessive ending attached to a word ending in ه |
| `کتابِ` | ezāfeh as a trailing kasra |
| `کتاب-e` | ezāfeh as a Latin transliteration tail |

**Does not resolve yet** (see below):

| Tapped word | Form |
|---|---|
| `خانۀ` `نامۀ` `بچۀ` | ezāfeh as the hamza ligature U+06C0 |
| `خانهٔ` | ezāfeh as heh + combining hamza above (U+0654) |
| `کتابى` `ايرانى` | word-final Arabic alef maqsura (U+0649) |

## Known limitations

- **Ezāfeh on a word ending in ه.** The generator adds ezāfeh aliases as a trailing kasra and as `-e`, but not as the `ۀ` ligature or the `هٔ` sequence. A text that writes `خانۀ من` will not open `خانه`.
- **Alef maqsura.** Word-final `ى` (U+0649) is not aliased, though the ordinary Arabic yeh `ي` (U+064A) is.
- **Registered as Persian-input.** The file declares `DictionaryInLanguage` as `fa`, so the Kindle offers it for Persian text. The source pack is in fact partly bidirectional — about 25,760 of the headwords are English — but those entries are unreachable as a lookup dictionary because the file is not declared English-input. There is no pronunciation or audio.
- **Aliases are spelling variants, not grammar.** A joined clitic points at the stem entry; the definition is the stem's, not a separate gloss for the inflected form.
- **Not a KFX or AZW3 dictionary.** Kindle's lookup popup reads the MOBI7 index format, so this is built as MOBI and is intended for USB sideloading.

## Rebuilding from source

The build needs a Persian–English dictionary in Apple Dictionary format, and `kindling` (version 0.45.5), the MOBI builder used here. The `kindling-cli` binary is not committed to this repository — put it in `tools/` before running step 3.

Point step 1 at the `Body.data` file inside the bundle's `Contents/Resources/`. It holds the entries in Apple's compressed chunk format, which is what `extract_apple.py` unpacks.

```bash
PACK="/path/to/persian-english.dictionary/Contents/Resources"

# 1. Unpack the compressed Body.data into dictionary XML
python3 extract_apple.py "$PACK/Body.data" build/apple-fa.xml

# 2. Convert entries to Kindle source and generate spelling aliases
python3 make_source.py build/apple-fa.xml build/source

# 3. Build the MOBI
./tools/kindling-cli build build/source/content.opf \
  -o build/Morads-Persian-English-Dictionary.mobi
```

Two helper subcommands are useful when checking a build:

```bash
./tools/kindling-cli validate build/source/content.opf          # Kindle Publishing Guidelines pre-flight
./tools/kindling-cli lookup build/Morads-Persian-English-Dictionary.mobi کتاب
```

`validate` reports the expected findings for a dictionary: no NCX or logical TOC, and the `<script>` elements inherited from the original entry HTML, which Kindle ignores in a dictionary index.

## Repository layout

```
extract_apple.py     unpack Apple's Body.data into entry XML
make_source.py       build Kindle dictionary HTML and generate lookup aliases
build/cover.png      cover artwork
build/source/        generated Kindle source (OPF, HTML, CSS, cover)
LICENSE-NOTICE.md    provenance and licence
```

`build/apple-fa.xml` and `build/source/` are generated and are not tracked; `build/Persian-English-Dictionary.mobi` is a superseded earlier build.

## Licence and provenance

The dictionary entries are compiled from **Wiktionary** and carry the **CC BY-SA 3.0** licence that Wiktionary's content is published under. That attribution and licence basis are preserved here. The lookup aliases, Kindle packaging, build scripts, and cover artwork are Morad Moazami's contribution to this release.

- Wiktionary — https://www.wiktionary.org/
- CC BY-SA 3.0 — https://creativecommons.org/licenses/by-sa/3.0/

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for the full notice.
