import requests
from typing import Optional, Union
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Literal
import json

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")


class NotionBlock(BaseModel):
    type: Literal[
        "paragraph",
        "heading1",
        "heading_2",
        "link_preview",
        "image",
        "numbered_list_item",
    ]
    text: Optional[str] = None
    url: Optional[str] = None
    is_code: bool = False


class NotionBlocks(BaseModel):
    blocks: list[NotionBlock]


def convert_json_to_notion_blocks(
    content_blocks: NotionBlocks, diagram_url: str
) -> list[dict]:

    notion_blocks = []

    for item in content_blocks.blocks:

        if item.type == "paragraph":
            notion_blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": item.text or ""},
                                "annotations": {"code": item.is_code},
                            }
                        ]
                    },
                }
            )
        elif item.type == "heading_1":
            notion_blocks.append(
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {"type": "text", "text": {"content": item.text or ""}}
                        ]
                    },
                }
            )
        elif item.type == "heading_2":
            notion_blocks.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"type": "text", "text": {"content": item.text or ""}}
                        ]
                    },
                }
            )
        elif item.type == "heading_3":
            notion_blocks.append(
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {"type": "text", "text": {"content": item.text or ""}}
                        ]
                    },
                }
            )
        elif item.type == "numbered_list_item":
            notion_blocks.append(
                {
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [
                            {"type": "text", "text": {"content": item.text or ""}}
                        ]
                    },
                }
            )
        elif item.type == "image":
            notion_blocks.append(
                {
                    "object": "block",
                    "type": "image",
                    "image": {"type": "external", "external": {"url": diagram_url}},
                }
            )
        elif item.type == "link_preview":
            url_val = getattr(item, "url", "")
            notion_blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": url_val}}]
                    },
                }
            )

    return notion_blocks


def add_newsletter_to_notion(parent_id: str, content_blocks: list):
    """
    Add newsletter content to a Notion page.

    Args:
        parent_id (str): The Notion page ID (should be a valid UUID)
        content_blocks (list): List of Notion block dictionaries
    """
    # Validate that parent_id looks like a UUID
    if parent_id == "notion-page-id" or len(parent_id) < 32:
        print(
            f"Warning: Using test page ID '{parent_id}'. This won't work with real Notion API.",
            flush=True,
        )
        print(
            "Please provide a valid Notion page UUID to actually create the page.",
            flush=True,
        )
        return False

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    data = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {"title": [{"text": {"content": f"Newsletter Draft"}}]}
        },
        "children": content_blocks,
    }

    print(
        f"Attempting to create Notion page with {len(content_blocks)} blocks",
        flush=True,
    )
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Newsletter added to Notion successfully.", flush=True)
        return True
    else:
        print("Failed to add newsletter to Notion.", flush=True)
        print("Response:", response.json(), flush=True)
        return False
