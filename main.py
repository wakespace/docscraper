import os
import sys
import logging

# Ensure src directory is in path when running as a module or script
# This helps imports when running from different locations or via Github Actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config_parser import load_config
from src.scraper import scrape_documentation
from src.gdrive_client import update_drive_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_scraper(config_path="docs_links.json"):
    """
    Main orchestration function.
    Loads config, iterates over projects, scrapes them and updates Google Drive.
    """
    logger.info("Starting DocScraper workflow...")
    
    try:
        config = load_config(config_path)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    documents = config.get("documentacoes", [])
    logger.info(f"Found {len(documents)} documentations to process.")

    for doc in documents:
        nome = doc["nome"]
        url_base = doc["url_base"]
        folder_id = doc["drive_folder_id"]

        logger.info(f"--- Processing: {nome} ---")
        
        try:
            logger.info(f"Starting scrape for {url_base}")
            markdown_content = scrape_documentation(url_base)
            
            if not markdown_content:
                logger.warning(f"No content extracted for {nome}. Skipping document update.")
                continue
                
            logger.info(f"Extracted {len(markdown_content)} characters. Updating Google Drive folder...")
            update_drive_file(folder_id, nome, markdown_content)
            
            logger.info(f"Successfully processed {nome}.")
            
        except Exception as e:
            logger.error(f"Error processing {nome}: {e}")
            # Continue to next document despite error

    logger.info("DocScraper workflow completed.")

if __name__ == "__main__":
    run_scraper()
