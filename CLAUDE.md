# Claude.md - Website Management Guide

## Overview

This is a personal research blog and portfolio for Wenrui Xu, showcasing ML interpretability research at Anthropic. This document serves as:
- Instructions for Claude to help manage the website
- Reference documentation for workflow and conventions

## Claude's Primary Responsibilities

### 1. Convert Markdown Writings to HTML Pages
- Take Markdown files and convert them to HTML using the existing Pandoc template
- Follow the established pattern from existing articles
- Ensure MathJax support is working for mathematical notation
- Adjust image widths as needed

### 2. Launch Local Preview Server
- Set up a local HTTP server for previewing changes
- Typical command: `python3 -m http.server 8000`
- Access at: `http://localhost:8000`

### 3. Fine-tune Styles
- Modify `styles.css` when requested
- Maintain responsive design (320px-1200px width)
- Keep consistent with existing aesthetic (Baskerville typography, minimalist design)

## Workflow Documentation

### Current Manual Workflow (from original readme.md)

1. **Compile Notion MD files to HTML:**
   ```bash
   pandoc input_name.md --template=template.html -o output_name.html --mathjax --metadata title="title"
   ```

2. **Manually specify image widths** in the resulting HTML

### Automated Workflow (Claude-assisted)

#### Converting New Articles
1. User provides Markdown file (with images exported from Notion or written directly)
2. Claude runs Pandoc conversion using the `writings/template.html`
3. Claude adjusts image widths in the generated HTML
4. Claude collaborates with user on one-sentence summary, then adds the article to `writings.html`

#### Local Preview
1. Claude launches local server: `python3 -m http.server 8000`
2. User reviews at `http://localhost:8000`
3. Claude makes adjustments as requested
4. User commits when satisfied

#### Style Modifications
1. User describes desired styling change
2. Claude modifies `styles.css`
3. Changes preview automatically in local server
4. Iterate until satisfied

## Technical Reference

### File Structure
```
wxu26.github.io/
├── index.html              # Home page
├── about.html             # Biography and career
├── writings.html          # Research articles hub
├── header.html            # Shared navigation
├── footer.html            # Shared footer
├── styles.css             # Main stylesheet
├── include.js             # Component loading utility
├── profile.jpg            # Author photo
├── eddy.jpg              # Cat photo
├── .nojekyll             # GitHub Pages config
├── .gitignore            # Git config
├── scripts/              # Build utilities
│   └── generate_toc.py    # Auto-generate table of contents
└── writings/             # Research content
    ├── template.html      # Pandoc template
    ├── *.md              # Markdown sources
    ├── *.html            # Compiled articles
    └── */                # Image directories for each article
```

### Key Files

**Template:** `writings/template.html`
- Includes header/footer via `data-include`
- MathJax configuration for mathematical rendering
- Metadata placeholders: `$title$`, `$body$`

**Stylesheet:** `styles.css`
- Global typography: Baskerville serif, 18px base
- Layout classes:
  - `.content` - Narrow layout (max-width: 700px) for regular pages
  - `.content-article` - Wider layout (max-width: 900px) for blog posts
  - `.main-content` - Flexible container (max-width: 1200px)
- Responsive images: `max-width: 100%`, `height: auto`

**Component System:**
- Uses `data-include` attributes with `include.js`
- Header and footer automatically injected on all pages

### Styling Conventions

- **Colors:** Black text on white background, blue links (#007bff)
- **Typography:** Baskerville for body, system fonts fallback
- **Spacing:** Consistent margins, comfortable line-height (1.6)
- **Responsive:** Flexible layouts that adapt 320px-1200px
- **Images:** Centered, responsive, with subtle borders on article images

## Common Tasks

### Adding a New Article (Interactive Workflow)

1. **User adds new content to `writings/` folder:**
   - Single Markdown file (e.g., `new_article.md`), OR
   - Folder containing Markdown file + images/attachments (exported from Notion)

2. **Claude identifies the new file** and suggests better filename:
   - Follow snake_case convention (e.g., `managing_claude.md`)
   - Present 2-3 options for user to choose from

3. **User confirms:**
   - Filename choice
   - Page title (what appears in browser tab)

4. **Claude executes:**
   - Rename file to chosen name
   - Convert to HTML: `pandoc filename.md --template=template.html -o filename.html --mathjax --metadata title="Page Title"`
   - Generate TOC (if article has 3+ section headings): `python3 scripts/generate_toc.py writings/filename.html`
   - Launch preview server from project root: `python3 -m http.server 8000`

5. **Claude suggests one-sentence summary:**
   - User provides preferred summary or edits Claude's suggestion
   - Claude adds entry to `writings.html` at the top (most recent)

6. **User previews at `http://localhost:8000/writings/filename.html`:**
   - Test all links and formatting
   - Request any adjustments (image widths, styling, etc.)

7. **Adjust image widths if needed** (common widths: 400px, 600px, 800px)

### Updating Existing Content

1. Edit the `.md` source file in `writings/`
2. Re-run Pandoc conversion
3. Re-run TOC generation if headings changed: `python3 scripts/generate_toc.py writings/filename.html`
4. Preview changes locally
5. Commit when satisfied

### Table of Contents Generation

The TOC script (`scripts/generate_toc.py`) auto-generates a floating sidebar TOC for articles:

```bash
python3 scripts/generate_toc.py writings/article.html
```

**Rules:**
- TOC is only generated if the article has **3 or more section headings** (excluding title)
- The script auto-detects the highest heading level used (h1, h2, or h3) and treats it as top-level
- Running the script multiple times is safe - it removes any existing TOC before generating a new one
- TOC appears as a floating sidebar on wide screens (≥1400px) and is hidden on narrow screens

### Modifying Global Styles

1. Edit `styles.css`
2. Test changes across multiple pages (index, about, writings, sample article)
3. Verify responsive behavior (resize browser window)
4. Commit when all pages look correct

### Previewing Changes Locally

```bash
# From project root
python3 -m http.server 8000

# Or use port 3000
python3 -m http.server 3000

# Access at http://localhost:8000 (or specified port)
```

## Common Pitfalls

### Server Location
- **CRITICAL:** Always run server from project root (`/Users/wenruixu/Documents/wxu26.github.io/`)
- **NOT** from `writings/` folder - this causes 404 errors
- Correct command: `python3 -m http.server 8000` (from root)

### Naming Conventions
- **Filename:** Use snake_case (e.g., `managing_claude.md`)
- Follow existing pattern: `feature_geometry.md`, `sparse_superposition.md`
- Avoid spaces and special characters in filenames

### Title vs Heading
- **Page title** (browser tab): Set via `--metadata title="Managing Claude"`
- **Article heading** (in HTML body): Can be longer, e.g., "Claude is meant to be managed, not used"
- These are different and serve different purposes

### File Organization
- **HTML files always go directly in `writings/`** (not in subfolders)
- Single MD files go directly in `writings/`
- MD + images: Can be in a subfolder within `writings/` (Notion export pattern), but the generated HTML should be moved to `writings/`
- Keep Markdown source files for future edits

## Session Wrap-up

When the user indicates they want to end the session (e.g., "let's wrap up", "done for now", "that's all"):
1. **Stop any running servers** launched during the session (e.g., `python3 -m http.server`)
2. **Check for uncommitted changes** with `git status` and remind the user if there are any

## Notes

- **GitHub Pages:** Uses `.nojekyll` to serve static HTML without Jekyll processing
- **Image optimization:** Large images (~1MB+) may benefit from compression before upload
- **MathJax:** Mathematical notation uses LaTeX syntax, renders client-side
- **Git workflow:** Commit after each complete article or significant style change
- **Browser testing:** Preview in multiple browsers when making CSS changes

---

*This document is maintained to facilitate collaboration between Wenrui and Claude on website updates.*
