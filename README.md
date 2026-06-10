# KittyKat

**Build websites with plain English.**

KittyKat is a simple language for creating static websites. You write one file (`site.kkat`), use readable words like `heading("Hello")` and `background color blue`, and KittyKat turns it into real HTML and CSS.

No HTML tags to memorize. No separate CSS files to manage. Easy enough for a child to learn, powerful enough for real projects.

## Install KittyKat

### Requirements
- Python 3.10 or newer

### Windows
1. Download the latest release ZIP
2. Extract to `C:\KittyKat`
3. Add `C:\KittyKat` to your PATH
4. Open a new terminal and run: `kkat help`

### Mac / Linux
1. Download and extract KittyKat
2. Add the folder to PATH in ~/.bashrc or ~/.zshrc:
   export PATH="$PATH:/path/to/KittyKat"
3. Run: python3 kkat.py help
   (or create a `kkat` shell script)

---

## Quick start

```bash
# Create a new project
kkat new mysite
cd mysite

# Live preview (reads site.kkat directly)
kkat serve

# Or build static files into dist/
kkat build
kkat preview
```

Open **http://localhost:3000** in your browser.

---

## How it works

```
site.kkat  ──►  KittyKat compiler  ──►  dist/
                                         ├── index.html
                                         ├── pages/
                                         ├── styles/site.css
                                         └── assets/
```

1. You write your website in **site.kkat**
2. KittyKat compiles it into a **dist/** folder
3. You open the site in a browser, or deploy it anywhere

You can also run **`kkat serve`**, which reads `site.kkat` directly — no build step needed while you work.

---

## Project structure

```
myproject/
├── site.kkat          ← your website (the only file you edit)
├── dist/              ← generated output (created by kkat build)
│   ├── index.html     ← home page
│   ├── pages/         ← all other pages
│   ├── styles/
│   │   └── site.css   ← all styles in one file
│   └── assets/        ← put images here
├── kkat.py            ← CLI tool
├── compiler.py        ← language compiler
├── styles.py          ← plain-English style engine
├── server.py          ← live runtime server
├── api/index.py       ← Vercel serverless handler
└── vercel.json        ← Vercel config
```

---

## The site.kkat file

Every KittyKat project has one source file wrapped in `<kkat>` tags:

```kkat
<kkat>

style page {
    background color cream
    font family sans
}

page("home") {
    title("My Website")
    heading("Hello!")
    paragraph("Welcome to my site.")
}

page("about") {
    title("About")
    heading("About me")
}

</kkat>
```

### File layout (top to bottom)

| Section | Purpose |
|---------|---------|
| `style page { }` | Global styles for the whole site |
| `look("name") { }` | Reusable style presets |
| `component("name") { }` | Reusable content blocks |
| `page("name") { }` | Your actual pages |

---

## Pages

Each `page()` block becomes one HTML file.

```kkat
page("home") {
    title("My Cool Site")          // browser tab title
    meta("description", "A site")  // SEO meta tag
    heading("Welcome")
}

page("about") {
    title("About")
    heading("About us")
}
```

| Page name | Output file |
|-----------|-------------|
| `home` | `dist/index.html` |
| `about` | `dist/pages/about.html` |
| `contact` | `dist/pages/contact.html` |

If you don't declare any pages, everything becomes a single home page automatically.

---

## Elements

Elements are the building blocks of your pages. Each one is plain English.

### Text

```kkat
heading("Big title")              // <h1>
subheading("Section title")       // <h2>
paragraph("A sentence.")          // <p>
quote("A wise saying.")           // <blockquote>
badge("New")                      // small label pill
divider                           // horizontal line
```

Add inline styles with curly braces:

```kkat
heading("Centered title") {
    center
    color navy
}
```

### Links and navigation

```kkat
link("Google", "https://google.com")     // external link
pagelink("About", "about")               // internal page link (auto paths)
```

Use **`pagelink()`** for links between your pages — KittyKat generates the correct relative URL automatically.

### Images

Put images in `dist/assets/`, then reference them by filename:

```kkat
image("My logo", "logo.png")
```

### Buttons

```kkat
button {
    text("Click me")
    goto("about")              // links to pages/about.html
    background color green
    text color white
    rounded
}
```

### Layout containers

```kkat
box {
    background color white
    padding large
    rounded
    shadow

    heading("Inside the box")
    paragraph("Grouped content.")
}

row {
    paragraph("Left")
    paragraph("Right")
}

column {
    heading("Top")
    paragraph("Bottom")
}
```

### Lists

```kkat
list {
    item("First thing")
    item("Second thing")
    item("Third thing")
}
```

### Reusable components

Define once, use everywhere:

```kkat
component("nav") {
    pagelink("Home", "home")
    pagelink("About", "about")
}

page("home") {
    styled("navbar") {
        use("nav")
    }
    heading("Welcome")
}
```

### Meta tags (SEO)

```kkat
page("home") {
    meta("description", "My awesome website")
    meta("author", "Your Name")
    meta("theme color", "#1a237e")
}
```

---

## Styling

KittyKat styling uses **plain English words**. No CSS syntax required.

### Three ways to style

**1. Global styles** — affect every element of a type:

```kkat
style page {
    background color cream
    text color dark gray
    font family sans
    padding large
}

style heading {
    color navy
    font size huge
}

style button {
    background color navy
    text color white
    rounded
}
```

Global targets: `page`, `heading`, `subheading`, `paragraph`, `button`, `link`, `image`, `list`, `quote`, `badge`

**2. Named looks** — reusable style presets:

```kkat
look("card") {
    background color white
    padding large
    rounded
    shadow
}

styled("card") {
    heading("Card title")
    paragraph("Card content.")
}
```

**3. Inline styles** — style one element:

```kkat
heading("Special") {
    color coral
    center
    italic
}
```

### Colors

```
white, black, red, orange, yellow, green, teal, blue, navy,
purple, pink, gray, light gray, dark gray, coral, cream,
lavender, mint, sky
```

Or hex codes: `background color #ff6b6b`

### Typography

| Word | Effect |
|------|--------|
| `font size tiny/small/medium/large/huge` | Text size |
| `font family sans/serif/mono` | Font type |
| `bold` | Bold text |
| `italic` | Italic text |
| `underline` | Underlined text |
| `center` / `left` / `right` | Text alignment |

### Spacing

| Word | Effect |
|------|--------|
| `padding small/medium/large` | Inner spacing |
| `padding top 20` | Top padding only |
| `margin medium` | Outer spacing |
| `gap medium` | Space between flex children |

### Shape and effects

| Word | Effect |
|------|--------|
| `rounded` | Rounded corners |
| `shadow` | Drop shadow |
| `soft shadow` | Lighter shadow |
| `border thin/thick` | Border line |
| `border color navy` | Colored border |
| `opacity light/medium/heavy` | Transparency |

### Layout

| Word | Effect |
|------|--------|
| `spread horizontally` | Row layout (flex) |
| `stack vertically` | Column layout (flex) |
| `space between` | Spread items apart |
| `space evenly` | Even spacing |
| `space around` | Space around items |
| `align center/start/end` | Align items |
| `width full` | Full width |
| `max width narrow/medium/wide` | Limit width |
| `sticky top` | Sticky navbar |

### Gradients

```kkat
look("hero") {
    gradient from navy to purple
    text color white
    padding huge
    center
}
```

### Hover effects

```kkat
style button {
    background color navy
    when hover {
        background color coral
    }
}

style link {
    when hover {
        text color coral
    }
}
```

Or shorthand:

```kkat
button {
    text("Click")
    hover background color green
}
```

### Transitions

```kkat
style button {
    transition smooth
}
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `kkat new <name>` | Create a new project folder |
| `kkat build` | Compile site.kkat → dist/ folder |
| `kkat serve` | Live server reading site.kkat directly |
| `kkat preview` | Build dist/ and serve static files |
| `kkat version` | Show version |
| `kkat help` | Show help |

### serve vs preview vs build

- **`kkat serve`** — reads `site.kkat` on every request. Best while editing. No dist/ needed.
- **`kkat build`** — writes organized files to `dist/`. Best for deployment.
- **`kkat preview`** — builds dist/ then serves it as static files. Best for testing the final output.

---

## Deploying

### Option 1: Static deploy (Netlify, GitHub Pages, etc.)

```bash
kkat build
```

Upload the **`dist/`** folder. That's your complete website.

### Option 2: Vercel (runs from site.kkat source)

Push your project to GitHub with these files:

- `site.kkat`
- `compiler.py`, `styles.py`, `config.py`
- `api/index.py`
- `vercel.json`

Vercel compiles your site on each request — you deploy the **source**, not just the generated HTML.

The included `vercel.json` routes all traffic through the Python handler in `api/index.py`.

---

## Complete example

```kkat
<kkat>

style page {
    background color light gray
    font family sans
    padding large
}

style heading {
    color navy
}

style button {
    background color navy
    text color white
    rounded
    when hover {
        background color coral
    }
}

look("navbar") {
    background color navy
    text color white
    padding medium
    spread horizontally
    rounded
    sticky top
}

component("nav") {
    pagelink("Home", "home")
    pagelink("About", "about")
}

page("home") {
    title("My Site")
    meta("description", "Built with KittyKat")

    styled("navbar") {
        use("nav")
    }

    box {
        background color white
        padding large
        rounded
        shadow
        max width medium

        heading("Welcome") { center }
        paragraph("Built with KittyKat!") { center }

        button {
            text("Learn more")
            goto("about")
        }
    }
}

page("about") {
    title("About")

    styled("navbar") {
        use("nav")
    }

    heading("About this site")
    paragraph("Made with plain English.")
}

</kkat>
```

---

## Language reference (cheat sheet)

```
STRUCTURE          CONTENT              STYLING
─────────          ───────              ───────
<kkat>             heading("text")      background color blue
style page { }     subheading("text")   text color white
look("name") { }   paragraph("text")    font size large
component("n"){}   quote("text")        font family sans
page("name") { }   badge("text")        padding / margin
                   link("t", "url")      rounded / shadow
                   pagelink("t", "pg")   center / bold
                   image("alt", "file")  spread horizontally
                   button { text goto }  gradient from X to Y
                   box / row / column     when hover { ... }
                   list { item() }        sticky top
                   divider                gap / opacity
                   use("component")       transition smooth
                   styled("look") { }
                   meta("key", "value")
                   title("tab title")
```

---

## License

KittyKat is open source. Build something fun.
