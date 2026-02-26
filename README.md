# DocScraper

DocScraper is a Python-based tool designed to scrape SaaS documentation sites, extract their content as Markdown, and automatically update Google Drive files with the extracted text. This project was developed following TDD principles.

## Features

- Configurable targets using `docs_links.json`.
- Extracts and cleans HTML content into Markdown format.
- Automatically handles Google Docs updates (including splitting large contents).
- Individual GitHub Actions workflows to scrape targets separately and concurrently on schedules.

## Prerequisites

- Python 3.12+
- Google Cloud Platform (GCP) credentials (Client ID, Secret, and Refresh Token) with access to the Google Drive API.

## Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/wakespace/docscraper.git
   cd docscraper
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Configuration

Update the `docs_links.json` file to define your scraping targets.

Example:
```json
{
  "documentacoes": [
    {
      "nome": "OpenRouter",
      "url_base": "https://openrouter.ai/docs",
      "drive_folder_id": "YOUR_DRIVE_FOLDER_ID",
      "ignore_paths": ["/sdks/", "/components/", "/operations/"]
    },
    {
      "nome": "OpenAI API",
      "url_base": "https://developers.openai.com/api/docs",
      "drive_folder_id": "YOUR_DRIVE_FOLDER_ID",
      "ignore_paths": []
    }
  ]
}
```

## Running Locally

To run the scraper manually, you need to set up the appropriate GCP credentials as environment variables:

```bash
export GCP_CLIENT_ID="your_client_id"
export GCP_CLIENT_SECRET="your_client_secret"
export GCP_REFRESH_TOKEN="your_refresh_token"
```

You can run the main script to process **all targets**:

```bash
python main.py
```

### Scraping a Specific Target

If you only want to scrape a specific target defined in your `docs_links.json` file, use the `--target` argument:

```bash
python main.py --target "OpenRouter"
```

This ensures only the specified documentation target is processed, skipping the others. Use the exact `nome` field given in your `docs_links.json`.

## GitHub Actions Automated Workflows

DocScraper runs automated jobs inside GitHub Actions. To prevent scraping failures from affecting other targets, we use separated, independent workflow files located in `.github/workflows/`:

- **update_openrouter.yml**: Scrapes exclusively `"OpenRouter"`. Scheduled to run every Monday at `03:00 UTC`.
- **update_openai.yml**: Scrapes exclusively `"OpenAI API"`. Scheduled to run every Monday at `04:00 UTC`.

You can also trigger any of these workflows manually from the "Actions" tab in the GitHub repository.

## Testing

DocScraper includes a suite of unit tests. Run them using `pytest` within your activated virtual environment:

```bash
PYTHONPATH=. pytest
```
