import pytest
import responses
from src.scraper import fetch_and_clean_html, convert_to_markdown, scrape_documentation

@pytest.fixture
def mock_html():
    return """
    <html>
        <head><title>Test Doc</title></head>
        <body>
            <header>Header Content</header>
            <nav>Nav Content</nav>
            <main>
                <h1>Main Title</h1>
                <p>This is the important content.</p>
                <a href="/docs/page2">Page 2</a>
                <a href="https://external.com">External</a>
            </main>
            <aside>Sidebar Content</aside>
            <footer>Footer Content</footer>
        </body>
    </html>
    """

def test_fetch_and_clean_html_success(mock_html):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://test.com/docs/page1",
            body=mock_html,
            status=200,
            content_type="text/html"
        )

        cleaned_html = fetch_and_clean_html("https://test.com/docs/page1")
        assert "Header Content" not in cleaned_html
        assert "Nav Content" not in cleaned_html
        assert "Footer Content" not in cleaned_html
        assert "Sidebar Content" not in cleaned_html
        assert "Main Title" in cleaned_html
        assert "important content" in cleaned_html

def test_convert_to_markdown():
    cleaned_html = "<h1>Title</h1><p>Text</p>"
    markdown = convert_to_markdown(cleaned_html)
    assert "# Title" in markdown
    assert "Text" in markdown

def test_scrape_documentation_single_page(mock_html):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://test.com/docs",
            body=mock_html,
            status=200,
            content_type="text/html"
        )
        
        # Test scraping with recursive flag false or mocking out the recursive part
        # Actually scrape_documentation should probably handle multiple pages if required,
        # but for simplicity let's test a linear scrape.
        # Given the requirements: "scraper must map internal links belonging to documentation"
        
        # Let's add a second page to the mock
        page2_html = "<html><body><main><h2>Page 2 Content</h2></main></body></html>"
        rsps.add(
            responses.GET,
            "https://test.com/docs/page2",
            body=page2_html,
            status=200,
            content_type="text/html"
        )

        # External link should not be fetched
        
        result_md = scrape_documentation("https://test.com/docs")
        
        assert "# Main Title" in result_md
        assert "important content" in result_md
        assert "## Page 2 Content" in result_md
