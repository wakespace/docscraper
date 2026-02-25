import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import markdownify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_internal_link(base_url: str, link_url: str) -> bool:
    """Check if a given link belongs to the same domain as the base URL."""
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(link_url).netloc
    return not link_domain or link_domain == base_domain

def fetch_and_clean_html(url: str) -> str:
    """Fetches a URL and removes semantic non-content tags."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove unwanted tags
    for tag in soup(["nav", "footer", "header", "aside", "script", "style"]):
        tag.decompose()

    # Try to find a main content container, fallback to body
    main_content = soup.find("main") or soup.find("article") or soup.find("body") or soup

    return str(main_content)

def convert_to_markdown(html_content: str) -> str:
    """Converts HTML string to Markdown."""
    if not html_content:
        return ""
    # Strip whitespace, ignore images/links if needed, but keeping simple for now
    return markdownify.markdownify(html_content, heading_style="ATX").strip()

def scrape_documentation(base_url: str) -> str:
    """
    Crawls the documentation starting at base_url.
    Finds internal links, visits them, and aggregates their Markdown content.
    """
    visited = set()
    to_visit = [base_url]
    aggregated_markdown = []

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
            
        visited.add(current_url)
        logger.info(f"Scraping: {current_url}")

        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {current_url}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find new links before decomposing tags
        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']
            # Ignore anchor links
            if href.startswith('#'):
                continue
                
            full_url = urljoin(current_url, href)
            # Ensure it's part of the base documentation (not just same domain, but under the base path)
            if full_url.startswith(base_url) and full_url not in visited and full_url not in to_visit:
                to_visit.append(full_url)

        # Clean HTML
        for tag in soup(["nav", "footer", "header", "aside", "script", "style"]):
            tag.decompose()

        main_content = soup.find("main") or soup.find("article") or soup.find("body") or soup
        
        md_content = markdownify.markdownify(str(main_content), heading_style="ATX")
        if md_content.strip():
            aggregated_markdown.append(f"<!-- Source: {current_url} -->\n" + md_content.strip())

    return "\n\n---\n\n".join(aggregated_markdown)
