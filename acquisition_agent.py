import json
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import logging

# --- Configuration ---
TARGETS_FILE = 'targets.json'
DATA_DIR = 'data'
REPOS_DIR = os.path.join(DATA_DIR, 'repos')
SCRAPED_DIR = os.path.join(DATA_DIR, 'scraped')

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_dir_exists(path):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Created directory: {path}")

def handle_git_target(target):
    """
    Handles the cloning of a git repository.
    Supports normal clones and sparse checkouts.
    """
    logging.info(f"Processing git target: {target['name']}")
    repo_url = target['url']

    # Auto-generate destination if not provided
    if 'destination' not in target:
        safe_name = target['name'].lower().replace(' ', '_').replace('.', '_')
        target['destination'] = f"repos/{safe_name}"

    destination_path = os.path.join(DATA_DIR, target['destination'])

    if os.path.exists(destination_path):
        logging.info(f"Repository '{target['name']}' already exists at '{destination_path}'. Skipping clone.")
        # In a more advanced version, you could add `git pull` logic here.
        return

    ensure_dir_exists(os.path.dirname(destination_path))
    
    sparse_checkout_paths = target.get('sparse_checkout')

    try:
        if sparse_checkout_paths:
            logging.info(f"Performing sparse checkout for paths: {sparse_checkout_paths}")
            # 1. Init a bare repo
            subprocess.run(['git', 'init', '--bare', destination_path], check=True)
            # 2. Add remote
            subprocess.run(['git', '-C', destination_path, 'remote', 'add', 'origin', repo_url], check=True)
            # 3. Enable sparse checkout
            subprocess.run(['git', '-C', destination_path, 'config', 'core.sparsecheckout', 'true'], check=True)
            # 4. Define sparse checkout paths
            sparse_checkout_file = os.path.join(destination_path, '.git', 'info', 'sparse-checkout')
            with open(sparse_checkout_file, 'w') as f:
                if isinstance(sparse_checkout_paths, list):
                    for path in sparse_checkout_paths:
                        f.write(f"{path}\n")
                else:
                    f.write(f"{sparse_checkout_paths}\n")
            # 5. Fetch and pull the default branch
            logging.info("Fetching from remote...")
            subprocess.run(['git', '-C', destination_path, 'fetch', 'origin', 'master'], check=True) # Try master
            subprocess.run(['git', '-C', destination_path, 'fetch', 'origin', 'main'], check=True) # Try main
            logging.info("Pulling sparse data...")
            # Attempt to checkout main, fallback to master
            try:
                subprocess.run(['git', '-C', destination_path, 'checkout', 'main'], check=True)
            except subprocess.CalledProcessError:
                logging.warning("Could not checkout 'main', trying 'master'.")
                subprocess.run(['git', '-C', destination_path, 'checkout', 'master'], check=True)

        else:
            logging.info(f"Performing a full clone for '{target['name']}'...")
            subprocess.run(['git', 'clone', '--depth', '1', repo_url, destination_path], check=True)
        
        logging.info(f"Successfully cloned '{target['name']}' to '{destination_path}'")

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to process git target '{target['name']}': {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred for git target '{target['name']}': {e}")


def handle_web_scrape_target(target):
    """
    Performs a basic web scrape of a single page.
    A more advanced version would crawl links recursively.
    """
    logging.info(f"Processing web_scrape target: {target['name']}")
    url = target['url']

    # Auto-generate destination if not provided
    if 'destination' not in target:
        safe_name = target['name'].lower().replace(' ', '_').replace('.', '_')
        target['destination'] = f"scraped/{safe_name}"

    destination_dir = os.path.join(DATA_DIR, target['destination'])
    ensure_dir_exists(destination_dir)
    
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Heuristic to find main content. This may need tuning per site.
        content_selectors = ['main', '[role="main"]', '#content', '#main-content', '.main-content']
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            content = soup.body

        text = content.get_text(separator='\n', strip=True)
        
        # Use the last part of the URL path as a filename if it's not a root path
        filename = os.path.basename(url.rstrip('/')) + '.md'
        if not filename or filename == '.md':
             filename = "index.md"

        filepath = os.path.join(destination_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Scraped Content from: {url}\n\n")
            f.write(text)
            
        logging.info(f"Successfully scraped '{url}' to '{filepath}'")

    except requests.RequestException as e:
        logging.error(f"Failed to fetch URL '{url}': {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred for web_scrape target '{target['name']}': {e}")


def main():
    """
    Main function to drive the acquisition agent.
    """
    logging.info("--- Starting Acquisition Agent ---")
    
    if not os.path.exists(TARGETS_FILE):
        logging.error(f"Targets file not found: {TARGETS_FILE}")
        return

    with open(TARGETS_FILE, 'r') as f:
        targets = json.load(f)

    ensure_dir_exists(DATA_DIR)
    ensure_dir_exists(REPOS_DIR)
    ensure_dir_exists(SCRAPED_DIR)

    for target in targets:
        if target.get('type') == 'git':
            handle_git_target(target)
        elif target.get('type') == 'web_scrape':
            handle_web_scrape_target(target)
        else:
            logging.warning(f"Unknown target type: {target.get('type')} for target '{target['name']}'")
        logging.info("-" * 20)

    logging.info("--- Acquisition Agent Finished ---")


if __name__ == "__main__":
    main()
