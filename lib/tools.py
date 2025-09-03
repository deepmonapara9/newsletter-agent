import mermaid as md
import os, shutil, subprocess, tempfile
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
from uuid import uuid4
from lib.s3 import upload_png_to_s3

from dotenv import load_dotenv

load_dotenv()

MERMAID_HTML = """
<!doctype html>
<html>
  <body><div id="app"></div></body>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    window.mermaidReady = (async () => {
      mermaid.initialize({ startOnLoad: false });
      return mermaid;
    })();
  </script>
</html>
"""


async def mermaid_to_svg(mermaid_code: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page()
        await page.set_content(MERMAID_HTML, wait_until="networkidle")
        # Validate + render
        await page.wait_for_function("() => window.mermaidReady !== undefined")
        svg = await page.evaluate(
            """
      async (code) => {
        const mermaid = await window.mermaidReady;
        try {
          // parse to validate first
          await mermaid.parse(code);
          const { svg } = await mermaid.render('g1', code);
          return svg;
        } catch (e) {
          return JSON.stringify({ error: String(e) });
        }
      }
    """,
            mermaid_code,
        )
        await browser.close()
        return svg


def save_svg(svg_text: str, out_svg: str):
    from pathlib import Path

    Path(out_svg).parent.mkdir(parents=True, exist_ok=True)
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write(svg_text)


async def mermaid_to_png(mermaid_code: str, width: int = 1024):
    """Generate a PNG image from Mermaid code using Mermaid Ink API.

    Args:
    - mermaid_code (str): The Mermaid code to convert.
    - width (int): The width of the output image (default: 1024).

    Returns:
    - str: The URL of the generated PNG file
    """
    try:
        import base64
        import urllib.parse
        import requests
        import tempfile

        # Use Mermaid Ink service - a public service that converts mermaid to images
        encoded = base64.b64encode(mermaid_code.encode("utf-8")).decode("ascii")
        ink_url = f"https://mermaid.ink/img/{encoded}?type=png&width={width}"

        print(f"✅ Generating diagram via Mermaid Ink: {ink_url[:100]}...", flush=True)

        # Download the image from Mermaid Ink
        response = requests.get(ink_url, timeout=30)
        if response.status_code == 200:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            print("✅ Downloaded diagram from Mermaid Ink, uploading to S3...", flush=True)
            
            # Upload to S3
            s3_url = upload_png_to_s3(temp_file_path, f"diagram-{str(uuid4())[:8]}")
            
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            if s3_url:
                print(f"✅ S3 upload successful: {s3_url[:100]}...", flush=True)
                return s3_url
            else:
                print("❌ S3 upload failed, using placeholder", flush=True)
                raise RuntimeError("S3 upload failed")
        else:
            print(f"❌ Mermaid Ink failed with status {response.status_code}", flush=True)
            raise RuntimeError(f"Mermaid Ink returned {response.status_code}")

    except Exception as e:
        print(f"Diagram generation failed: {e}", flush=True)
        # Return a placeholder diagram from Unsplash
        return "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop&crop=center"
