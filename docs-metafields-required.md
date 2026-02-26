# Metafields required by this theme

Create these in **Shopify Admin → Settings → Custom data** (or **Content → Metafields** in older admin). Definitions below use namespace `custom` unless noted.

---

## 1. ABD theme (header, footer, and section styling)

| Metafield key | Owner(s) | Type | Description |
|---------------|----------|------|-------------|
| **custom.abd_theme** | Page, Product, Collection, Article, Blog | **Single line text** or **Metaobject reference** | ABD theme for that resource. When set, header and footer (and product/article/blog sections) use this theme instead of the section default or “theme by page type.” |

**Allowed theme key values (use exactly one):**  
`cable-news`, `ca-assembly-daily-file`, `california-dreaming`, `california-mission`, `cubism`, `disco`, `france`, `free-love`, `highway-street-photo`, `impressionist`, `italy`, `men's-magazine`, `military-theme`, `millennial-myspace`, `national-parks-poster`, `newspaper`, `nineties-graphic-design`, `renaissance`, `retro-diner`, `retro-internet`, `retro-tech-polaroid`, `stars-and-stripes`, `stpatricks`, `las-vegas`, `travel-nyc-liberty`, `valentines-her`, `wayfinding-receipt`, `zine`

**Where it’s used:**
- **Header** – per-page header theme
- **Footer** – per-page footer theme
- **Product section** – product/collection theme for product template
- **Article section** – article/blog theme for article template
- **Blog section** – blog theme for blog template

### Option A: Single line text (legacy)

- **Namespace:** `custom`
- **Key:** `abd_theme`
- **Name:** e.g. “ABD theme”
- **Type:** Single line text
- **Definitions:** Create one for **Pages**, one for **Products**, one for **Collections**, one for **Articles**, one for **Blogs** (same namespace + key, different owners).  
- **Value:** One of the allowed theme keys above (e.g. `retro-internet`).

### Option B: Metaobject reference (dropdown of themes)

Use a **metaobject** as a reusable list of theme entries; each entry holds one theme key. Then set **custom.abd_theme** as a **Metaobject reference** to one of those entries.

1. **Create a metaobject definition** (e.g. “ABD Theme”):
   - Add one field that stores the theme key. The theme looks for a field with one of these **keys**: **`theme`**, **`theme_key`**, or **`value`** (use exactly one of these names).
   - Type for that field: **Single line text**.
   - Example: field key **`theme`**, name “Theme”, type Single line text. In each entry you enter a theme key (e.g. `retro-internet`, `cable-news`).

2. **Create metaobject entries** (one per theme or a curated list):
   - Each entry has that single-line field set to one of the allowed theme keys above.

3. **Create the metafield definition** for the resource (Page, Product, etc.):
   - **Namespace:** `custom`
   - **Key:** `abd_theme`
   - **Name:** e.g. “ABD theme”
   - **Type:** **Metaobject reference** → select your metaobject definition (e.g. “ABD Theme”).
   - **Definitions:** Create one for **Pages**, **Products**, **Collections**, **Articles**, **Blogs** as needed.

4. On each page/product/collection/article/blog, set **ABD theme** to one of the metaobject entries. The theme will read the theme key from that entry’s `theme`, `theme_key`, or `value` field.

---

## 2. Page featured image (multi-column section)

| Metafield key | Owner(s) | Type | Description |
|---------------|----------|------|-------------|
| **custom.featured_image** | Page | **File** (Image) | Image shown when a “Page” block in the Multi-column section has “Show image” enabled. |

**Where it’s used:**  
`sections/multi-column.liquid` – Page block: if “Show image” is on and this metafield is set, that image is used for the card.

**How to create in Shopify:**
- **Namespace:** `custom`
- **Key:** `featured_image`
- **Name:** e.g. “Featured image”
- **Type:** File – Images only
- **Definitions:** Pages only.

---

## 3. Product reviews (structured data / SEO)

| Metafield key | Owner(s) | Type | Description |
|---------------|----------|------|-------------|
| **reviews.rating** | Product | Number (decimal) or single line text | Average rating (e.g. 4.5). Used in JSON-LD for SEO. |
| **reviews.count** | Product | Integer or single line text | Total review count. Used in JSON-LD for SEO. |

**Where it’s used:**  
`snippets/structured-data.liquid` – adds `aggregateRating` to product schema when both are present.

**Note:** These are usually **filled by a review app** (e.g. Judge.me, Loox, Stamped, Yotpo). If you use such an app, it will create and populate these (or similarly named) metafields; you only need to create them yourself if you are not using an app and want to manually enter rating/count.

**If you create them manually:**
- **Namespace:** `reviews`
- **Keys:** `rating`, `count`
- **Types:** `rating` → Number (decimal) or Single line text; `count` → Integer or Single line text
- **Definitions:** Products only.

---

## Summary checklist

| # | Namespace | Key | Owner(s) | Type | Required for theme? |
|---|-----------|-----|----------|------|----------------------|
| 1 | custom | abd_theme | Page, Product, Collection, Article, Blog | Single line text or Metaobject reference | Optional (per-resource theme; metaobject = dropdown) |
| 2 | custom | featured_image | Page | File (image) | Optional (only if Multi-column “Page” blocks use “Show image”) |
| 3 | reviews | rating | Product | Number or text | Optional (or provided by review app) |
| 4 | reviews | count | Product | Integer or text | Optional (or provided by review app) |

**Minimum to “make” for your theme:**  
- **custom.abd_theme** (Page, Product, Collection, Article, Blog) if you want per-page/product/collection/article/blog header/footer and section themes.  
- **custom.featured_image** (Page) if you use Multi-column page blocks with images.  
- **reviews.rating** / **reviews.count** only if you’re not using a review app and want manual or custom review data in structured data.
