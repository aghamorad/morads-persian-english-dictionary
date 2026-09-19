# Morad's Persian–English Dictionary

**A practical Persian-to-English dictionary for Kindle.**

Persian Kindle dictionaries are surprisingly difficult to find in a form that
works reliably with real Persian writing. Exact-match lookup can fail when a
reader uses Arabic rather than Persian letter forms, writes a suffix with or
without a zero-width non-joiner, joins a clitic to its word, or includes an
ezāfeh mark. This project packages a substantial Persian–English dictionary as
a proper Kindle dictionary and adds lookup aliases for those everyday writing
differences.

The goal is simple: make Persian reading on Kindle less fragile. Select a
Persian word as it appears on the page and get an English definition, even when
the spelling convention is not identical to the dictionary headword.

The dictionary contains 53,055 entries and more than one million indexed lookup
terms. It is built from the Persian–English pack supplied by Dictionaries.app,
whose metadata identifies the underlying entries as compiled from Wiktionary
under CC BY-SA 3.0.

The build preserves the original entry HTML and adds lookup aliases for common
Persian text differences: Arabic/Persian letter variants, zero-width joiner
and non-joiner differences, spacing differences, and common attached
conjunctions/clitics. It does not silently claim that every inflected form is
semantically identical; aliases point to the base entry so the original
dictionary text remains visible.

## What this release handles

- Persian and Arabic keyboard letter variants, such as `ک/ك` and `ی/ي`
- Joined, spaced, and zero-width-non-joiner forms
- Common attached forms such as `کتابها`, `کتاب‌ها`, and possessive endings
- Common `می‌/می` and `نمی‌/نمی` spacing variants
- Ezāfeh written with a kasra or common typed alternatives
- Kindle's dictionary lookup index, rather than an ordinary ebook word search

## Installing on Kindle

Download `build/Morads-Persian-English-Dictionary.mobi` from this repository and
copy it to the Kindle's `documents` folder over USB. On the Kindle, set it as
the primary dictionary for Persian if the device offers that language setting.

This is a community release, not an official Amazon dictionary. It is intended
to be useful and expandable: corrections, missing headwords, and better
examples can be added in future versions.

The Apple pack remains on the Mac in:

`~/Library/Application Support/io.dictionaries.Dictionaries/Packs/fa.langpack`

No files in the installed app are modified.

## Release files

- `build/Morads-Persian-English-Dictionary.mobi` — the finished Kindle dictionary
- `build/cover.png` — the front cover
- `extract_apple.py` — Apple Dictionary data extractor
- `make_source.py` — Kindle source and alias generator

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for provenance and licence details.
