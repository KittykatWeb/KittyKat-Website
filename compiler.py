import os
import re

from config import (
    ASSETS_DIR,
    CSS_FILE,
    OUTPUT_DIR,
    PAGES_DIR,
    SOURCE_FILE,
    STYLES_DIR,
    css_href,
    dist_path,
    page_href,
)
from styles import (
    build_stylesheet,
    inline_style,
    parse_rules,
    split_block,
    split_box_block,
    split_hover_rules,
)


def skip_space(text, index):
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def extract_brace_block(text, open_brace_index):
    depth = 0
    i = open_brace_index

    while i < len(text):
        char = text[i]

        if char == '"':
            i += 1
            while i < len(text):
                if text[i] == "\\" and i + 1 < len(text):
                    i += 2
                    continue
                if text[i] == '"':
                    break
                i += 1
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_index + 1 : i], i + 1

        i += 1

    return text[open_brace_index + 1 :], len(text)


def extract_named_brace_blocks(code, opener, flags=0):
    found = {}
    pattern = re.compile(opener, flags)
    pos = 0
    remove_ranges = []

    while pos < len(code):
        match = pattern.search(code, pos)
        if not match:
            break

        name = match.group(1)
        inner, end = extract_brace_block(code, match.end() - 1)
        found[name] = inner
        remove_ranges.append((match.start(), end))
        pos = end

    stripped = code
    for start, end in reversed(remove_ranges):
        stripped = stripped[:start] + stripped[end:]

    return found, stripped


def parse_source(code):
    start = code.find("<kkat>")
    end = code.rfind("</kkat>")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Missing or invalid <kkat> block")

    code = code[start + len("<kkat>") : end]

    looks, code = extract_named_brace_blocks(
        code, r'(?:^|\n)\s*look\("(.+?)"\)\s*\{', re.MULTILINE
    )

    global_styles = {}
    style_pattern = re.compile(r"(?:^|\n)\s*style\s+(\w+)\s*\{", re.MULTILINE)
    style_remove_ranges = []
    pos = 0

    while pos < len(code):
        match = style_pattern.search(code, pos)
        if not match:
            break

        target = match.group(1)
        inner, end = extract_brace_block(code, match.end() - 1)
        global_styles[target] = inner
        style_remove_ranges.append((match.start(), end))
        pos = end

    for start, end in reversed(style_remove_ranges):
        code = code[:start] + code[end:]

    components, code = extract_named_brace_blocks(
        code, r'(?:^|\n)\s*component\("(.+?)"\)\s*\{', re.MULTILINE
    )

    pages, leftover = extract_named_brace_blocks(
        code, r'(?:^|\n)\s*page\("(.+?)"\)\s*\{', re.MULTILINE
    )

    if not pages and leftover.strip():
        pages["home"] = leftover

    if not pages:
        raise ValueError("No pages found in site.kkat")

    return {
        "looks": looks,
        "global_styles": global_styles,
        "components": components,
        "pages": pages,
    }


def element_style(content, pos, n):
    if pos < n and content[pos] == "{":
        style_block, end = extract_brace_block(content, pos)
        rules, hover = parse_rules(style_block)
        normal, extra_hover = split_hover_rules(rules)
        hover.update(extra_hover)
        return inline_style(normal, hover), end
    return "", pos


def render_button_block(block, current_page):
    rules, hover, content = split_block(block)

    text_match = re.search(r'text\("(.+?)"\)', content)
    goto_match = re.search(r'goto\("(.+?)"\)', content)

    if not text_match:
        return ""

    text = text_match.group(1)
    style = inline_style(rules, hover)
    button = f"<button{style}>{text}</button>"

    if goto_match:
        url = page_href(current_page, goto_match.group(1))
        return f'<a href="{url}">{button}</a>\n'

    return f"{button}\n"


def render_list_block(block, current_page, components, looks):
    rules, hover, content = split_block(block)
    style = inline_style(rules, hover)
    items = re.findall(r'item\("(.+?)"\)', content)
    items_html = "".join(f"<li>{item}</li>\n" for item in items)
    return f"<ul{style}>{items_html}</ul>\n"


def render_content(content, components, looks, current_page):
    html = ""
    i = 0
    n = len(content)

    while i < n:
        while i < n and content[i].isspace():
            i += 1

        if i >= n:
            break

        remaining = content[i:]

        match = re.match(r'styled\("(.+?)"\)\s*\{', remaining)
        if match:
            name = match.group(1)
            inner, end = extract_brace_block(content, i + match.end() - 1)
            if name not in looks:
                print(f"WARNING: Unknown look '{name}'")
                html += render_content(inner, components, looks, current_page)
            else:
                inner_html = render_content(inner, components, looks, current_page)
                html += f'<div class="kkat-{name}">{inner_html}</div>\n'
            i = end
            continue

        match = re.match(r"box\s*\{", remaining)
        if match:
            inner, end = extract_brace_block(content, i + match.end() - 1)
            rules, hover, inner_content = split_box_block(inner)
            inner_html = render_content(inner_content, components, looks, current_page)
            style = inline_style(rules, hover)
            html += f"<div{style}>{inner_html}</div>\n"
            i = end
            continue

        match = re.match(r"row\s*\{", remaining)
        if match:
            inner, end = extract_brace_block(content, i + match.end() - 1)
            rules, hover, inner_content = split_box_block(inner)
            inner_html = render_content(inner_content, components, looks, current_page)
            style = inline_style(rules, hover)
            html += f'<div class="kkat-row"{style}>{inner_html}</div>\n'
            i = end
            continue

        match = re.match(r"column\s*\{", remaining)
        if match:
            inner, end = extract_brace_block(content, i + match.end() - 1)
            rules, hover, inner_content = split_box_block(inner)
            inner_html = render_content(inner_content, components, looks, current_page)
            style = inline_style(rules, hover)
            html += f'<div class="kkat-column"{style}>{inner_html}</div>\n'
            i = end
            continue

        match = re.match(r"list\s*\{", remaining)
        if match:
            inner, end = extract_brace_block(content, i + match.end() - 1)
            html += render_list_block(inner, current_page, components, looks)
            i = end
            continue

        match = re.match(r'use\("(.+?)"\)', remaining)
        if match:
            name = match.group(1)
            if name not in components:
                print(f"WARNING: Unknown component '{name}'")
            else:
                html += render_content(components[name], components, looks, current_page)
            i += match.end()
            continue

        match = re.match(r'pagelink\("(.+?)",\s*"(.+?)"\)', remaining)
        if match:
            text, target = match.group(1), match.group(2)
            pos = skip_space(content, i + match.end())
            style, i = element_style(content, pos, n)
            url = page_href(current_page, target)
            html += f'<a href="{url}"{style}>{text}</a>\n'
            continue

        match = re.match(r'heading\("(.+?)"\)', remaining)
        if match:
            text = match.group(1)
            pos = skip_space(content, i + match.end())
            style, i = element_style(content, pos, n)
            html += f"<h1{style}>{text}</h1>\n"
            continue

        match = re.match(r'subheading\("(.+?)"\)', remaining)
        if match:
            text = match.group(1)
            pos = skip_space(content, i + match.end())
            style, i = element_style(content, pos, n)
            html += f"<h2{style}>{text}</h2>\n"
            continue

        match = re.match(r'paragraph\("(.+?)"\)', remaining)
        if match:
            text = match.group(1)
            pos = skip_space(content, i + match.end())
            style, i = element_style(content, pos, n)
            html += f"<p{style}>{text}</p>\n"
            continue

        match = re.match(r'quote\("(.+?)"\)', remaining)
        if match:
            text = match.group(1)
            pos = skip_space(content, i + match.end())
            style, i = element_style(content, pos, n)
            html += f"<blockquote{style}>{text}</blockquote>\n"
            continue

        match = re.match(r'badge\("(.+?)"\)', remaining)
        if match:
            text = match.group(1)
            pos = skip_space(content, i + match.end())
            style, i = element_style(content, pos, n)
            html += f'<span class="kkat-badge"{style}>{text}</span>\n'
            continue

        match = re.match(r'link\("(.+?)",\s*"(.+?)"\)', remaining)
        if match:
            text, url = match.group(1), match.group(2)
            pos = skip_space(content, i + match.end())
            style, i = element_style(content, pos, n)
            html += f'<a href="{url}"{style}>{text}</a>\n'
            continue

        match = re.match(r'image\("(.+?)",\s*"(.+?)"\)', remaining)
        if match:
            alt, src = match.group(1), match.group(2)
            pos = skip_space(content, i + match.end())
            style, i = element_style(content, pos, n)
            if not src.startswith(("http://", "https://", "/")):
                if current_page == "home":
                    src = f"{ASSETS_DIR}/{src}"
                else:
                    src = f"../{ASSETS_DIR}/{src}"
            html += f'<img src="{src}" alt="{alt}"{style}>\n'
            continue

        if re.match(r"divider", remaining):
            html += "<hr>\n"
            i += len("divider")
            continue

        match = re.match(r"button\s*\{", remaining)
        if match:
            inner, end = extract_brace_block(content, i + match.end() - 1)
            html += render_button_block(inner, current_page)
            i = end
            continue

        i += 1

    return html


def page_meta(page_content):
    meta_tags = []

    for key, value in re.findall(r'meta\("(.+?)",\s*"(.+?)"\)', page_content):
        if key.lower() == "description":
            meta_tags.append(f'<meta name="description" content="{value}">')
        elif key.lower() == "author":
            meta_tags.append(f'<meta name="author" content="{value}">')
        elif key.lower() == "theme color":
            meta_tags.append(f'<meta name="theme-color" content="{value}">')
        else:
            meta_tags.append(f'<meta name="{key}" content="{value}">')

    return "\n".join(meta_tags)


def render_page(page_name, page_content, components, looks, stylesheet):
    title_match = re.search(r'title\("(.+?)"\)', page_content)
    title = title_match.group(1) if title_match else page_name
    body = render_content(page_content, components, looks, page_name)
    meta = page_meta(page_content)
    css_link = css_href(page_name)

    meta_block = f"{meta}\n" if meta else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{meta_block}<title>{title}</title>
<link rel="stylesheet" href="{css_link}">
</head>
<body>
{body}</body>
</html>
"""


def compile_site(source=SOURCE_FILE):
    if not os.path.exists(source):
        raise FileNotFoundError(source)

    with open(source, "r", encoding="utf-8") as file:
        source_code = file.read()

    parsed = parse_source(source_code)
    stylesheet = build_stylesheet(parsed["global_styles"], parsed["looks"])

    pages_html = {}
    for page_name, page_content in parsed["pages"].items():
        pages_html[page_name] = render_page(
            page_name,
            page_content,
            parsed["components"],
            parsed["looks"],
            stylesheet,
        )

    return {
        "pages": pages_html,
        "stylesheet": stylesheet,
        "page_names": list(parsed["pages"].keys()),
    }


def resolve_route(path):
    path = path.split("?", 1)[0].split("#", 1)[0]
    path = path.strip("/")

    if path in ("", "index.html"):
        return "home"

    if path.endswith(".html"):
        path = path[:-5]

    if path.startswith(f"{PAGES_DIR}/"):
        path = path[len(PAGES_DIR) + 1 :]

    if path == "home":
        return "home"

    return path


def compile_route(source=SOURCE_FILE, path="/"):
    compiled = compile_site(source)
    page_name = resolve_route(path)

    if page_name not in compiled["pages"]:
        return None, compiled

    return compiled["pages"][page_name], compiled


def write_build(compiled, output_dir=OUTPUT_DIR):
    pages_dir = os.path.join(output_dir, PAGES_DIR)
    styles_dir = os.path.join(output_dir, STYLES_DIR)
    assets_dir = os.path.join(output_dir, ASSETS_DIR)

    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(styles_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    for folder in (output_dir, pages_dir):
        for filename in os.listdir(folder):
            if filename.endswith(".html"):
                os.remove(os.path.join(folder, filename))

    css_path = os.path.join(styles_dir, CSS_FILE)
    with open(css_path, "w", encoding="utf-8") as file:
        file.write(compiled["stylesheet"])

    for page_name, html in compiled["pages"].items():
        if page_name == "home":
            with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as file:
                file.write(html)
        else:
            with open(os.path.join(pages_dir, f"{page_name}.html"), "w", encoding="utf-8") as file:
                file.write(html)


def build(source=SOURCE_FILE, output_dir=OUTPUT_DIR):
    try:
        compiled = compile_site(source)
    except FileNotFoundError:
        print(f"ERROR: '{source}' not found")
        print("Run 'kkat new mysite' to create a project, or add a site.kkat file.")
        return False
    except ValueError as error:
        print(f"ERROR: {error}")
        return False

    write_build(compiled, output_dir)

    page_count = len(compiled["pages"])
    print(f"Website built successfully! ({page_count} page(s))")
    print(f"Output folder: {output_dir}/")
    print(f"  index.html")
    print(f"  {PAGES_DIR}/   (other pages)")
    print(f"  {STYLES_DIR}/{CSS_FILE}")
    print(f"  {ASSETS_DIR}/  (put images here)")
    return True
