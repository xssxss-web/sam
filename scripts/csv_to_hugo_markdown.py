#!/usr/bin/env python3
"""
MikeOK CSV to Hugo Markdown converter.

Reads a product CSV (53-column universal template) and generates
one Hugo .md file per product under content/products/.

Usage:
    python scripts/csv_to_hugo_markdown.py products.csv content/products/

The script maps 35 public fields to Hugo frontmatter and product page content.
18 internal fields (supplier info, cost, internal notes) are preserved in
frontmatter but not rendered by the default product template.

Full field mapping reference:
    data/categories.yaml   — category definitions
    hugo.yaml              — site config and taxonomies
"""

import csv, re, sys
from pathlib import Path
from datetime import date


def slugify(s):
    """Convert a string to a URL-safe slug."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"[\s-]+", "-", s).strip("-")


def q(s):
    """Wrap a string value in YAML-safe double quotes."""
    return '"' + str(s).replace('"', '\\"').replace("\n", "\\n") + '"'


def list_yaml(items):
    """Convert comma-separated values to YAML list."""
    vals = [x.strip() for x in (items or "").split(",") if x.strip()]
    return "[" + ", ".join(q(x) for x in vals) + "]"


def add(lines, key, value, numeric=False):
    """Add a YAML frontmatter key-value pair, skipping empty values."""
    if value is None or str(value).strip() == "":
        return
    v = str(value).strip()
    if numeric:
        try:
            float(v)
            lines.append(f"{key}: {v}")
            return
        except ValueError:
            pass
    lines.append(f"{key}: {q(v)}")


def build_markdown(row):
    """
    Build a complete Hugo .md file from one CSV row.
    Returns (filename, content) or (None, None) if SKU or name is missing.
    """

    # --- Required fields ---
    sku = row.get("sku", "").strip()
    name = row.get("product_name_en", "").strip()
    if not sku or not name:
        return None, None

    slug = row.get("slug", "").strip() or slugify(name)
    category = slugify(row.get("category", "").strip() or row.get("category_en", "").strip())

    lines = ["---"]

    # --- Core identity ---
    add(lines, "title", name)
    add(lines, "slug", slug)
    add(lines, "sku", sku)
    if category:
        lines.append(f"categories: [{q(category)}]")

    # --- Taxonomies ---
    if row.get("tags"):
        lines.append(f"tags: {list_yaml(row.get('tags'))}")
    if row.get("target_buyers"):
        lines.append(f"buyers: {list_yaml(row.get('target_buyers'))}")
    if row.get("use_cases"):
        lines.append(f"usecases: {list_yaml(row.get('use_cases'))}")

    # --- SEO & display ---
    add(lines, "description", row.get("meta_description") or row.get("short_summary_en"))
    add(lines, "summary", row.get("short_summary_en"))
    add(lines, "product_name_cn", row.get("product_name_cn"))

    # --- Product specifications ---
    for key in [
        "material", "color_options", "size_cm", "weight_g",
        "packing", "carton_qty_pcs", "carton_size_cm",
        "carton_gw_kg", "carton_nw_kg",
    ]:
        numeric = key in (
            "weight_g", "carton_qty_pcs", "carton_gw_kg", "carton_nw_kg"
        )
        add(lines, key, row.get(key), numeric=numeric)

    # --- Wholesale info ---
    for key in [
        "moq_pcs", "price_min_usd", "price_max_usd", "sample_fee_usd",
    ]:
        add(lines, key, row.get(key), numeric=True)

    add(lines, "lead_time_days", row.get("lead_time_days"))
    add(lines, "customization_options", row.get("customization_options"))
    add(lines, "certifications", row.get("certifications"))

    # --- Images ---
    add(lines, "main_image", row.get("main_image"))
    add(lines, "image_alt", row.get("image_alt_en"))
    if row.get("gallery_images"):
        lines.append("gallery_images:")
        for img in [x.strip() for x in row.get("gallery_images", "").split(",") if x.strip()]:
            lines.append(f"  - {q(img)}")

    # --- FAQ (up to 4 entries) ---
    faq = []
    for i in range(1, 5):
        question = row.get(f"faq_{i}_q", "").strip()
        answer = row.get(f"faq_{i}_a", "").strip()
        if question and answer:
            faq.append((question, answer))
    if faq:
        lines.append("faq:")
        for question, answer in faq:
            lines.append(f"  - question: {q(question)}")
            lines.append(f"    answer: {q(answer)}")

    # --- Related products ---
    if row.get("related_skus"):
        lines.append(f"related_skus: {list_yaml(row.get('related_skus'))}")

    # --- Internal fields (not rendered on public pages) ---
    # These are preserved in frontmatter but hidden by templates.
    # Suppliers can access them for internal reference if needed.
    for key in [
        "branch_code", "supplier_name", "supplier_contact",
        "market_location", "supplier_type",
        "source_cost_rmb", "quality_notes", "risk_notes", "internal_notes",
    ]:
        add(lines, f"internal_{key}", row.get(key))

    # --- Publish status ---
    lines.append("draft: false")
    lines.append(f"last_updated: {q(date.today().isoformat())}")
    lines.append("---")
    lines.append("")

    # --- Body content ---
    body = row.get("description_en", "").strip() or row.get("short_summary_en", "").strip()
    if not body:
        body = f"Wholesale {name} from Yiwu China. Contact us for pricing, samples, and customization options."
    lines.append(body)

    filename = f"{sku.lower()}-{slug}.md"
    return filename, "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/csv_to_hugo_markdown.py products.csv content/products/")
        print()
        print("  Reads a 53-column product CSV and generates Hugo .md files.")
        print("  Each product file includes full frontmatter for the MikeOK Hugo theme.")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    if not src_path.exists():
        print(f"Error: CSV file not found: {src_path}")
        sys.exit(1)

    count = 0
    skipped = 0

    with src_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename, content = build_markdown(row)
            if filename:
                out_path = out_dir / filename
                out_path.write_text(content, encoding="utf-8")
                count += 1
            else:
                skipped += 1

    print(f"Done. Generated {count} Hugo product markdown files in {out_dir}")
    if skipped:
        print(f"Skipped {skipped} rows (missing SKU or product name).")


if __name__ == "__main__":
    main()
