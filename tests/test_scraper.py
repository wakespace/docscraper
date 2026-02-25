import pytest
import responses
from src.scraper import fetch_and_clean_html, convert_to_markdown, scrape_documentation, clean_text, chunk_text

def test_clean_text():
    text_with_extra_newlines = "Line 1\n\n\n\nLine 2\n\n\nLine 3"
    cleaned = clean_text(text_with_extra_newlines)
    assert cleaned == "Line 1\n\nLine 2\n\nLine 3"

def test_chunk_text():
    # 10 words per line, 10 lines = 100 words total
    text = "\n".join(["word " * 9 + "word" for _ in range(10)])
    
    # Should not chunk if under max_words
    chunks = chunk_text(text, max_words=200)
    assert len(chunks) == 1
    assert chunks[0] == text
    
    # Needs 3 chunks if max_words=45 (each chunk can only fit 4 lines / 40 words)
    # Chunk 1: Lines 1,2,3,4 (40 words)
    # Chunk 2: Lines 5,6,7,8 (40 words)
    # Chunk 3: Lines 9,10 (20 words)
    chunks = chunk_text(text, max_words=45)
    assert len(chunks) == 3
    assert len(chunks[0].split()) == 40
    assert len(chunks[1].split()) == 40
    assert len(chunks[2].split()) == 20


@pytest.fixture
def mock_html():
    return """
        <head><title>Test Doc</title></head>
        <body>
            <header>Header Content</header>
            <nav>Nav Content</nav>
            <main>
                <h1>Main Title</h1>
                <p>This is the important content.</p>
                <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" alt="base64 image"/>
                <svg width="100" height="100"><circle cx="50" cy="50" r="40" stroke="green" stroke-width="4" fill="yellow" /></svg>
                <script>console.log("This should be removed");</script>
                <noscript>Your browser does not support JavaScript!</noscript>
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
        assert "data:image/png;base64" not in cleaned_html
        assert "circle cx" not in cleaned_html
        assert "This should be removed" not in cleaned_html
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
