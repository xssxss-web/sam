# MikeOK Hugo Website

mikeok.com — Yiwu Sourcing Agent & B2B Wholesale Supplier website, built with Hugo + GitHub Pages + GitHub Actions.

## Tech Stack

- **Hugo** — static site generator
- **GitHub Pages** — free hosting
- **GitHub Actions** — auto-deploy on every push
- **Python** — CSV to Markdown product converter

## Project Structure

```
mikeok-hugo/
├── hugo.yaml                    # Site config (baseURL, menus, taxonomies, SEO)
├── data/                        # Data-driven content (edit once, update everywhere)
│   ├── company.yaml             # Company name, contact, address, trade terms
│   ├── categories.yaml          # Product categories with descriptions
│   └── footer.yaml             # Footer links and trade terms
├── content/                     # All page content as Markdown
│   ├── _index.md                # Homepage
│   ├── about.md                 # About page
│   ├── services.md              # Services page
│   ├── contact.md               # Contact page
│   ├── products/_index.md       # Products overview
│   └── guides/_index.md         # Wholesale guides
├── layouts/                     # Hugo templates
│   ├── _default/                # baseof, single, list
│   ├── products/                # Product single + list
│   ├── categories/              # Category term pages
│   ├── partials/                # head, header, footer, breadcrumbs, product-card, schema
│   └── robots.txt
├── static/css/main.css          # Full site stylesheet
├── scripts/
│   └── csv_to_hugo_markdown.py  # CSV → Hugo .md converter
└── .github/workflows/hugo.yaml  # Auto-deploy workflow
```

## Quick Start

### 1. Add products from CSV

```bash
python scripts/csv_to_hugo_markdown.py products.csv content/products/
```

This reads your 53-column product CSV and generates one `.md` file per product in `content/products/`.

### 2. Preview locally

```bash
hugo server -D
```

Open http://localhost:1313

### 3. Deploy

Push to `main` branch → GitHub Actions builds and publishes automatically.

First-time setup: go to your repo → Settings → Pages → Source = GitHub Actions.

## Editing Guide

| What to change | Edit this file |
|---|---|
| Company name, phone, email | `data/company.yaml` |
| Product categories | `data/categories.yaml` |
| Footer links | `data/footer.yaml` |
| Homepage content | `content/_index.md` + `layouts/index.html` |
| Product content | `content/products/*.md` |
| Product page layout | `layouts/products/single.html` |
| Site-wide styles | `static/css/main.css` |
| SEO / site config | `hugo.yaml` |

## Design Principles

- **Data-driven** — Company info, categories, and footer links are centralized in `data/` files. Change once, update everywhere.
- **Product pages are standalone** — Adding new products never touches navigation, layout, or config.
- **New categories only need one edit** — Add an entry to `data/categories.yaml`, and it appears in navigation, footer, homepage, and category filter automatically.
- **CSV is the single source of truth** — All product data lives in a spreadsheet. The Python script converts it to Hugo Markdown.

## Scaling to 500+ Products

The architecture is built for scale:

- Each product is one `.md` file — no database, no backend
- Hugo builds 500+ pages in seconds
- GitHub Pages handles unlimited static pages for free
- Category pages auto-populate from product frontmatter
- Sitemap, robots.txt, and llms.txt auto-generate

## SEO & GEO

- Clean URLs with product slugs
- Structured data (Schema.org Product) on every product page
- Open Graph meta tags for social sharing
- Auto-generated sitemap.xml
- llms.txt for AI tool discovery
- Canonical URLs for duplicate content prevention
