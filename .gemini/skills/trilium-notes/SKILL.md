---
name: trilium-notes
description: Expert guidance for managing and organizing notes in Trilium. Use this skill when the user wants to refactor their note tree, automate journal entries, or ingest external data into Trilium notes.
---

# Trilium Notes Skill

This skill provides expert procedural knowledge for maintaining a high-quality personal knowledge base in Trilium Notes.

## Core Workflows

### 1. The "Inbox to Archive" Refactor
When the user has many notes in their inbox and wants to organize them:
1.  **List Inbox**: Use `get_inbox_note` or `get_note_tree` on the inbox folder.
2.  **Categorize**: For each note, determine its logical parent.
3.  **Move & Branch**: Use `move_note` or `clone_note`.
4.  **Label**: Apply relevant labels using `set_attribute`.

### 2. Surgical Content Updates
To update specific parts of a note without overwriting the whole thing:
-   **Preferred**: Use `update_note_content` with `mode: 'search_replace'`.
-   **Batched Edits**: Use `patch_note` for CSS/Line/Regex based patches.

### 3. Creating Projects
A "Project" in Trilium is usually a note with specific labels:
1.  Create the project note under a parent.
2.  Add a `#project` label.
3.  Add a `status` label (e.g., `active`, `done`).
4.  Create children for `tasks`, `logs`, and `resources`.

## Advanced Reference
For detailed patterns on journaling and automated ingestion, see [workflows.md](references/workflows.md).
