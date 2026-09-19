# Morad's Persian–English Dictionary

This project converts the installed Dictionaries.app Persian–English pack into
a sideloadable Kindle dictionary. The pack identifies itself as 53,055 entries
compiled from Wiktionary and licensed under CC BY-SA 3.0.

The build preserves the original entry HTML and adds lookup aliases for common
Persian text differences: Arabic/Persian letter variants, zero-width joiner
and non-joiner differences, spacing differences, and common attached
conjunctions/clitics. It does not silently claim that every inflected form is
semantically identical; aliases point to the base entry so the original
dictionary text remains visible.

The Apple pack remains on the Mac in:

`~/Library/Application Support/io.dictionaries.Dictionaries/Packs/fa.langpack`

No files in the installed app are modified.

## Release files

- `build/Morads-Persian-English-Dictionary.mobi` — the finished Kindle dictionary
- `build/cover.png` — the front cover
- `extract_apple.py` — Apple Dictionary data extractor
- `make_source.py` — Kindle source and alias generator

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for provenance and licence details.
