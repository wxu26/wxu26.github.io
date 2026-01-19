#!/usr/bin/env python3
"""
Generate table of contents for HTML articles.

Usage:
    python scripts/generate_toc.py writings/article.html

This script:
1. Removes any existing TOC (nav.toc)
2. Finds all h1/h2/h3 headings with id attributes (excluding the title h1)
3. Detects the highest heading level used and treats it as top-level
4. Generates a nested TOC structure
5. Inserts it before </main>
"""

import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup


def generate_toc(html_path: str) -> None:
    path = Path(html_path)
    if not path.exists():
        print(f"Error: {html_path} not found")
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup just to extract headings
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the content-article div
    content_div = soup.find('div', class_='content-article')
    if not content_div:
        print("Error: No .content-article div found")
        sys.exit(1)

    # Find all headings with ids (h1, h2, h3)
    headings = content_div.find_all(['h1', 'h2', 'h3'], id=True)

    if not headings:
        print("No headings with IDs found")
        sys.exit(0)

    # Skip the first h1 if it's the title (usually the first heading)
    first_h1 = content_div.find('h1', id=True)
    if first_h1 and headings and headings[0] == first_h1:
        headings = headings[1:]

    if not headings:
        print("No headings to include in TOC (only title found)")
        sys.exit(0)

    if len(headings) < 3:
        print(f"Only {len(headings)} headings found - need at least 3 for TOC")
        sys.exit(0)

    # Determine the highest (smallest number) heading level used
    levels = [int(h.name[1]) for h in headings]
    min_level = min(levels)

    # Build TOC HTML manually for cleaner output
    def build_toc_html(headings, min_level):
        lines = ['        <nav class="toc">', '            <ul>']
        prev_level = min_level

        for i, heading in enumerate(headings):
            level = int(heading.name[1])
            heading_id = heading.get('id')
            heading_text = ' '.join(heading.get_text(strip=True).split())

            # Calculate relative depth
            depth = level - min_level

            # Close lists if going up
            while prev_level > level:
                lines.append('                ' + '    ' * (prev_level - min_level - 1) + '</ul>')
                lines.append('                ' + '    ' * (prev_level - min_level - 1) + '</li>')
                prev_level -= 1

            # Open new sublist if going deeper
            if level > prev_level:
                lines.append('                ' + '    ' * (prev_level - min_level) + '<ul>')

            # Close previous li if at same level (not first item)
            elif i > 0 and level == prev_level:
                pass  # li was already closed or doesn't need closing

            # Add the item
            indent = '                ' + '    ' * depth
            lines.append(f'{indent}<li><a href="#{heading_id}">{heading_text}</a>')

            # Check if next heading is deeper (don't close li yet)
            next_level = int(headings[i + 1].name[1]) if i + 1 < len(headings) else min_level
            if next_level <= level:
                lines[-1] += '</li>'

            prev_level = level

        # Close remaining open tags
        while prev_level > min_level:
            lines.append('                ' + '    ' * (prev_level - min_level - 1) + '</ul>')
            lines.append('                ' + '    ' * (prev_level - min_level - 1) + '</li>')
            prev_level -= 1

        lines.append('            </ul>')
        lines.append('        </nav>')
        return '\n'.join(lines)

    toc_html = build_toc_html(headings, min_level)

    # Remove existing TOC using regex (preserves formatting of rest of document)
    html_content, n_removed = re.subn(
        r'\s*<nav class="toc">.*?</nav>\s*',
        '\n',
        html_content,
        flags=re.DOTALL
    )
    if n_removed:
        print("Removed existing TOC")

    # Insert new TOC before </main>
    html_content = re.sub(
        r'(</main>)',
        f'\n{toc_html}\n    \\1',
        html_content
    )

    # Write back
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated TOC with {len(headings)} entries")
    print(f"Heading levels used: h{min_level}-h{max(levels)} (normalized to top-level)")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_toc.py <html_file>")
        sys.exit(1)

    generate_toc(sys.argv[1])
