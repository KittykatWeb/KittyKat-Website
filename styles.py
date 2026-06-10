import re


COLORS = {
    "white": "#ffffff",
    "black": "#111111",
    "red": "#e74c3c",
    "orange": "#f39c12",
    "yellow": "#f1c40f",
    "green": "#27ae60",
    "teal": "#1abc9c",
    "blue": "#3498db",
    "navy": "#1a237e",
    "purple": "#9b59b6",
    "pink": "#e91e63",
    "gray": "#7f8c8d",
    "grey": "#7f8c8d",
    "light gray": "#f4f4f4",
    "light grey": "#f4f4f4",
    "dark gray": "#333333",
    "dark grey": "#333333",
    "coral": "#ff6b6b",
    "cream": "#fff8e7",
    "lavender": "#e8e0f0",
    "mint": "#d4edda",
    "sky": "#87ceeb",
}

SIZES = {
    "tiny": "0.75rem",
    "small": "0.875rem",
    "medium": "1rem",
    "large": "1.75rem",
    "huge": "3rem",
}

SPACING = {
    "none": "0",
    "tiny": "4px",
    "small": "8px",
    "medium": "16px",
    "large": "32px",
    "huge": "64px",
}

FONTS = {
    "sans": "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
    "serif": "Georgia, Cambria, Times New Roman, serif",
    "mono": "Consolas, Monaco, Courier New, monospace",
}

STYLE_TARGETS = {
    "page": "body",
    "heading": "h1",
    "subheading": "h2",
    "paragraph": "p",
    "button": "button",
    "link": "a",
    "image": "img",
    "list": "ul",
    "quote": "blockquote",
    "badge": ".kkat-badge",
}

STYLE_LINE = re.compile(
    r"^(center|left|right|bold|italic|underline|rounded(?: corners)?|shadow|soft shadow|"
    r"spread horizontally|stack vertically|space between|space evenly|space around|"
    r"align center|align start|align end|sticky top|transition smooth|"
    r"background color .+|text color .+|color .+|font size .+|font family .+|"
    r"padding(?: (?:top|bottom|left|right))? .+|margin(?: (?:top|bottom|left|right))? .+|"
    r"border color .+|border (?:thin|thick)|width .+|max width .+|gap .+|"
    r"opacity .+|gradient from .+ to .+|"
    r"when hover \{|hover background color .+|hover text color .+)$",
    re.IGNORECASE,
)


def resolve_color(name):
    key = name.strip().lower()
    if key in COLORS:
        return COLORS[key]
    if re.fullmatch(r"#[0-9a-fA-F]{3,8}", name.strip()):
        return name.strip()
    return name.strip()


def resolve_size(value):
    key = value.strip().lower()
    if key in SIZES:
        return SIZES[key]
    if re.fullmatch(r"\d+(\.\d+)?", key):
        return f"{key}px"
    return value.strip()


def resolve_spacing(value):
    key = value.strip().lower()
    if key in SPACING:
        return SPACING[key]
    if re.fullmatch(r"\d+(\.\d+)?", key):
        return f"{key}px"
    return value.strip()


def parse_rules(block):
    rules = {}
    hover_rules = {}
    lines = block.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        index += 1

        if not line or line.startswith("//"):
            continue

        if line.lower() == "when hover {":
            hover_block_lines = []
            depth = 1
            while index < len(lines) and depth > 0:
                inner_line = lines[index].strip()
                index += 1
                if inner_line.lower() == "when hover {":
                    depth += 1
                    hover_block_lines.append(inner_line)
                elif inner_line == "}":
                    depth -= 1
                    if depth > 0:
                        hover_block_lines.append(inner_line)
                else:
                    hover_block_lines.append(inner_line)
            nested_rules, nested_hover = parse_rules("\n".join(hover_block_lines))
            hover_rules.update(nested_rules)
            hover_rules.update(nested_hover)
            continue

        apply_rule_line(line, rules)

    return rules, hover_rules


def apply_rule_line(line, rules):
    if line == "center":
        rules["text-align"] = "center"
        return
    if line == "left":
        rules["text-align"] = "left"
        return
    if line == "right":
        rules["text-align"] = "right"
        return
    if line == "bold":
        rules["font-weight"] = "bold"
        return
    if line == "italic":
        rules["font-style"] = "italic"
        return
    if line == "underline":
        rules["text-decoration"] = "underline"
        return
    if line in ("rounded", "rounded corners"):
        rules["border-radius"] = "8px"
        return
    if line == "shadow":
        rules["box-shadow"] = "0 4px 12px rgba(0, 0, 0, 0.15)"
        return
    if line == "soft shadow":
        rules["box-shadow"] = "0 2px 8px rgba(0, 0, 0, 0.08)"
        return
    if line == "spread horizontally":
        rules["display"] = "flex"
        rules["flex-direction"] = "row"
        rules.setdefault("gap", "1rem")
        rules.setdefault("align-items", "center")
        return
    if line == "stack vertically":
        rules["display"] = "flex"
        rules["flex-direction"] = "column"
        rules.setdefault("gap", "0.5rem")
        return
    if line == "space between":
        rules["display"] = "flex"
        rules["justify-content"] = "space-between"
        return
    if line == "space evenly":
        rules["display"] = "flex"
        rules["justify-content"] = "space-evenly"
        return
    if line == "space around":
        rules["display"] = "flex"
        rules["justify-content"] = "space-around"
        return
    if line == "align center":
        rules["align-items"] = "center"
        return
    if line == "align start":
        rules["align-items"] = "flex-start"
        return
    if line == "align end":
        rules["align-items"] = "flex-end"
        return
    if line == "sticky top":
        rules["position"] = "sticky"
        rules["top"] = "0"
        rules["z-index"] = "100"
        return
    if line == "transition smooth":
        rules["transition"] = "all 0.2s ease"
        return

    match = re.fullmatch(r"background color (.+)", line, re.IGNORECASE)
    if match:
        rules["background-color"] = resolve_color(match.group(1))
        return
    match = re.fullmatch(r"text color (.+)", line, re.IGNORECASE)
    if match:
        rules["color"] = resolve_color(match.group(1))
        return
    match = re.fullmatch(r"color (.+)", line, re.IGNORECASE)
    if match:
        rules["color"] = resolve_color(match.group(1))
        return
    match = re.fullmatch(r"hover background color (.+)", line, re.IGNORECASE)
    if match:
        rules["_hover_background-color"] = resolve_color(match.group(1))
        return
    match = re.fullmatch(r"hover text color (.+)", line, re.IGNORECASE)
    if match:
        rules["_hover_color"] = resolve_color(match.group(1))
        return
    match = re.fullmatch(r"font size (.+)", line, re.IGNORECASE)
    if match:
        rules["font-size"] = resolve_size(match.group(1))
        return
    match = re.fullmatch(r"font family (.+)", line, re.IGNORECASE)
    if match:
        key = match.group(1).strip().lower()
        rules["font-family"] = FONTS.get(key, match.group(1).strip())
        return
    match = re.fullmatch(r"padding (.+)", line, re.IGNORECASE)
    if match:
        rules["padding"] = resolve_spacing(match.group(1))
        return
    match = re.fullmatch(r"padding (top|bottom|left|right) (.+)", line, re.IGNORECASE)
    if match:
        rules[f"padding-{match.group(1).lower()}"] = resolve_spacing(match.group(2))
        return
    match = re.fullmatch(r"margin (.+)", line, re.IGNORECASE)
    if match:
        rules["margin"] = resolve_spacing(match.group(1))
        return
    match = re.fullmatch(r"margin (top|bottom|left|right) (.+)", line, re.IGNORECASE)
    if match:
        rules[f"margin-{match.group(1).lower()}"] = resolve_spacing(match.group(2))
        return
    match = re.fullmatch(r"border color (.+)", line, re.IGNORECASE)
    if match:
        rules["border"] = f"2px solid {resolve_color(match.group(1))}"
        return
    match = re.fullmatch(r"border (thin|thick)", line, re.IGNORECASE)
    if match:
        size = "1px" if match.group(1).lower() == "thin" else "4px"
        rules["border"] = f"{size} solid currentColor"
        return
    match = re.fullmatch(r"width (.+)", line, re.IGNORECASE)
    if match:
        value = match.group(1).strip().lower()
        rules["width"] = "100%" if value == "full" else resolve_size(value)
        return
    match = re.fullmatch(r"max width (.+)", line, re.IGNORECASE)
    if match:
        value = match.group(1).strip().lower()
        presets = {"narrow": "600px", "medium": "900px", "wide": "1200px"}
        rules["max-width"] = presets.get(value, resolve_size(value))
        return
    match = re.fullmatch(r"gap (.+)", line, re.IGNORECASE)
    if match:
        rules["gap"] = resolve_spacing(match.group(1))
        return
    match = re.fullmatch(r"opacity (.+)", line, re.IGNORECASE)
    if match:
        value = match.group(1).strip().lower()
        presets = {"light": "0.85", "medium": "0.65", "heavy": "0.45"}
        rules["opacity"] = presets.get(value, value)
        return
    match = re.fullmatch(r"gradient from (.+) to (.+)", line, re.IGNORECASE)
    if match:
        start = resolve_color(match.group(1))
        end = resolve_color(match.group(2))
        rules["background"] = f"linear-gradient(135deg, {start}, {end})"
        return


def split_hover_rules(rules):
    normal = {}
    hover = {}
    for key, value in rules.items():
        if key.startswith("_hover_"):
            hover[key.replace("_hover_", "")] = value
        else:
            normal[key] = value
    return normal, hover


def rules_to_css(rules):
    return "; ".join(f"{prop}: {value}" for prop, value in rules.items())


def inline_style(rules, hover_rules=None):
    normal, inline_hover = split_hover_rules(rules)
    if hover_rules:
        inline_hover.update(hover_rules)
    css = rules_to_css(normal)
    if not css:
        return ""
    if inline_hover:
        return f' style="{css}"'
    return f' style="{css}"'


def split_block(block):
    style_lines = []
    content_lines = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if STYLE_LINE.match(line) or line.lower() == "when hover {":
            style_lines.append(line)
        else:
            content_lines.append(line)
    rules, hover = parse_rules("\n".join(style_lines))
    normal, extra_hover = split_hover_rules(rules)
    hover.update(extra_hover)
    return normal, hover, "\n".join(content_lines)


def split_box_block(block):
    style_lines = []
    content_lines = []
    past_styles = False
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not past_styles and (STYLE_LINE.match(line) or line.lower() == "when hover {"):
            style_lines.append(line)
        else:
            past_styles = True
            content_lines.append(line)
    rules, hover = parse_rules("\n".join(style_lines))
    normal, extra_hover = split_hover_rules(rules)
    hover.update(extra_hover)
    return normal, hover, "\n".join(content_lines)


def css_block(selector, rules, hover_rules=None):
    lines = []
    if rules:
        lines.append(f"{selector} {{ {rules_to_css(rules)}; }}")
    if hover_rules:
        lines.append(f"{selector}:hover {{ {rules_to_css(hover_rules)}; }}")
    return lines


def build_stylesheet(global_styles, looks):
    lines = [
        "/* KittyKat generated styles */",
        "* { box-sizing: border-box; }",
        "body { margin: 0; min-height: 100vh; }",
        "a { text-decoration: none; transition: color 0.2s ease, background-color 0.2s ease; }",
        "a:hover { text-decoration: underline; }",
        "button { border: none; cursor: pointer; padding: 10px 20px; font-size: 1rem; transition: all 0.2s ease; }",
        "button:hover { filter: brightness(1.08); }",
        "img { max-width: 100%; height: auto; }",
        "hr { border: none; border-top: 2px solid #e0e0e0; margin: 24px 0; }",
        "blockquote { margin: 16px 0; padding: 16px 24px; border-left: 4px solid #1a237e; background: #f8f8f8; }",
        ".kkat-badge { display: inline-block; padding: 4px 10px; border-radius: 999px; background: #1a237e; color: #fff; font-size: 0.8rem; font-weight: bold; }",
        "ul { margin: 0; padding-left: 24px; }",
        "li { margin: 6px 0; }",
        ".kkat-row { display: flex; flex-direction: row; gap: 1rem; align-items: center; }",
        ".kkat-column { display: flex; flex-direction: column; gap: 0.5rem; }",
    ]

    for target, block in global_styles.items():
        selector = STYLE_TARGETS.get(target)
        if not selector:
            print(f"WARNING: Unknown style target '{target}'")
            continue
        rules, hover = parse_rules(block)
        normal, extra_hover = split_hover_rules(rules)
        hover.update(extra_hover)
        lines.extend(css_block(selector, normal, hover))

    for name, block in looks.items():
        rules, hover = parse_rules(block)
        normal, extra_hover = split_hover_rules(rules)
        hover.update(extra_hover)
        lines.extend(css_block(f".kkat-{name}", normal, hover))
        if "color" in normal:
            lines.append(f".kkat-{name} a {{ color: {normal['color']}; }}")

    return "\n".join(lines) + "\n"
