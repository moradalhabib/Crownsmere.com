"""Create an isolated synthetic property-site build for browser and HTML QA.

Never writes fixtures into the live repository. Generated sample content is
strictly for local CI validation and must never be committed or deployed.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

def create_fixture(output):
    repo = Path(__file__).resolve().parents[1]
    root = Path(output).resolve()
    if root == repo or repo in root.parents:
        raise ValueError("Fixture output must be outside the tracked repository")
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "data").mkdir(exist_ok=True)
    shutil.copy2(repo / "tools/build.py", root / "tools/build.py")
    shutil.copy2(repo / "tools/property_pages.py", root / "tools/property_pages.py")
    shutil.copytree(repo / "assets", root / "assets", dirs_exist_ok=True)
    slug = "qa-fictional-apartment"
    photos = root / "assets/img/properties" / slug
    photos.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / "assets/img/townhouse.jpg", photos / "image.jpg")
    listing = {
        "slug": slug,
        "reference": "CME-QA-ONLY",
        "status": "published",
        "owner_authority": True,
        "compliance_cleared": True,
        "listing_type": "rent",
        "title": "QA Fictional Apartment",
        "area": "Test District",
        "address_public": "Test District, London",
        "price": 4321,
        "rent_period": "pcm",
        "property_type": "Apartment",
        "bedrooms": 2,
        "bathrooms": 1,
        "floor_area_sqft": 754,
        "description": "Fictional QA property, not an available listing. <script>alert('xss')</script>",
        "features": ["Private terrace", "Near test station"],
        "epc_rating": "C",
        "furnished": "Furnished",
        "availability": "By appointment",
        "photos": ["image.jpg"],
        "private_owner_email": "private-qa-owner@example.test",
    }
    (root / "data/properties.json").write_text(json.dumps([listing], indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(root / "tools/build.py")], cwd=root, check=True)
    detail = (root / ("property-" + slug + ".html")).read_text(encoding="utf-8")
    index = (root / "properties.html").read_text(encoding="utf-8")
    sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")
    assert "<script>alert('xss')</script>" not in detail, "XSS escaped in visible content and JSON-LD"
    assert "\\u003cscript\\u003e" in detail, "Structured data safely escaped"
    assert "&lt;script&gt;" in detail, "Description safely escaped"
    assert "private-qa-owner@example.test" not in detail + index, "Owner contact must remain private"
    assert "property-qa-fictional-apartment.html" in sitemap, "Published fixture must enter sitemap"
    print("QA-only fixture built and verified:", root)
    return root

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    create_fixture(args.output_dir)
