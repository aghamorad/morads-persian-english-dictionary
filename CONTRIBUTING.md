# Contributing Persian entries

The goal is comprehensive *and reliable* Persian–English lookup: literary and archaic terms, modern colloquial language, slang, regional language, and full idiomatic expressions. More entries alone do not establish quality.

## Adding a term

Edit lexicon/idioms.json. A record contains a Persian headword, a part of speech, and an array of English senses. Each sense must have a distinct gloss and appropriate register labels. For example:

    {
      "word": "دبه درآوردن",
      "pos": "verb",
      "senses": [
        {"gloss": "to back out of an agreement or change the agreed terms", "labels": ["colloquial"]}
      ]
    }

Optional variants (an array of Persian spellings) are indexed as aliases of the same entry.

- Separate distinct senses rather than flattening incompatible meanings.
- Translate the meaning of idioms, not just their constituent words.
- Do not treat Tehrani slang as universal across Persian varieties.
- Label vulgar, rude, archaic, rare, regional, and figurative senses accurately.
- Record spelling variants only when they refer to the same expression.
- Never fabricate a sense, example, etymology, or reference.
- Supply evidence for unusual, historical, dialectal or contested meanings in the pull request.
- Do not copy proprietary dictionary definitions without permission and compatible licensing.
- Avoid spurious automatically generated plurals and inflected words.

## Review status

The first editorial batch consists of **candidate definitions**, not independent lexicographic verification. Each is separately attributed as Editorial in the output and should receive Persian native-speaker editorial review before being presented as authoritative.

## Validation

Run python -m unittest discover -s tests -v. The tests cover Unicode spelling, register labels, aliases, cross-platform exports, and escaped Kindle markup. The validation suite is a baseline, not a replacement for sense-by-sense review.

Full upstream source data are checksum-pinned in sources.lock.json. Replacing a snapshot requires verifying its SHA-256 and byte size. See LICENSE-NOTICE.md for redistribution terms.
