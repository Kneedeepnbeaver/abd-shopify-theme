# ABD theme layout notes (sections vs. themes)

Some ABD themes (like `cable-news`, `ca-assembly-daily-file`, `california-dreaming`, `california-mission`, `cubism`, `disco`, `newspaper`, etc.) apply **layout rules** directly to `.theme-content` and `.abd-content` in `assets/abd-themes.css`. Examples:

```css
.abd-theme-cable-news .theme-content,
.abd-theme-cable-news .abd-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  /* ... sidebar layout ... */
}
```

That works well when you **want** a 2‑column layout with a sidebar, but it can make some sections (articles, pages, etc.) look too narrow or pushed to the left when they only have main content and no sidebar.

## Fixing it by section (preferred pattern)

Rather than changing `abd-themes.css` globally, we **override per section** so only the sections we care about are forced back to a single column.

### Article section

File: `sections/article.liquid`

```liquid
{% style %}
  .section-article {
    padding-top: {{ section.settings.padding_top | default: 60 }}px;
    padding-bottom: {{ section.settings.padding_bottom | default: 60 }}px;
  }

  .article {
    width: 100%;
    max-width: 100%;
  }

  /* Ensure article body is a single full-width column even when ABD themes add grid/sidebars */
  .section-article .abd-content {
    display: block;
    max-width: 100%;
  }
{% endstyle %}
```

### Page section

File: `sections/page.liquid`

```liquid
{% style %}
  .section-page .abd-content {
    display: block;
    max-width: 100%;
  }
{% endstyle %}
```

### Rich Text section

File: `sections/rich-text.liquid`

```liquid
{% style %}
  .section-rich-text {
    padding-top: {{ section.settings.padding_top }}px;
    padding-bottom: {{ section.settings.padding_bottom }}px;
  }

  /* Force single-column body */
  .section-rich-text .abd-content {
    display: block;
    max-width: 100%;
  }
{% endstyle %}
```

### Product section

File: `sections/product.liquid`

```liquid
{% style %}
  .section-product {
    padding-top: {{ section.settings.padding_top | default: 60 }}px;
    padding-bottom: {{ section.settings.padding_bottom | default: 60 }}px;
  }

  /* ... existing product layout rules ... */

  /* Force product description to single-column */
  .section-product .abd-content {
    display: block;
    max-width: 100%;
  }
{% endstyle %}
```

### About Me section

File: `sections/about-me.liquid`

```liquid
{% style %}
  .section-about-me {
    padding-top: {{ section.settings.padding_top }}px;
    padding-bottom: {{ section.settings.padding_bottom }}px;
  }

  .section-about-me .abd-content {
    display: block;
    max-width: 100%;
  }
{% endstyle %}
```

### Downloads / GitHub programs section

File: `sections/hello-world.liquid` (Downloads)

```liquid
{% stylesheet %}
  .downloads-section {
    display: grid;
    grid-template-columns: var(--content-grid, 1fr);
    background-color: #f6f6f7;
  }

  /* ... existing styles ... */

  /* Ensure intro + card descriptions stay single-column */
  .downloads-section .abd-content {
    display: block;
    max-width: 100%;
  }
{% endstylesheet %}
```

## When to use this pattern

Use the **section-local override** when:

- The ABD theme should still control typography, colors, “paper” backgrounds, etc.
- A specific section (article, legal page, about page, product, downloads) should always read as a single wide column, even if the theme normally uses a 2‑column grid for `.abd-content`.

If you ever want to move this to a more global pattern, the next step would be to update `abd-themes.css` so sidebar grids only apply to `.abd-content.columns` (or similar), and then opt-in per template by adding that class. For now, the section overrides above are the safest way to keep layouts predictable while experimenting with themes.

