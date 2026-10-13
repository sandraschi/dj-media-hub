# dj-media-hub (MCPB Bundle)

Composite MCP server - VirtualDJ + Plex + more (cross-server workflows)

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "dj-media-hub": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "dj_media_hub"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **plex_to_deck**: plex_to_deck

## Requirements

- Python 3.12+
- uv
