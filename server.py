import os
import httpx
import asyncio
import base64
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types

load_dotenv()

TRILIUM_URL = os.environ.get("TRILIUM_URL", "http://localhost:37840/etapi")
TRILIUM_TOKEN = os.environ.get("TRILIUM_TOKEN")

if not TRILIUM_TOKEN:
    print("Warning: TRILIUM_TOKEN environment variable is not set.", flush=True)

server = Server("trilium-mcp-server")

async def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=TRILIUM_URL,
        headers={
            "Authorization": TRILIUM_TOKEN or "",
            "Content-Type": "application/json",
        },
        timeout=30.0
    )

# --- Tool Definitions ---
TOOLS = [
    # System & General
    types.Tool(name="get_application_information", description="Returns information about the running Trilium instance.", inputSchema={"type": "object", "properties": {}}),
    types.Tool(name="search_tools", description="Search available tools by keyword.", inputSchema={"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}),
    
    # Search & Discovery
    types.Tool(name="search_notes", description="Unified full-text search.", inputSchema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}),
    types.Tool(name="resolve_note_id", description="Find a note's ID by its title.", inputSchema={"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}),
    types.Tool(name="get_note_tree", description="List direct child notes of a parent.", inputSchema={"type": "object", "properties": {"parentNoteId": {"type": "string"}}, "required": ["parentNoteId"]}),
    
    # Note Management
    types.Tool(name="create_note", description="Create a note.", inputSchema={"type": "object", "properties": {"parentNoteId": {"type": "string"}, "title": {"type": "string"}, "type": {"type": "string"}, "content": {"type": "string"}, "mime": {"type": "string"}}, "required": ["parentNoteId", "title", "content"]}),
    types.Tool(name="get_note", description="Retrieve note metadata by ID.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="get_note_content", description="Get note content.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="update_note", description="Update note metadata.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}, "title": {"type": "string"}, "type": {"type": "string"}, "mime": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="update_note_content", description="Update note content.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}, "content": {"type": "string"}, "mode": {"type": "string", "enum": ["replace", "search_replace"], "default": "replace"}, "changes": {"type": "array", "items": {"type": "object", "properties": {"old_string": {"type": "string"}, "new_string": {"type": "string"}}}}}, "required": ["noteId"]}),
    types.Tool(name="append_note_content", description="Append content to a note.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}, "content": {"type": "string"}}, "required": ["noteId", "content"]}),
    types.Tool(name="delete_note", description="Delete a single note.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="patch_note", description="Apply targeted batched edits using mode-based patches.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}, "patch": {"type": "string"}}, "required": ["noteId", "patch"]}),
    types.Tool(name="undelete_note", description="Restore a previously deleted note.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="get_note_history", description="Get recent changes.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    
    # Organization & Branches
    types.Tool(name="get_branch", description="Returns a branch identified by ID.", inputSchema={"type": "object", "properties": {"branchId": {"type": "string"}}, "required": ["branchId"]}),
    types.Tool(name="clone_note", description="Clone a note (create a branch).", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}, "parentNoteId": {"type": "string"}, "prefix": {"type": "string"}}, "required": ["noteId", "parentNoteId"]}),
    types.Tool(name="update_branch", description="Update prefix/position on a branch.", inputSchema={"type": "object", "properties": {"branchId": {"type": "string"}, "prefix": {"type": "string"}, "notePosition": {"type": "integer"}}, "required": ["branchId"]}),
    types.Tool(name="move_note", description="Move a note to a different parent.", inputSchema={"type": "object", "properties": {"branchId": {"type": "string"}, "newParentNoteId": {"type": "string"}}, "required": ["branchId", "newParentNoteId"]}),
    types.Tool(name="reorder_notes", description="Change note positions within a parent.", inputSchema={"type": "object", "properties": {"parentNoteId": {"type": "string"}, "noteIds": {"type": "array", "items": {"type": "string"}}}, "required": ["parentNoteId", "noteIds"]}),
    types.Tool(name="refresh_note_order", description="Push re-ordering to connected clients immediately.", inputSchema={"type": "object", "properties": {"parentNoteId": {"type": "string"}}, "required": ["parentNoteId"]}),
    types.Tool(name="delete_branch", description="Remove a branch by ID.", inputSchema={"type": "object", "properties": {"branchId": {"type": "string"}}, "required": ["branchId"]}),
    
    # Attributes & Labels
    types.Tool(name="get_attributes", description="Read all attributes.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="get_attribute", description="Get a single attribute by ID.", inputSchema={"type": "object", "properties": {"attributeId": {"type": "string"}}, "required": ["attributeId"]}),
    types.Tool(name="set_attribute", description="Create or add an attribute.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}, "type": {"type": "string", "enum": ["label", "relation"]}, "name": {"type": "string"}, "value": {"type": "string"}, "isInheritable": {"type": "boolean"}}, "required": ["noteId", "type", "name"]}),
    types.Tool(name="delete_attribute", description="Remove an attribute.", inputSchema={"type": "object", "properties": {"attributeId": {"type": "string"}}, "required": ["attributeId"]}),
    
    # Calendar & Journal
    types.Tool(name="get_inbox_note", description="Get the inbox note for a given date.", inputSchema={"type": "object", "properties": {"date": {"type": "string"}}, "required": ["date"]}),
    types.Tool(name="get_day_note", description="Get/create daily note.", inputSchema={"type": "object", "properties": {"date": {"type": "string"}}, "required": ["date"]}),
    types.Tool(name="get_week_note", description="Get/create week note (YYYY-Www).", inputSchema={"type": "object", "properties": {"date": {"type": "string"}}, "required": ["date"]}),
    types.Tool(name="get_month_note", description="Get/create month note (YYYY-MM).", inputSchema={"type": "object", "properties": {"date": {"type": "string"}}, "required": ["date"]}),
    types.Tool(name="get_year_note", description="Get/create year note (YYYY).", inputSchema={"type": "object", "properties": {"date": {"type": "string"}}, "required": ["date"]}),
    
    # Attachments
    types.Tool(name="get_note_attachments", description="List all attachments for a note.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="create_attachment", description="Create attachment.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}, "title": {"type": "string"}, "mime": {"type": "string"}, "content": {"type": "string"}}, "required": ["noteId", "title", "content"]}),
    types.Tool(name="get_attachment", description="Get attachment metadata.", inputSchema={"type": "object", "properties": {"attachmentId": {"type": "string"}}, "required": ["attachmentId"]}),
    types.Tool(name="get_attachment_content", description="Get attachment content.", inputSchema={"type": "object", "properties": {"attachmentId": {"type": "string"}}, "required": ["attachmentId"]}),
    types.Tool(name="update_attachment", description="Update attachment metadata.", inputSchema={"type": "object", "properties": {"attachmentId": {"type": "string"}, "title": {"type": "string"}, "mime": {"type": "string"}, "role": {"type": "string"}}, "required": ["attachmentId"]}),
    types.Tool(name="update_attachment_content", description="Update attachment content.", inputSchema={"type": "object", "properties": {"attachmentId": {"type": "string"}, "content": {"type": "string"}}, "required": ["attachmentId", "content"]}),
    types.Tool(name="delete_attachment", description="Delete attachment.", inputSchema={"type": "object", "properties": {"attachmentId": {"type": "string"}}, "required": ["attachmentId"]}),
    
    # Revisions & Backups
    types.Tool(name="get_note_revisions", description="List revisions for note.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="get_revision", description="Get revision metadata.", inputSchema={"type": "object", "properties": {"revisionId": {"type": "string"}}, "required": ["revisionId"]}),
    types.Tool(name="get_revision_content", description="Get revision content.", inputSchema={"type": "object", "properties": {"revisionId": {"type": "string"}}, "required": ["revisionId"]}),
    types.Tool(name="create_revision", description="Create a revision snapshot of a note.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}}, "required": ["noteId"]}),
    types.Tool(name="create_backup", description="Create backup.", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
    types.Tool(name="export_note", description="Export note subtree as ZIP.", inputSchema={"type": "object", "properties": {"noteId": {"type": "string"}, "format": {"type": "string", "default": "html"}}, "required": ["noteId"]}),
    
    # Web Clipper
    types.Tool(name="clip_url", description="Clip web page to root.", inputSchema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]})
]

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        async with await get_client() as client:
            # System
            if name == "get_application_information":
                response = await client.get("/app-info")
            elif name == "search_tools":
                results = [t for t in TOOLS if arguments.get("keyword").lower() in t.description.lower() or arguments.get("keyword").lower() in t.name.lower()]
                return [types.TextContent(type="text", text=str([{"name": t.name, "description": t.description} for t in results]))]
                
            # Search & Discovery
            elif name == "search_notes":
                response = await client.get("/notes", params={"search": arguments.get("query")})
            elif name == "resolve_note_id":
                response = await client.get("/notes", params={"search": f"note.title='{arguments.get('title')}'"})
            elif name == "get_note_tree":
                response = await client.get("/notes", params={"search": f"note.parents.noteId='{arguments.get('parentNoteId')}'"})
                
            # Note Management
            elif name == "create_note":
                data = {
                    "parentNoteId": arguments.get("parentNoteId"),
                    "title": arguments.get("title"),
                    "type": arguments.get("type", "text"),
                    "content": arguments.get("content"),
                    "mime": arguments.get("mime", "text/html"),
                }
                response = await client.post("/create-note", json=data)
            elif name == "get_note":
                response = await client.get(f"/notes/{arguments.get('noteId')}")
            elif name == "get_note_content":
                response = await client.get(f"/notes/{arguments.get('noteId')}/content")
            elif name == "update_note":
                data = {k: v for k, v in arguments.items() if k != "noteId" and v is not None}
                response = await client.put(f"/notes/{arguments.get('noteId')}", json=data)
            elif name == "update_note_content":
                note_id = arguments.get("noteId")
                mode = arguments.get("mode", "replace")
                
                if mode == "replace":
                    content = arguments.get("content", "")
                elif mode == "search_replace":
                    # Get current content first
                    r = await client.get(f"/notes/{note_id}/content")
                    r.raise_for_status()
                    content = r.text
                    changes = arguments.get("changes", [])
                    for change in changes:
                        content = content.replace(change.get("old_string", ""), change.get("new_string", ""))
                else:
                    content = arguments.get("content", "")

                response = await client.put(f"/notes/{note_id}/content", content=content, headers={"Content-Type": "text/plain"})
            elif name == "append_note_content":
                note_id = arguments.get("noteId")
                r = await client.get(f"/notes/{note_id}/content")
                r.raise_for_status()
                content = r.text + "\n" + arguments.get("content", "")
                response = await client.put(f"/notes/{note_id}/content", content=content, headers={"Content-Type": "text/plain"})
            elif name == "delete_note":
                response = await client.delete(f"/notes/{arguments.get('noteId')}")
            elif name == "patch_note":
                response = await client.post(f"/notes/{arguments.get('noteId')}/patch", content=arguments.get("patch"), headers={"Content-Type": "text/plain"})
            elif name == "undelete_note":
                # Typically done via updating isDeleted flag
                response = await client.put(f"/notes/{arguments.get('noteId')}", json={"isDeleted": False})
            elif name == "get_note_history":
                response = await client.get(f"/notes/{arguments.get('noteId')}/revisions")
                
            # Branches
            elif name == "get_branch":
                response = await client.get(f"/branches/{arguments.get('branchId')}")
            elif name == "clone_note":
                response = await client.post("/branches", json={"noteId": arguments.get("noteId"), "parentNoteId": arguments.get("parentNoteId"), "prefix": arguments.get("prefix", "")})
            elif name == "update_branch":
                data = {k: v for k, v in arguments.items() if k != "branchId" and v is not None}
                response = await client.put(f"/branches/{arguments.get('branchId')}", json=data)
            elif name == "move_note":
                response = await client.put(f"/branches/{arguments.get('branchId')}", json={"parentNoteId": arguments.get("newParentNoteId")})
            elif name == "reorder_notes":
                response = await client.post(f"/notes/{arguments.get('parentNoteId')}/reorder", json={"noteIds": arguments.get("noteIds")})
            elif name == "refresh_note_order":
                response = await client.post(f"/notes/{arguments.get('parentNoteId')}/refresh-order")
            elif name == "delete_branch":
                response = await client.delete(f"/branches/{arguments.get('branchId')}")
                
            # Attributes
            elif name == "get_attributes":
                response = await client.get("/attributes", params={"noteId": arguments.get("noteId")})
            elif name == "get_attribute":
                response = await client.get(f"/attributes/{arguments.get('attributeId')}")
            elif name == "set_attribute":
                data = {
                    "noteId": arguments.get("noteId"),
                    "type": arguments.get("type"),
                    "name": arguments.get("name"),
                    "value": arguments.get("value", ""),
                    "isInheritable": arguments.get("isInheritable", False),
                }
                response = await client.post("/attributes", json=data)
            elif name == "delete_attribute":
                response = await client.delete(f"/attributes/{arguments.get('attributeId')}")
                
            # Calendar
            elif name == "get_inbox_note":
                response = await client.get(f"/calendar/inbox/{arguments.get('date')}")
            elif name == "get_day_note":
                response = await client.get(f"/calendar/days/{arguments.get('date')}")
            elif name == "get_week_note":
                response = await client.get(f"/calendar/weeks/{arguments.get('date')}")
            elif name == "get_month_note":
                response = await client.get(f"/calendar/months/{arguments.get('date')}")
            elif name == "get_year_note":
                response = await client.get(f"/calendar/years/{arguments.get('date')}")
                
            # Attachments
            elif name == "get_note_attachments":
                response = await client.get(f"/notes/{arguments.get('noteId')}/attachments")
            elif name == "create_attachment":
                response = await client.post(f"/notes/{arguments.get('noteId')}/attachments", json={"title": arguments.get("title"), "mime": arguments.get("mime"), "content": arguments.get("content")})
            elif name == "get_attachment":
                response = await client.get(f"/attachments/{arguments.get('attachmentId')}")
            elif name == "get_attachment_content":
                response = await client.get(f"/attachments/{arguments.get('attachmentId')}/content")
            elif name == "update_attachment":
                data = {k: v for k, v in arguments.items() if k != "attachmentId" and v is not None}
                response = await client.put(f"/attachments/{arguments.get('attachmentId')}", json=data)
            elif name == "update_attachment_content":
                response = await client.put(f"/attachments/{arguments.get('attachmentId')}/content", content=arguments.get("content"), headers={"Content-Type": "text/plain"})
            elif name == "delete_attachment":
                response = await client.delete(f"/attachments/{arguments.get('attachmentId')}")
                
            # Revisions & Backups
            elif name == "get_note_revisions":
                response = await client.get(f"/notes/{arguments.get('noteId')}/revisions")
            elif name == "get_revision":
                response = await client.get(f"/revisions/{arguments.get('revisionId')}")
            elif name == "get_revision_content":
                response = await client.get(f"/revisions/{arguments.get('revisionId')}/content")
            elif name == "create_revision":
                response = await client.post(f"/notes/{arguments.get('noteId')}/revisions")
            elif name == "create_backup":
                response = await client.post("/backup", json={"name": arguments.get("name")})
            elif name == "export_note":
                response = await client.get(f"/notes/{arguments.get('noteId')}/export", params={"format": arguments.get("format")})
                
            # Web Clipper
            elif name == "clip_url":
                url = arguments.get("url")
                async with httpx.AsyncClient() as wc:
                    web_res = await wc.get(url)
                    web_res.raise_for_status()
                    html_content = web_res.text
                    
                # Create a note in root with the content
                title = "Clipped: " + url[:20]
                response = await client.post("/create-note", json={
                    "parentNoteId": "root",
                    "title": title,
                    "type": "text",
                    "content": html_content,
                    "mime": "text/html"
                })
            else:
                raise ValueError(f"Tool not found: {name}")

            response.raise_for_status()
            
            # Format output
            try:
                response_data = response.json()
                import json
                text = json.dumps(response_data, indent=2)
            except Exception:
                text = response.text

            return [types.TextContent(type="text", text=text)]
            
    except httpx.HTTPStatusError as e:
        return [types.TextContent(type="text", text=f"HTTP Error {e.response.status_code}: {e.response.text}")]
    except Exception as e:
        return [types.TextContent(type="text", text=str(e))]

async def main():
    options = InitializationOptions(
        server_name="trilium-mcp-server",
        server_version="1.0.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        )
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
