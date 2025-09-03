from lib.github import download_github_repo
from lib.agent_template import (
    newsletter_writer_agent,
    newsletter_editor_agent,
    text_to_json_writer,
    diagram_generator_agent,
)
import asyncio
import google.generativeai as genai
from lib.file_reader import read_files_in_directory
from lib.notion import convert_json_to_notion_blocks, add_newsletter_to_notion
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from dotenv import load_dotenv
import json
import os

load_dotenv()
# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "x-api-key"


async def run_agent_with_gemini(agent_prompt, user_input):
    """Helper function to run agent prompts with Gemini API"""
    try:
        # Combine agent prompt with user input
        full_prompt = f"{agent_prompt}\n\nUser Input:\n{user_input}"

        # Generate content with Gemini
        response = model.generate_content(full_prompt)

        # Return response in a format similar to the original Runner
        class AgentResponse:
            def __init__(self, output):
                self.final_output = output

        return AgentResponse(response.text)
    except Exception as e:
        print(f"Gemini API error: {e}")
        raise


async def run_generate_newsletter(notion_id: str, repo_link: str):
    try:
        print("Downloading repository from:", repo_link, flush=True)

        directory = await download_github_repo(repo_link)

        files_string = read_files_in_directory(directory, ["md", "py"])

        user_prompt = f"""
        <files>
        {files_string}
        </files>
        <github link>
        {repo_link}
        </github link>
        """

        diagram_agent_output = await run_agent_with_gemini(
            diagram_generator_agent, user_prompt
        )

        # Extract Mermaid code and convert to PNG URL
        mermaid_code = diagram_agent_output.final_output.strip()
        if mermaid_code.startswith("```mermaid"):
            mermaid_code = mermaid_code[10:]  # Remove ```mermaid
        if mermaid_code.endswith("```"):
            mermaid_code = mermaid_code[:-3]  # Remove ```
        mermaid_code = mermaid_code.strip()

        # Clean up any problematic characters or syntax
        lines = mermaid_code.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("```"):
                # Remove any problematic characters
                line = line.replace("{", "[").replace("}", "]")  # Convert {} to []
                cleaned_lines.append(line)
        mermaid_code = "\n".join(cleaned_lines)

        print(f"Cleaned Mermaid code: {mermaid_code[:200]}...", flush=True)

        # Convert Mermaid to PNG URL using our tools
        from lib.tools import mermaid_to_png

        try:
            diagram_url_result = await mermaid_to_png(mermaid_code)
            if diagram_url_result:
                diagram_url = diagram_url_result
                print("Generated diagram URL:", diagram_url, flush=True)
            else:
                diagram_url = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop&crop=center"
                print("Diagram upload failed, using placeholder", flush=True)
        except Exception as e:
            print(f"Error generating diagram: {e}", flush=True)
            # Try a simpler diagram
            simple_diagram = """graph TD
    A[User] --> B[System]
    B --> C[Result]"""
            try:
                print("Attempting simple fallback diagram...", flush=True)
                diagram_url_result = await mermaid_to_png(simple_diagram)
                if diagram_url_result:
                    diagram_url = diagram_url_result
                    print("Fallback diagram successful:", diagram_url, flush=True)
                else:
                    diagram_url = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop&crop=center"
                    print("Using Unsplash placeholder", flush=True)
            except Exception as e2:
                print(f"Fallback diagram also failed: {e2}", flush=True)
                diagram_url = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop&crop=center"

        newsletter_draft = await run_agent_with_gemini(
            newsletter_writer_agent, user_prompt
        )

        edited_newsletter = await run_agent_with_gemini(
            newsletter_editor_agent, newsletter_draft.final_output
        )

        # # Convert to JSON Blocks

        json_blocks = await run_agent_with_gemini(
            text_to_json_writer, edited_newsletter.final_output
        )

        print("JSON blocks raw output:", json_blocks.final_output[:500], flush=True)

        # Parse the JSON string output and convert to NotionBlocks
        try:
            # Clean the JSON output by removing markdown code block markers
            json_output = json_blocks.final_output.strip()
            if json_output.startswith("```json"):
                json_output = json_output[7:]  # Remove ```json
            if json_output.endswith("```"):
                json_output = json_output[:-3]  # Remove ```
            json_output = json_output.strip()

            parsed_json = json.loads(json_output)
            # Import NotionBlocks from lib.notion
            from lib.notion import NotionBlocks

            notion_blocks_obj = NotionBlocks(**parsed_json)
            notion_blocks = convert_json_to_notion_blocks(
                notion_blocks_obj, diagram_url
            )
            add_newsletter_to_notion(notion_id, notion_blocks)
            print("Newsletter processing completed successfully!", flush=True)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON output: {e}", flush=True)
            print(f"Raw output: {json_blocks.final_output[:1000]}...", flush=True)
        except Exception as e:
            print(f"Error creating notion blocks: {e}", flush=True)
            if "parsed_json" in locals():
                print(
                    f"Parsed JSON keys: {list(parsed_json.keys()) if isinstance(parsed_json, dict) else 'Not a dict'}",
                    flush=True,
                )
    except Exception as e:
        print(f"Background task error: {e}", flush=True)


# FastAPI Setup

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()


def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key


@app.get("/")
def read_root(api_key: str = Depends(verify_api_key)):
    return {"message": "API is working"}


@app.post("/newsletter")
async def run_process(
    request: dict,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
):
    print(f"Received request: {request}", flush=True)

    properties = request.get("data", {}).get("properties", {})

    print(f"Properties: {properties}", flush=True)

    if not properties or "GitHub" not in properties:
        raise HTTPException(
            status_code=400, detail="Invalid request: 'GitHub' property is required"
        )

    repo_link = request["data"]["properties"]["GitHub"]["url"]
    page_id = request.get("data", {}).get("id", "")

    print(f"Processing Repo: {repo_link} for page ID: {page_id}")

    if not page_id:
        raise HTTPException(
            status_code=400, detail="Invalid request: 'Page ID' is required"
        )

    if not repo_link:
        raise HTTPException(
            status_code=400, detail="Invalid request: 'GitHub' property is required"
        )

    # Add the task to background processing
    background_tasks.add_task(run_generate_newsletter, page_id, repo_link)

    # Return immediately
    return {
        "status": "processing",
        "message": f"Generating Newsletter for GitHub repo: {repo_link}",
    }
