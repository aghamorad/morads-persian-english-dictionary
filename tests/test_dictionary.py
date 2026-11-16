"""Small offline regression tests for lexical quality and browser export."""

import json
import tempfile
import unittest
from pathlib import Path

from export_web import export_site, shard_name
from make_source import (
    add_definition, get_entry, kindle_entry, load_editorial, load_kaikki,
    merge_key,
)


class DictionaryTests(unittest.TestCase):
    def test_persian_script_normalization(self):
        self.assertEqual(merge_key("كتاب"), merge_key("کتاب"))
        self.assertEqual(merge_key("خانهٔ"), merge_key("خانۀ"))
        self.assertEqual(merge_key("کتاب‌ها"), merge_key("کتابها"))

    def test_editorial_idioms_and_register(self):
        entries = {}
        load_editorial(Path(__file__).resolve().parents[1] / "lexicon/idioms.json", entries)
        self.assertGreaterEqual(len(entries), 60)
        slang = entries[merge_key("چس‌ناله")]
        self.assertTrue(any("vulgar" in text for text in slang.definitions["Editorial"]))
        proverb = entries[merge_key("نان به نرخ روز خوردن")]
        self.assertIn("نون به نرخ روز خوردن", proverb.forms)
        self.assertTrue(any("opportun" in text for text in proverb.definitions["Editorial"]))

    def test_wiktionary_labels_preserve_senses(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "kaikki.jsonl"
            path.write_text(json.dumps({
                "word": "فرضی", "pos": "adj",
                "senses": [
                    {"glosses": ["imaginary"], "tags": ["literary"]},
                    {"glosses": ["hypothetical"], "tags": ["formal"]},
                ],
            }, ensure_ascii=False) + "\n", encoding="utf-8")
            entries = {}
            load_kaikki(path, entries)
            senses = entries[merge_key("فرضی")].definitions["Wiktionary"]
            self.assertIn("[literary] imaginary", senses)
            self.assertIn("[formal] hypothetical", senses)

    def test_web_export_variants_and_filtered_owners(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            web = root / "web"
            web.mkdir()
            (web / "index.html").write_text("test", encoding="utf-8")
            cover = root / "cover.png"
            cover.write_bytes(b"test")
            entries = {}
            book = get_entry(entries, "کتاب", "Wiktionary")
            add_definition(book, "Wiktionary", "book")
            # A headword without definitions must not steal an inflection alias.
            get_entry(entries, "کتابی", "HMT")
            result = export_site(entries, root / "site", web, cover)
            self.assertEqual(result["entries"], 1)
            index = json.loads((root / "site/data/index" / (shard_name("ک") + ".json")).read_text(encoding="utf-8"))
            self.assertEqual(index["کتابی"], merge_key("کتاب"))
            self.assertEqual(index["کتاب"], merge_key("کتاب"))
            entry = json.loads((root / "site/data/entries" / (shard_name("ک") + ".json")).read_text(encoding="utf-8"))
            self.assertEqual(entry[merge_key("کتاب")]["sources"]["Wiktionary"], ["book"])

    def test_kindle_html_escaping(self):
        entries = {}
        entry = get_entry(entries, "نمونه", "Wiktionary")
        add_definition(entry, "Wiktionary", 'example & <script>alert("x")</script>')
        markup = kindle_entry(1, entry, [])
        self.assertNotIn("<script>", markup)
        self.assertIn("&lt;script&gt;", markup)


if __name__ == "__main__":
    unittest.main()
