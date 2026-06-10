import os

OUTPUT_DIR = "dist"
PAGES_DIR = "pages"
STYLES_DIR = "styles"
ASSETS_DIR = "assets"
CSS_FILE = "site.css"

SOURCE_FILE = "site.kkat"


def dist_path(*parts):
    return os.path.join(OUTPUT_DIR, *parts)


def css_href(from_page):
    """Relative path to the stylesheet from a given page."""
    if from_page == "home":
        return f"{STYLES_DIR}/{CSS_FILE}"
    return f"../{STYLES_DIR}/{CSS_FILE}"


def page_href(from_page, target_page):
    """Relative path between pages in the dist folder."""
    if target_page == "home":
        return "../index.html" if from_page != "home" else "index.html"
    if from_page == "home":
        return f"{PAGES_DIR}/{target_page}.html"
    return f"{target_page}.html"
