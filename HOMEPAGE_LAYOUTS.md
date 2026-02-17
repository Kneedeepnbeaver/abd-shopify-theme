# Homepage layout options (SEO-friendly)

Rough drafts for your theme editor. A wireframe graphic of all three layouts is available for reference (see generated image in this chat). All section names match your `frontend/theme/sections` so you can add/reorder them in the Shopify theme editor.

---

## Layout A — “Classic store” (current-style)

**Best for:** Clear shopping path, strong first impression.

| Order | Section | SEO / UX note |
|-------|--------|----------------|
| 1 | **Hero Banner** | One clear H1 + CTA. Use `heading` as main keyword phrase. |
| 2 | **Featured Collection** | Products above the fold → internal links, relevance. |
| 3 | **Feature Grid** | Trust (shipping, returns, security). Good for E-E-A-T. |
| 4 | **Image with Text** | About / story. Use `heading` + `content` for brand keywords. |
| 5 | **Rich Text** (optional) | Policies snippet, “Why shop here,” or FAQ teaser. |

**Theme editor:** `templates/index.json` → section order: `hero_banner` → `featured_collection` → `feature_grid` → `image_with_text`.

---

## Layout B — “Browse first”

**Best for:** Multiple categories, discovery, content-rich homepage.

| Order | Section | SEO / UX note |
|-------|--------|----------------|
| 1 | **Hero Banner** | Short headline + primary CTA. |
| 2 | **Collections** (grid) | Category links = strong internal linking + crawl depth. |
| 3 | **Featured Collection** | “New” or “Bestsellers” — keep one main product block. |
| 4 | **Video Banner** or **Image with Text** | One story/explainer block. |
| 5 | **Feature Grid** | Trust/shipping/security. |
| 6 | **Blog** (teaser) | Fresh content, more keywords, internal links. |

**Theme editor:** Add `collections` (list-collections style) and optionally `blog` section; order as above.

---

## Layout C — “Brand / editorial”

**Best for:** Strong brand story, visual products, “magazine” feel.

| Order | Section | SEO / UX note |
|-------|--------|----------------|
| 1 | **Hero Banner** or **Video Banner** | Full-width hero; H1 in settings. |
| 2 | **Multi-Column Content** | 2–3 columns: categories, “Shop by X,” or short copy. |
| 3 | **Featured Collection** | One focused product strip. |
| 4 | **Image with Text** (×2 optional) | Two blocks: e.g. “Our process” + “Sustainability.” |
| 5 | **Logo List** | “As seen in” / stockists / certifications → trust. |
| 6 | **Rich Text** | Short FAQ or “How to shop” for long-tail queries. |

**Theme editor:** Use `multi-column`, `image-with-text`, `logo-list`, `rich-text` in this order.

---

## SEO checklist (any layout)

- **One H1:** Set it in Hero (or first section with a heading). Don’t duplicate H1 in other sections.
- **Heading order:** H1 → H2 (section titles) → H3 (sub-blocks). Use `feature-grid` / `rich-text` headings as H2s.
- **Internal links:** Use **Featured Collection**, **Collections**, and **Blog** to link to collection and article URLs.
- **Above the fold:** Hero + one product or category block so crawlers and users see intent fast.
- **Unique text:** Put real copy in **Rich Text** and **Image with Text** (not only images) so the homepage has indexable content.

---

## Section → template reference

| Section (theme editor name) | Liquid file | Typical use |
|----------------------------|-------------|-------------|
| Hero Banner | `hero-banner.liquid` | Top hero, H1, CTA |
| Featured Collection | `featured-collection.liquid` | Product strip |
| Feature Grid | `feature-grid.liquid` | Icons + trust copy |
| Image with Text | `image-with-text.liquid` | Story, about, promo |
| Rich Text | `rich-text.liquid` | Policies, FAQ, copy |
| Collections | `collections.liquid` | Category grid |
| Multi-Column Content | `multi-column.liquid` | Columns (links, text, images) |
| Video Banner | `video-banner.liquid` | Hero or mid-page video |
| Logo List | `logo-list.liquid` | Trust / press logos |
| Blog | `blog.liquid` | Article teasers |
| Image Gallery | `image-gallery.liquid` | Lookbook / gallery |
| Slideshow Gallery | `slideshow-gallery.liquid` | Rotating banners |

Use this doc next to the theme editor to pick a layout and then drag sections into the same order in **Theme → Customize → Homepage**.
image.png