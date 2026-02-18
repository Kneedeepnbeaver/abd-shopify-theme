import re
import os

CSS_FILE = "/Volumes/The Secret Archive/01_BUSINESS/ABD 2.0/frontend/theme/assets/abd-themes.css"

def standardize_theme(theme_id, palette):
    """
    Standardizes a single theme in the CSS content.
    """
    if not os.path.exists(CSS_FILE):
        print(f"Error: {CSS_FILE} not found.")
        return

    with open(CSS_FILE, 'r') as f:
        content = f.read()

    # 1. Update/Inject Standard Variables
    # Find the block starting with .abd-theme-{theme_id}
    theme_pattern = rf"\.abd-theme-{theme_id}\s*\{{(.*?)\n\}}"
    match = re.search(theme_pattern, content, re.DOTALL)
    
    if not match:
        print(f"Theme {theme_id} not found in CSS.")
        return

    block_content = match.group(1)
    
    # Standard mapping template
    std_vars = f"""
    /* Shopify Standard Variables (Injected by standardize_themes.py) */
    --color-background: var(--bg, var(--paper, var(--background, {palette['bg']})));
    --color-foreground: var(--text, var(--ink, var(--color, {palette['ink']})));
    --color-primary: var(--accent, var(--primary, {palette['accent']}));
    --color-secondary: {palette['secondary']};
    --color-border: var(--rule, var(--border, {palette['border']}));
    
    /* Variable mapping for buttons */
    --color-bg: var(--paper, {palette['bg']});
    --color-text: var(--ink, {palette['ink']});
"""

    # Aggressively remove any existing standard variable blocks
    # This matches the comment and any subsequent --color- lines
    block_content = re.sub(rf"/\* Shopify Standard Variables.*?\*/(\s*--color-.*?;)+", "", block_content, flags=re.DOTALL)
    
    # Inject at the top of the block
    block_content = "\n" + std_vars.strip() + "\n" + block_content.strip()

    new_full_block = f".abd-theme-{theme_id} {{{block_content}\n}}"
    content = content.replace(match.group(0), new_full_block)

    # 2. Update/Inject Site-Wide Component Scoping
    site_wide_styles = f"""
/* Site-Wide Component Scoping for {theme_id} */
.abd-theme-{theme_id} .header-wrapper,
.abd-theme-{theme_id} header.shopify-section-header,
.abd-theme-{theme_id} .footer,
.abd-theme-{theme_id} .footer__content-top,
.abd-theme-{theme_id} .cart-drawer,
.abd-theme-{theme_id} .drawer__inner,
.abd-theme-{theme_id} .search-modal,
.abd-theme-{theme_id} .modal__content {{
    background-color: var(--color-background) !important;
    color: var(--color-foreground) !important;
}}

.abd-theme-{theme_id} .header__heading,
.abd-theme-{theme_id} .header__heading-link,
.abd-theme-{theme_id} .list-menu__item,
.abd-theme-{theme_id} .footer__link,
.abd-theme-{theme_id} .footer a,
.abd-theme-{theme_id} .footer__social a,
.abd-theme-{theme_id} .search-modal__input,
.abd-theme-{theme_id} .search__input {{
    color: var(--color-foreground) !important;
}}

.abd-theme-{theme_id} .header-wrapper,
.abd-theme-{theme_id} .footer {{
    border-color: var(--color-border) !important;
}}
"""
    # Injection/replacement logic for Site-Wide Components
    site_comment = f"/* Site-Wide Component Scoping for {theme_id} */"
    if site_comment in content:
        # Replace existing block
        site_pattern = rf"/\* Site-Wide Component Scoping for {theme_id} \*/.*?border-color: var\(--color-border\) !important;\s*\n\}}"
        content = re.sub(site_pattern, site_wide_styles.strip(), content, flags=re.DOTALL)
    else:
        content += site_wide_styles

    # 3. Update/Inject Button Components
    button_styles = f"""
/* Standard Button Components for {theme_id} */
.abd-theme-{theme_id} .button,
.abd-theme-{theme_id} .button--primary,
.abd-theme-{theme_id} .btn-primary,
.abd-theme-{theme_id} button:not([class*="quantity"]) {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 12px 24px;
    background: {palette['accent']} !important;
    color: {palette['btn_text']} !important;
    border: 2px solid var(--color-foreground) !important;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    box-shadow: 4px 4px 0 var(--color-foreground);
    border-radius: 0;
}}

.abd-theme-{theme_id} .button:hover,
.abd-theme-{theme_id} .button--primary:hover,
.abd-theme-{theme_id} .btn-primary:hover,
.abd-theme-{theme_id} button:not([class*="quantity"]):hover {{
    background: {palette['secondary']} !important;
    color: {palette['btn_text']} !important;
    transform: translate(-1px, -1px);
    box-shadow: 6px 6px 0 var(--color-foreground);
}}

.abd-theme-{theme_id} .button--secondary,
.abd-theme-{theme_id} .btn-secondary {{
    background: {palette['secondary']} !important;
    color: {palette['btn_text']} !important;
    border: 2px solid var(--color-foreground) !important;
    box-shadow: 4px 4px 0 var(--color-foreground);
}}

.abd-theme-{theme_id} .button--secondary:hover,
.abd-theme-{theme_id} .btn-secondary:hover {{
    background: {palette['accent']} !important;
    transform: translate(-1px, -1px);
    box-shadow: 6px 6px 0 var(--color-foreground);
}}
"""
    # Injection/replacement for buttons
    btn_comment = f"/* Standard Button Components for {theme_id} */"
    if btn_comment in content:
        btn_pattern = rf"/\* Standard Button Components for {theme_id} \*/.*?box-shadow: 6px 6px 0 var\(--color-foreground\);\s*\n\}}"
        content = re.sub(btn_pattern, button_styles.strip(), content, flags=re.DOTALL)
    else:
        # If it was injected without the new box-shadow variable, replace it manually
        btn_pattern_old = rf"/\* Standard Button Components for {theme_id} \*/.*?box-shadow: 6px 6px 0 .*?;\n\}}"
        if re.search(btn_pattern_old, content, re.DOTALL):
            content = re.sub(btn_pattern_old, button_styles.strip(), content, flags=re.DOTALL)
        else:
            content += button_styles

    with open(CSS_FILE, 'w') as f:
        f.write(content)

# Complete Palette Matrix
palettes = {
    # Batch 1: News & Gov
    "ca-assembly-daily-file": {"bg": "#ffffff", "ink": "#000000", "accent": "#1a365d", "secondary": "#333333", "border": "#cccccc", "btn_text": "#ffffff"},
    "cable-news": {"bg": "#ffffff", "ink": "#1a1a2e", "accent": "#dc2626", "secondary": "#1e40af", "border": "#1a1a2e", "btn_text": "#ffffff"},
    "newspaper": {"bg": "#e9e3d8", "ink": "#2b2b2b", "accent": "#7a6b5a", "secondary": "#4c4c4c", "border": "#cfc8be", "btn_text": "#ffffff"},
    
    # Batch 2: Cali & Nature
    "california-dreaming": {"bg": "#FFECB3", "ink": "#006994", "accent": "#007BFF", "secondary": "#FFD700", "border": "#FFC107", "btn_text": "#ffffff"},
    "california-mission": {"bg": "#6A3A4F", "ink": "#FFF3E0", "accent": "#F44336", "secondary": "#8BC34A", "border": "#212121", "btn_text": "#ffffff"},
    "national-parks-poster": {"bg": "#FDF5E6", "ink": "#1A1A1A", "accent": "#CC8833", "secondary": "#6A7B8C", "border": "#B0B8C8", "btn_text": "#ffffff"},
    "highway-street-photo": {"bg": "#FFFFFF", "ink": "#12285C", "accent": "#2E8B57", "secondary": "#1E66E0", "border": "#B0B0B0", "btn_text": "#ffffff"},
    
    # Batch 3: Artistic
    "cubism": {"bg": "#6EC4F2", "ink": "#4B3621", "accent": "#FF9900", "secondary": "#D2691E", "border": "#4B3621", "btn_text": "#ffffff"},
    "zine": {"bg": "#f5f5f5", "ink": "#111111", "accent": "#cf142b", "secondary": "#00247d", "border": "#111111", "btn_text": "#ffffff"},
    "impressionist": {"bg": "#F5E6DC", "ink": "#5C4A42", "accent": "#7BA3A8", "secondary": "#8B6B5C", "border": "#C8C0B8", "btn_text": "#ffffff"},
    "france": {"bg": "#f7f4ef", "ink": "#2b2b2b", "accent": "#c9232f", "secondary": "#1f4aa8", "border": "#2b2b2b", "btn_text": "#ffffff"},
    "italy": {"bg": "#dde8ed", "ink": "#333333", "accent": "#e88d3e", "secondary": "#7dc34c", "border": "#333333", "btn_text": "#ffffff"},
    "renaissance": {"bg": "#f4eddc", "ink": "#2b2621", "accent": "#6b2c2c", "secondary": "#5a3e2b", "border": "#cdbfa8", "btn_text": "#ffffff"},
    "free-love": {"bg": "#f7efe0", "ink": "#3b2a1e", "accent": "#ff6b6b", "secondary": "#5fbf6a", "border": "#3b2a1e", "btn_text": "#ffffff"},
    
    # Batch 4: Retro
    "disco": {"bg": "#241018", "ink": "#fff2d9", "accent": "#ff4fb2", "secondary": "#3fe0d0", "border": "#f5c542", "btn_text": "#ffffff"},
    "retro-diner": {"bg": "#fff7ee", "ink": "#111111", "accent": "#e53935", "secondary": "#2bb7b3", "border": "#111111", "btn_text": "#ffffff"},
    "retro-internet": {"bg": "#111111", "ink": "#ffff00", "accent": "#00ffff", "secondary": "#ff00ff", "border": "#c0c0c0", "btn_text": "#000000"},
    "las-vegas": {"bg": "#93d0e2", "ink": "#2b1d12", "accent": "#d34e35", "secondary": "#2993ae", "border": "#2993ae", "btn_text": "#ffffff"},
    "retro-tech-polaroid": {"bg": "#ffffff", "ink": "#2b2b2b", "accent": "#ff5fa2", "secondary": "#ff9a3c", "border": "#2b2b2b", "btn_text": "#ffffff"},
    "millennial-myspace": {"bg": "#fafafa", "ink": "#262626", "accent": "#3b5998", "secondary": "#e95950", "border": "#dbdbdb", "btn_text": "#ffffff"},
    "nineties-graphic-design": {"bg": "#ffffff", "ink": "#000000", "accent": "#ffee00", "secondary": "#00ffff", "border": "#000000", "btn_text": "#000000"},
    
    # Final Batch: Misc
    "military-theme": {"bg": "#faf8f3", "ink": "#1a237e", "accent": "#d4af37", "secondary": "#001f3f", "border": "#d4af37", "btn_text": "#ffffff"},
    "mens-magazine": {"bg": "#f5ebe0", "ink": "#1a1510", "accent": "#c41e3a", "secondary": "#d4af37", "border": "#1a1510", "btn_text": "#ffffff"},
    "stars-and-stripes": {"bg": "#FFFAF0", "ink": "#1a1a1a", "accent": "#BF0A30", "secondary": "#002868", "border": "#1a1a1a", "btn_text": "#ffffff"},
    "stpatricks": {"bg": "#FFE4C4", "ink": "#1a2e1a", "accent": "#2D5A27", "secondary": "#E07C3C", "border": "#1a2e1a", "btn_text": "#ffffff"},
    "travel-nyc-liberty": {"bg": "#e8f4fc", "ink": "#1a365d", "accent": "#cf142b", "secondary": "#ffd700", "border": "#1a365d", "btn_text": "#ffffff"},
    "valentines-her": {"bg": "#FFE4C4", "ink": "#3d2914", "accent": "#C41E3A", "secondary": "#FFB6C1", "border": "#3d2914", "btn_text": "#ffffff"},
    "wayfinding-receipt": {"bg": "#f4f2ee", "ink": "#1d1d1d", "accent": "#2b5da8", "secondary": "#5a5a5a", "border": "#1d1d1d", "btn_text": "#ffffff"},
}

for theme_id, palette in palettes.items():
    standardize_theme(theme_id, palette)
    print(f"Standardized {theme_id}")
