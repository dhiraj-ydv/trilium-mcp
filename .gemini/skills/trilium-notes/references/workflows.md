# Trilium Workflows

## Journaling & Daily Notes
Trilium has built-in calendar support. 
- Use `get_day_note(date="YYYY-MM-DD")` to get or create the daily note.
- Standard daily note structure includes:
    - `#dailyNote` label.
    - `date` attribute.

## Web Ingestion
When clipping content from the web:
- Use `clip_url(url="...")` for quick capture.
- The resulting note is placed in the root.
- Post-clipping workflow:
    1. `resolve_note_id` for the new note.
    2. `move_note` to a dedicated "Clipped" folder.
    3. Add a `#webclip` label.

## Linking Notes
Use `set_attribute` with `type="relation"` to link notes:
- **Relation Name**: `related` or `parentOf`.
- **Value**: The `noteId` of the target note.
