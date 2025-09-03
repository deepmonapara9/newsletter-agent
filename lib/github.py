import os
import tempfile
import aiohttp
import asyncio
from urllib.parse import urlparse
import zipfile
import ssl
import certifi


async def download_github_repo(repo_url, dest_folder="/tmp/newsletter_repos"):
    """
    Asynchronously downloads the contents of a public GitHub repository as a zip file and extracts it to dest_folder.
    Args:
            repo_url (str): The URL of the GitHub repository.
            dest_folder (str): The folder to extract the repo into (default: '/tmp/newsletter_repos').
    Returns:
            str: Path to the extracted repository folder.
    """
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL")
    owner, repo = path_parts[0], path_parts[1].replace(".git", "")
    zip_urls = [
        f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip",
        f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip",
        f"https://github.com/{owner}/{repo}/archive/HEAD.zip",
    ]
    os.makedirs(dest_folder, exist_ok=True)
    last_error = None

    # Create SSL context for secure connections
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    for zip_url in zip_urls:
        try:
            print(f"Trying to download from: {zip_url}", flush=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                timeout = aiohttp.ClientTimeout(total=30)
                async with session.get(zip_url, timeout=timeout) as response:
                    print(f"Response status: {response.status}", flush=True)
                    if response.status == 200:
                        print("Download successful, extracting...", flush=True)
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".zip"
                        ) as tmp_zip:
                            while True:
                                chunk = await response.content.read(8192)
                                if not chunk:
                                    break
                                tmp_zip.write(chunk)
                            tmp_zip_path = tmp_zip.name
                        with zipfile.ZipFile(tmp_zip_path, "r") as zip_ref:
                            zip_ref.extractall(dest_folder)
                        os.remove(tmp_zip_path)
                        extracted_folder = os.path.join(
                            dest_folder, os.listdir(dest_folder)[0]
                        )
                        print(f"Extracted to: {extracted_folder}", flush=True)
                        return extracted_folder
                    else:
                        print(
                            f"HTTP {response.status}: {await response.text()}",
                            flush=True,
                        )
        except Exception as e:
            print(f"Error downloading from {zip_url}: {str(e)}", flush=True)
            last_error = e
            continue
    raise Exception(
        f"Failed to download repo from {repo_url}. Last error: {last_error}"
    )
