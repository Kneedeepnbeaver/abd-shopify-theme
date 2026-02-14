import re
import os
import json

# Configuration
css_file_path = '/Volumes/The Secret Archive/01_BUSINESS/ABD 2.0/frontend/theme/assets/abd-themes.css'
output_md_path = '/Volumes/The Secret Archive/01_BUSINESS/ABD 2.0/frontend/theme/THEME_COLORS.md'
output_liquid_path = '/Volumes/The Secret Archive/01_BUSINESS/ABD 2.0/frontend/theme/sections/theme-color-guide.liquid'

def parse_css_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    themes = {}
    current_theme = None
    
    # Split content by lines to process sequentially, but keep it simple
    # Better approach for this structured file: Find blocks
    
    # Regex to find theme blocks: START OF LINE .abd-theme-name { ... }
    # This avoids capturing the Dark Mode blocks inside @media which are indented
    theme_usage_regex = re.compile(r'(?m)^\.abd-theme-([a-z0-9-]+)\s*\{(.*?)\}', re.DOTALL)
    
    matches = theme_usage_regex.findall(content)
    
    for theme_name, block_content in matches:
        # Ignore media queries for now, just get the main block
        colors = []
        # Regex for variables: --name: value; /* comment */
        # Values can be hex, rgb, rgba, or color names
        color_regex = re.compile(r'\s*(--[a-z0-9-]+):\s*([^;]+);\s*(/\*.*?\*/)?')
        
        for line in block_content.strip().split('\n'):
            line = line.strip()
            match = color_regex.match(line)
            if match:
                var_name = match.group(1)
                color_value = match.group(2).strip()
                comment = match.group(3)
                
                # Check if it looks like a color
                if (color_value.startswith('#') or 
                    color_value.startswith('rgb') or 
                    color_value.startswith('hsl') or
                    var_name in ['--bg', '--text', '--accent', '--alert', '--panel', '--muted', '--rule']):
                    
                    colors.append({
                        'variable': var_name,
                        'value': color_value,
                        'comment': comment.strip('/* ').strip(' */') if comment else ''
                    })
        
        if colors:
            themes[theme_name] = colors
            
    return themes

def generate_markdown(themes):
    md_content = "# ABD Theme Color Reference\n\n"
    md_content += "This document contains the extracted color palettes for all ABD Themes. Use these hex codes when setting **Custom Colors** in the Theme Editor to maintain consistency.\n\n"
    
    for theme_name, colors in sorted(themes.items()):
        formatted_name = theme_name.replace('-', ' ').title()
        md_content += f"## {formatted_name} (`{theme_name}`)\n\n"
        md_content += "| Variable | Color | Hex/Value | Description |\n"
        md_content += "| :--- | :---: | :--- | :--- |\n"
        
        for color in colors:
            # We can't render the color swatch easily in a plain markdown file without HTML/Images, 
            # but we can try using a placeholder or just the text.
            # Ideally we'd use a service like shields.io for swatches, but let's keep it simple text for now.
            val = color['value']
            md_content += f"| `{color['variable']}` | <div style='background-color:{val}; width:20px; height:20px; border:1px solid #ccc;'></div> | `{val}` | {color['comment']} |\n"
        
        md_content += "\n"
        
    return md_content

def generate_liquid_section(themes):
    liquid_content = """{% comment %}
  Theme Color Guide Section
  Generated automatically.
{% endcomment %}

<div class="page-width section-color-guide">
  <h2 class="abd-title">ABD Theme Color Styles</h2>
  <div class="color-guide-grid">
"""
    
    # We will loop through our extracted data and create hardcoded HTML for this section
    # This is "consistent" because it's static at generation time.
    
    for theme_name, colors in sorted(themes.items()):
        formatted_name = theme_name.replace('-', ' ').title()
        
        liquid_content += f"""    <div class="theme-block">
      <h3 class="theme-title">{formatted_name}</h3>
      <code class="theme-code">.abd-theme-{theme_name}</code>
      <div class="color-list">
"""
        for color in colors:
             liquid_content += f"""        <div class="color-item">
          <div class="color-swatch" style="background-color: {color['value']};"></div>
          <div class="color-info">
            <span class="color-var">{color['variable']}</span>
            <span class="color-val">{color['value']}</span>
            <span class="color-desc">{color['comment']}</span>
          </div>
        </div>
"""
        liquid_content += """      </div>
    </div>
"""

    liquid_content += """  </div>
</div>

{% schema %}
{
  "name": "Theme Color Guide",
  "tag": "section",
  "class": "section-theme-color-guide",
  "settings": [],
  "presets": [
    {
      "name": "Theme Color Guide"
    }
  ]
}
{% endschema %}

{% style %}
.section-color-guide {
  padding: 60px 20px;
}
.color-guide-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 40px;
}
.theme-block {
  border: 1px solid #e0e0e0;
  padding: 20px;
  border-radius: 8px;
}
.theme-title {
  margin: 0 0 5px 0;
  font-size: 1.25rem;
}
.theme-code {
  display: block;
  margin-bottom: 15px;
  color: #666;
  font-size: 0.85rem;
}
.color-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.color-item {
  display: flex;
  align-items: center;
  gap: 15px;
}
.color-swatch {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  border: 1px solid #ddd;
  flex-shrink: 0;
}
.color-info {
  display: flex;
  flex-direction: column;
  font-size: 0.85rem;
}
.color-var {
  font-weight: bold;
}
.color-val {
  font-family: monospace;
  color: #555;
}
.color-desc {
  font-style: italic;
  color: #888;
  font-size: 0.8rem;
}
{% endstyle %}
"""
    return liquid_content

# Main Execution
themes = parse_css_file(css_file_path)

# Write Markdown
with open(output_md_path, 'w') as f:
    f.write(generate_markdown(themes))

# Write Liquid Section
with open(output_liquid_path, 'w') as f:
    f.write(generate_liquid_section(themes))

print(f"Parsed {len(themes)} themes.")
print(f"Generated Markdown: {output_md_path}")
print(f"Generated Liquid: {output_liquid_path}")
print("Example extracted from Cable News:")
# simple print of first few colors to verify
if 'cable-news' in themes:
    for c in themes['cable-news'][:3]:
        print(f"  {c['variable']}: {c['value']}")
