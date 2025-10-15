#!/usr/bin/env python3
"""
Professional PDF Generator for MkDocs Documentation
Uses WeasyPrint to convert MkDocs HTML output to high-quality PDF

Usage:
    python3 generate_pdf.py [--output path/to/output.pdf]
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print("ERROR: WeasyPrint not installed!")
    print("Install with: pip install weasyprint")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: BeautifulSoup not installed!")
    print("Install with: pip install beautifulsoup4")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MkDocsPDFGenerator:
    """Generate professional PDF from MkDocs HTML output"""

    def __init__(self, site_dir: Path, output_path: Path):
        self.site_dir = site_dir.resolve()  # Convert to absolute path
        self.output_path = output_path.resolve()
        self.base_url = self.site_dir.as_uri() + "/"

    def get_navigation_pages(self) -> List[str]:
        """
        Extract navigation pages from index.html in correct order
        Returns list of relative URLs
        """
        index_path = self.site_dir / "index.html"
        if not index_path.exists():
            logger.error(f"Index file not found: {index_path}")
            return []

        with open(index_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        pages = []

        # Find navigation menu
        nav = soup.find("nav", class_="md-nav--primary")
        if not nav:
            logger.warning("Navigation not found, will use index only")
            return ["index.html"]

        # Extract all links from navigation
        for link in nav.find_all("a", class_="md-nav__link"):
            href = link.get("href", "")
            if href and not href.startswith("#") and not href.startswith("http"):
                # Clean up the href
                href = href.split("#")[0]  # Remove anchors
                if href not in pages:
                    pages.append(href)

        logger.info(f"Found {len(pages)} pages in navigation")
        return pages

    def extract_page_titles(self, pages: List[str]) -> List[dict]:
        """
        Extract titles from each page for Table of Contents
        Returns list of dicts with page info: {path, title, id}
        """
        page_titles = []

        for page_path in pages:
            # Handle directory URLs
            if page_path == "." or page_path == "":
                page_path = "index.html"
            elif page_path.endswith("/"):
                page_path = page_path + "index.html"
            elif not page_path.endswith(".html"):
                page_path = page_path + "/index.html"

            full_path = self.site_dir / page_path

            if not full_path.exists():
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")

                # Try to get title from h1 in article or from page title
                title = None
                content = (
                    soup.find("article")
                    or soup.find("main")
                    or soup.find(class_="md-content__inner")
                )

                if content:
                    h1 = content.find("h1")
                    if h1:
                        title = h1.get_text(strip=True)

                # Fallback to page title
                if not title:
                    title_tag = soup.find("title")
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                        # Remove site name suffix if present
                        title = title.split(" - ")[0]

                if not title:
                    title = page_path.replace("/index.html", "").replace(".html", "")

                # Create unique ID for anchor
                page_id = f"page-{len(page_titles) + 1}"

                page_titles.append({"path": page_path, "title": title, "id": page_id})

            except Exception as e:
                logger.warning(f"Could not extract title from {page_path}: {e}")

        return page_titles

    def create_toc_html(self, page_titles: List[dict]) -> str:
        """
        Create Table of Contents HTML
        """
        toc_parts = []
        toc_parts.append('<div class="toc-page">')
        toc_parts.append('<h1 class="toc-title">📑 Sumário</h1>')
        toc_parts.append(
            '<p class="toc-intro">Navegue pelo manual completo do Sistema de Certificados Pint of Science Brasil. '
            "Clique em qualquer item para ir diretamente à seção desejada.</p>"
        )

        # Group pages by section (detect from path)
        sections = {
            "participantes": {"title": "👥 Para Participantes", "pages": []},
            "coordenadores": {"title": "👨‍💼 Para Coordenadores", "pages": []},
            "administradores": {"title": "⚙️ Para Administradores", "pages": []},
            "configuracao": {"title": "🔧 Configuração", "pages": []},
            "outros": {"title": "📚 Informações Gerais", "pages": []},
        }

        for page_info in page_titles:
            path = page_info["path"]

            # Categorize page
            if "participantes" in path:
                sections["participantes"]["pages"].append(page_info)
            elif "coordenadores" in path:
                sections["coordenadores"]["pages"].append(page_info)
            elif "administradores" in path:
                sections["administradores"]["pages"].append(page_info)
            elif "configuracao" in path:
                sections["configuracao"]["pages"].append(page_info)
            else:
                sections["outros"]["pages"].append(page_info)

        # Generate TOC HTML
        for section_key, section_data in sections.items():
            if section_data["pages"]:
                toc_parts.append(f'<div class="toc-section">')
                toc_parts.append(
                    f'<h2 class="toc-section-title">{section_data["title"]}</h2>'
                )
                toc_parts.append('<ul class="toc-items">')

                for page_info in section_data["pages"]:
                    toc_parts.append(
                        f'<li><a href="#{page_info["id"]}">{page_info["title"]}</a></li>'
                    )

                toc_parts.append("</ul>")
                toc_parts.append("</div>")

        toc_parts.append("</div>")

        return "\n".join(toc_parts)

    def create_combined_html(self, pages: List[str]) -> str:
        """
        Combine multiple HTML pages into single document for PDF generation
        Preserves styling and content from all pages
        """
        combined_parts = []

        # HTML header with proper styling
        combined_parts.append(
            """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manual do Usuário - Pint of Science Brasil</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Roboto+Condensed:wght@400;700&family=Roboto+Mono:wght@400;500&display=swap');

        /* Page setup */
        @page {
            size: A4;
            margin: 20mm 15mm;

            @top-center {
                content: "Manual do Usuário - Pint of Science Brasil";
                font-size: 9pt;
                color: #666;
            }

            @bottom-right {
                content: "Página " counter(page);
                font-size: 9pt;
                color: #666;
            }
        }

        @page :first {
            @top-center { content: none; }
            @bottom-right { content: none; }
        }

        /* Base styling */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.6;
            color: #333;
            background: white;
        }

        /* Typography */
        h1 {
            font-family: 'Roboto Condensed', sans-serif;
            font-size: 24pt;
            font-weight: 700;
            color: #d84315;
            margin: 20pt 0 12pt 0;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        h2 {
            font-family: 'Roboto Condensed', sans-serif;
            font-size: 18pt;
            font-weight: 700;
            color: #e91e63;
            margin: 16pt 0 10pt 0;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        h3 {
            font-family: 'Roboto Condensed', sans-serif;
            font-size: 14pt;
            font-weight: 700;
            color: #c2185b;
            margin: 12pt 0 8pt 0;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        h4 {
            font-size: 12pt;
            font-weight: 600;
            color: #555;
            margin: 10pt 0 6pt 0;
            page-break-after: avoid;
        }

        p {
            margin-bottom: 8pt;
            text-align: justify;
            orphans: 2;
            widows: 2;
        }

        /* Lists */
        ul, ol {
            margin: 8pt 0 8pt 20pt;
            padding-left: 10pt;
        }

        li {
            margin-bottom: 4pt;
            line-height: 1.5;
        }

        ul ul, ol ul, ul ol, ol ol {
            margin-top: 4pt;
            margin-bottom: 4pt;
        }

        /* Code blocks */
        pre {
            font-family: 'Roboto Mono', 'Courier New', monospace;
            font-size: 8.5pt;
            line-height: 1.4;
            padding: 10pt;
            margin: 10pt 0;
            background-color: #f8f8f8;
            border: 1pt solid #ddd;
            border-radius: 3pt;
            page-break-inside: avoid;
            overflow-wrap: break-word;
            white-space: pre-wrap;
        }

        code {
            font-family: 'Roboto Mono', 'Courier New', monospace;
            font-size: 9pt;
            padding: 2pt 4pt;
            background-color: #f5f5f5;
            border-radius: 2pt;
            color: #d84315;
        }

        pre code {
            padding: 0;
            background: none;
            color: inherit;
        }

        /* Tables */
        table {
            width: 100%;
            margin: 10pt 0;
            border-collapse: collapse;
            font-size: 9pt;
            page-break-inside: auto;
        }

        thead {
            display: table-header-group;
        }

        tr {
            page-break-inside: avoid;
        }

        th, td {
            padding: 6pt 8pt;
            border: 1pt solid #ddd;
            text-align: left;
            vertical-align: top;
        }

        th {
            background-color: #f5f5f5;
            font-weight: 600;
            color: #d84315;
        }

        /* Admonitions */
        .admonition {
            padding: 10pt;
            margin: 12pt 0;
            border-left: 4pt solid #448aff;
            background-color: #e3f2fd;
            page-break-inside: avoid;
        }

        .admonition-title {
            font-weight: 700;
            font-size: 10.5pt;
            margin-bottom: 6pt;
            color: #1976d2;
        }

        .admonition.note {
            border-left-color: #448aff;
            background-color: #e3f2fd;
        }

        .admonition.tip {
            border-left-color: #00bfa5;
            background-color: #e0f2f1;
        }

        .admonition.warning {
            border-left-color: #ff9100;
            background-color: #fff3e0;
        }

        .admonition.danger {
            border-left-color: #ff5252;
            background-color: #ffebee;
        }

        /* Links */
        a {
            color: #1976d2;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        /* Style for external links */
        a[href^="http"]::after {
            content: " 🔗";
            font-size: 0.8em;
            color: #666;
        }

        /* Style for internal anchor links */
        a[href^="#"] {
            color: #d84315;
            text-decoration: underline;
            text-decoration-style: dotted;
        }

        /* Hide navigation elements and symbols */
        .headerlink,
        a.headerlink,
        .md-content__button,
        .md-icon,
        .md-nav__icon,
        svg,
        details,
        summary,
        .md-button,
        .md-top,
        .twemoji,
        .octicon,
        [class*="octicons-"],
        [class*="md-icon"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
        }

        /* Hide any remaining anchor symbols */
        a[href^="#"]::after {
            content: "" !important;
        }

        /* Style for inter-page references (converted to strong) */
        strong {
            font-weight: 600;
            color: #555;
        }

        /* Ensure no icon SVGs appear */
        img[src*="octicon"],
        img[src*="emoji"],
        span[class*="icon"] {
            display: none !important;
        }

        /* Images */
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 10pt auto;
            page-break-inside: avoid;
        }

        /* Blockquotes */
        blockquote {
            margin: 10pt 0;
            padding-left: 15pt;
            border-left: 3pt solid #ddd;
            color: #666;
            font-style: italic;
        }

        /* Horizontal rules */
        hr {
            border: none;
            border-top: 1pt solid #ddd;
            margin: 12pt 0;
        }

        /* Page sections */
        .page-section {
            page-break-before: always;
        }

        .page-section:first-child {
            page-break-before: auto;
        }

        /* Hide navigation elements */
        nav, .md-header, .md-footer, .md-sidebar, .md-search, .md-tabs {
            display: none !important;
        }

        /* Cover page */
        .cover-page {
            page-break-after: always;
            text-align: center;
            padding-top: 100pt;
        }

        .cover-title {
            font-size: 36pt;
            font-weight: 700;
            color: #d84315;
            margin-bottom: 20pt;
        }

        .cover-subtitle {
            font-size: 18pt;
            color: #e91e63;
            margin-bottom: 40pt;
        }

        .cover-info {
            font-size: 12pt;
            color: #666;
            margin-top: 60pt;
        }

        /* Table of Contents */
        .toc-page {
            page-break-after: always;
            padding: 30pt 40pt;
        }

        .toc-title {
            font-size: 28pt;
            font-weight: 700;
            color: #d84315;
            margin-bottom: 25pt;
            text-align: center;
            border-bottom: 3pt solid #e91e63;
            padding-bottom: 15pt;
        }

        .toc-section {
            margin-bottom: 18pt;
        }

        .toc-section-title {
            font-size: 13pt;
            font-weight: 700;
            color: #e91e63;
            margin-bottom: 10pt;
            padding: 5pt 0;
            border-left: 4pt solid #d84315;
            padding-left: 10pt;
            background-color: #fff5f5;
        }

        .toc-items {
            list-style: none;
            padding-left: 0;
            margin-left: 20pt;
            counter-reset: toc-counter;
        }

        .toc-items li {
            margin-bottom: 6pt;
            padding-left: 25pt;
            position: relative;
            counter-increment: toc-counter;
        }

        .toc-items li::before {
            content: counter(toc-counter) ".";
            position: absolute;
            left: 0;
            color: #d84315;
            font-weight: 600;
            font-size: 9pt;
        }

        .toc-items a {
            color: #333;
            text-decoration: none;
            font-size: 10pt;
            display: block;
            padding: 4pt 8pt;
            border-radius: 2pt;
            transition: all 0.2s;
        }

        .toc-items a:hover {
            background-color: #fff3e0;
            color: #d84315;
            text-decoration: none;
            padding-left: 12pt;
        }

        .toc-intro {
            font-size: 10pt;
            color: #666;
            text-align: center;
            margin-bottom: 25pt;
            font-style: italic;
            padding: 0 60pt;
        }
    </style>
</head>
<body>
"""
        )

        # Cover page
        combined_parts.append(
            """
<div class="cover-page">
    <h1 class="cover-title">Manual do Usuário</h1>
    <p class="cover-subtitle">Sistema de Certificados<br>Pint of Science Brasil</p>
    <div class="cover-info">
        <p>Versão 2025</p>
        <p>Documentação Completa do Sistema</p>
    </div>
</div>
"""
        )

        # Table of Contents
        logger.info("Generating Table of Contents...")
        page_titles = self.extract_page_titles(pages)
        toc_html = self.create_toc_html(page_titles)
        combined_parts.append(toc_html)

        # Process each page
        for i, page_path in enumerate(pages, 1):
            # Handle directory URLs - MkDocs uses index.html
            if page_path == "." or page_path == "":
                page_path = "index.html"
            elif page_path.endswith("/"):
                page_path = page_path + "index.html"
            elif not page_path.endswith(".html"):
                page_path = page_path + "/index.html"

            full_path = self.site_dir / page_path

            if not full_path.exists():
                logger.warning(f"Page not found: {page_path}")
                continue

            logger.info(f"Processing page {i}/{len(pages)}: {page_path}")

            # Get page ID from page_titles
            page_id = f"page-{i}"
            for pt in page_titles:
                if pt["path"] == page_path:
                    page_id = pt["id"]
                    break

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")

                # Extract main content
                content = (
                    soup.find("article")
                    or soup.find("main")
                    or soup.find(class_="md-content__inner")
                )

                if content:
                    # Remove unwanted navigation elements
                    for element in content.find_all(["nav", "header", "footer"]):
                        element.decompose()

                    # Remove SVG icons (arrows, etc) - MUST be done before processing links
                    for svg in content.find_all("svg"):
                        svg.decompose()

                    # Remove twemoji spans (emoji icons from Material theme)
                    for emoji in content.find_all("span", class_="twemoji"):
                        emoji.decompose()

                    # Remove Material icon elements
                    for icon in content.find_all(
                        class_=lambda x: x and ("md-icon" in x or "octicon" in x)
                    ):
                        icon.decompose()

                    # Remove details/summary elements (collapse/expand navigation)
                    for details in content.find_all("details"):
                        details.decompose()

                    # Remove navigation arrows and buttons
                    for nav_element in content.find_all(
                        class_=[
                            "md-footer",
                            "md-nav__link--next",
                            "md-nav__link--prev",
                            "md-nav__icon",
                            "md-icon",
                            "md-button",
                            "md-content__button",
                        ]
                    ):
                        nav_element.decompose()

                    # Remove permalink symbols (¶) from headings
                    for permalink in content.find_all("a", class_="headerlink"):
                        permalink.decompose()

                    # Remove links with only symbol content (no text) or just whitespace
                    for link in content.find_all("a"):
                        text = link.get_text(strip=True)
                        # Only remove if it's JUST a symbol with no meaningful text
                        if (
                            text in ["¶", "¶​", "#", "↗", "⚓", "»", "«", "→", "←", ""]
                            or len(text) == 0
                        ):
                            link.decompose()

                    # Process internal links - keep text but fix hrefs
                    for link in content.find_all("a", href=True):
                        href = link["href"]

                        # Skip external links (keep as-is)
                        if href.startswith(("http://", "https://", "mailto:")):
                            continue

                        # Skip already processed anchors (keep as-is)
                        if href.startswith("#"):
                            continue

                        # For internal links with anchors, extract just the anchor
                        # e.g., "../solucao-problemas/#problema-1" -> "#problema-1"
                        if "#" in href:
                            anchor = href.split("#", 1)[1]
                            link["href"] = f"#{anchor}"
                        else:
                            # For links without anchors (inter-page navigation),
                            # convert to plain text with emphasis
                            # Keep the text but remove the non-functional link
                            link.name = "strong"
                            del link["href"]

                    # Add page section with ID for TOC linking
                    combined_parts.append(f'<div class="page-section" id="{page_id}">')
                    combined_parts.append(str(content))
                    combined_parts.append("</div>")
                else:
                    logger.warning(f"No content found in {page_path}")

            except Exception as e:
                logger.error(f"Error processing {page_path}: {e}")

        # Close HTML
        combined_parts.append(
            """
</body>
</html>
"""
        )

        return "\n".join(combined_parts)

    def generate_pdf(self) -> bool:
        """
        Generate PDF from MkDocs site
        Returns True if successful
        """
        try:
            logger.info("Starting PDF generation...")

            # Get navigation pages
            pages = self.get_navigation_pages()
            if not pages:
                logger.error("No pages found to process")
                return False

            logger.info(f"Processing {len(pages)} pages...")

            # Create combined HTML
            html_content = self.create_combined_html(pages)

            # Configure fonts
            font_config = FontConfiguration()

            # Generate PDF
            logger.info("Rendering PDF with WeasyPrint...")
            html = HTML(string=html_content, base_url=self.base_url)

            # Render to PDF
            html.write_pdf(self.output_path, font_config=font_config)

            # Check file size
            size_mb = self.output_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ PDF generated successfully: {self.output_path}")
            logger.info(f"📄 File size: {size_mb:.2f} MB")
            logger.info(f"📊 Pages processed: {len(pages)}")

            return True

        except Exception as e:
            logger.error(f"❌ Error generating PDF: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate professional PDF from MkDocs documentation"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("docs-site/pdf/manual-completo-pint-brasil.pdf"),
        help="Output PDF path (default: docs-site/pdf/manual-completo-pint-brasil.pdf)",
    )
    parser.add_argument(
        "--site-dir",
        "-s",
        type=Path,
        default=Path("docs-site"),
        help="MkDocs site directory (default: docs-site)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate site directory
    if not args.site_dir.exists():
        logger.error(f"Site directory not found: {args.site_dir}")
        logger.info("Run 'mkdocs build' first to generate the site")
        sys.exit(1)

    # Create output directory
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Generate PDF
    generator = MkDocsPDFGenerator(args.site_dir, args.output)
    success = generator.generate_pdf()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
