"""Regression tests for Crownsmere's private-by-default property catalogue.

Run: python3 tools/test_properties.py
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from property_pages import allowed_image_path, build_properties, validate_published

def ready_row():
    return {
        "slug": "test-marylebone-apartment",
        "reference": "CME-TEST-001",
        "status": "published",
        "owner_authority": True,
        "compliance_cleared": True,
        "listing_type": "sale",
        "title": "Test Marylebone Apartment",
        "area": "Marylebone",
        "address_public": "Marylebone, London",
        "price": 1250000,
        "property_type": "Apartment",
        "bedrooms": 2,
        "bathrooms": 2,
        "description": "An entirely fictional test fixture.",
        "features": ["Test feature"],
        "photos": ["test.jpg"],
        "private_owner_email": "never-render-this@example.com"
    }

class PropertyBuildTest(unittest.TestCase):
    def setUp(self):
        self.work = TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        (self.root / "data").mkdir()
        self.pages = {}
        def page(name, title, description, body, **kwargs):
            self.pages[name] = {"title": title, "body": body, "kwargs": kwargs}
        def btn(url, label, kind="primary", *args, **kwargs):
            return '<a href="' + url + '">' + label + "</a>"
        self.ctx = {"OUT": str(self.root), "SITE": "https://crownsmere.com",
                    "BRAND": "Crownsmere Estate", "ALAA": "alaa.qadir@crownsmere.com",
                    "page": page, "btn": btn, "CRUMBS": {}, "SECTION_OF": {}}

    def records(self, items):
        (self.root / "data" / "properties.json").write_text(json.dumps(items), encoding="utf-8")

    def add_image(self, item):
        p = self.root / "assets" / "img" / "properties" / item["slug"]
        p.mkdir(parents=True, exist_ok=True)
        (p / "test.jpg").write_bytes(b"test fixture only")

    def test_empty_collection_is_safe(self):
        self.records([])
        self.assertEqual([], build_properties(self.ctx))
        self.assertIn("properties.html", self.pages)
        self.assertIn("collection is being prepared", self.pages["properties.html"]["body"].lower())
        self.assertNotIn("property-", ",".join(self.pages))

    def test_draft_is_never_public(self):
        row = ready_row()
        row.update(status="draft", owner_authority=False, compliance_cleared=False)
        self.records([row])
        self.assertEqual([], build_properties(self.ctx))
        self.assertNotIn(row["title"], self.pages["properties.html"]["body"])

    def test_review_cannot_be_bypassed(self):
        row = ready_row()
        row["compliance_cleared"] = False
        self.records([row])
        with self.assertRaisesRegex(ValueError, "Refusing to publish"):
            build_properties(self.ctx)

    def test_approved_property_has_detail_and_enquiry_for_alaa(self):
        row = ready_row()
        self.add_image(row)
        self.records([row])
        result = build_properties(self.ctx)
        self.assertEqual(["property-test-marylebone-apartment.html"], result)
        index = self.pages["properties.html"]["body"]
        detail = self.pages[result[0]]["body"]
        self.assertIn("£1,250,000", index)
        self.assertIn(row["title"], index)
        self.assertIn("data-property-enquiry", detail)
        self.assertIn("alaa.qadir@crownsmere.com", detail)
        self.assertIn("without my separate agreement", detail)
        self.assertNotIn(row["private_owner_email"], detail)
        self.assertIn(result[0], self.ctx["CRUMBS"])
        self.assertIn("assets/property.js", self.pages[result[0]]["kwargs"]["scripts"])

    def test_withdrawn_listing_cleans_up_old_page(self):
        row = ready_row()
        row["status"] = "withdrawn"
        self.records([row])
        old = self.root / "property-test-marylebone-apartment.html"
        old.write_text("Old page")
        self.assertEqual([], build_properties(self.ctx))
        self.assertFalse(old.exists())

    def test_rejects_image_path_traversal(self):
        row = ready_row()
        with self.assertRaisesRegex(ValueError, "image names"):
            allowed_image_path(self.root, row["slug"], "../outside.jpg")

if __name__ == "__main__":
    unittest.main()
