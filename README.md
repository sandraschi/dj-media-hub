# DJ Media Hub - Composite MCP Server

**VirtualDJ + Plex = Unlimited Possibilities** 🎧📺

A composite MCP server that mounts multiple media servers under one roof,
enabling cross-server workflows that no single server could achieve alone.

## Features

### Mounted Servers

| Server | Mount Point | Description |
|--------|-------------|-------------|
| VirtualDJ-MCP | `/dj/*` | 49 tools for DJ automation, 8-deck mixing, stems, beatgrid |
| Plex-MCP | `/plex/*` | 15 portmanteau tools for media library management |

### Cross-Server Workflows

| Tool | Description |
|------|-------------|
| `plex_to_deck` | Search Plex library -> Load track to VirtualDJ deck |
| `plex_playlist_to_automix` | Load Plex playlist -> VirtualDJ automix queue |
| `record_mix_to_plex` | Save VirtualDJ recording -> Plex library |
| `multi_deck_plex_load` | Load 8 tracks from Plex -> 8 decks in one call! |

## Installation

```powershell
# Clone the repo
git clone https://github.com/sandraschi/dj-media-hub.git
cd dj-media-hub

# Create venv with Python 3.11 (required for aubio)
uv venv --python 3.11
.venv\Scripts\Activate.ps1

# Install with dependencies
uv pip install -e .

# Install component servers (if not already installed)
uv pip install -e D:\Dev\repos\virtualdj-mcp
uv pip install -e D:\Dev\repos\plexmcp
```

## Usage

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dj-media-hub": {
      "command": "python",
      "args": ["-m", "dj_media_hub"],
      "cwd": "D:\\Dev\\repos\\dj-media-hub"
    }
  }
}
```

### Example Workflows

**1. DJ Set from Plex Playlist**
```
# Load your "Party Mix" playlist to automix
plex_playlist_to_automix("Party Mix", shuffle=True, limit=20)

# Start automix for 1 hour
/dj/auto_dj_mode(duration_minutes=60)
```

**2. Quick 8-Deck Setup from Plex**
```
# Load 8 tracks from Plex in ONE call!
multi_deck_plex_load([
    "Daft Punk Around the World",
    "Chemical Brothers Block Rockin",
    "Fatboy Slim Praise You",
    "Prodigy Firestarter",
    "Underworld Born Slippy",
    "Orbital Halcyon",
    "Aphex Twin Windowlicker",
    "Massive Attack Teardrop"
])
```

**3. Record and Archive to Plex**
```
# Start recording your mix
/dj/start_recording(name="Saturday_Night_Set")

# ... epic mixing happens ...

# Stop and save to Plex library
/dj/stop_recording()
record_mix_to_plex("Saturday Night Set 2025")
```

## Architecture

```
DJ-Media-Hub (Composite)
├── /dj/*           <-- VirtualDJ-MCP mounted
│   ├── load_track_to_deck
│   ├── set_deck_volume
│   ├── stem_kill/stem_volume
│   ├── beatgrid_adjust
│   └── ... (49 tools)
├── /plex/*         <-- Plex-MCP mounted
│   ├── plex_library
│   ├── plex_playlist
│   ├── plex_search
│   └── ... (15 tools)
└── Root Tools      <-- Cross-server workflows
    ├── plex_to_deck
    ├── plex_playlist_to_automix
    ├── record_mix_to_plex
    ├── multi_deck_plex_load
    ├── hub_status
    └── hub_help
```

## Requirements

- Python 3.10-3.11 (3.11 recommended for aubio)
- VirtualDJ (running with HTTP network control enabled)
- Plex Media Server (with API access)
- FastMCP 2.13+

## How It Works

FastMCP's `mount()` feature allows composing multiple MCP servers:

```python
from fastmcp import FastMCP

# Main composite server
mcp = FastMCP("DJ-Media-Hub")

# Mount component servers
from virtualdj_mcp.server import mcp as vdj_mcp
from plex_mcp.app import mcp as plex_mcp

mcp.mount("/dj", vdj_mcp)      # All VirtualDJ tools at /dj/*
mcp.mount("/plex", plex_mcp)   # All Plex tools at /plex/*

# Add cross-server tools
@mcp.tool()
async def plex_to_deck(query: str, deck: int):
    # Uses both servers!
    track = await plex_search(query)
    await vdj_load(deck, track.path)
```

## Future Mounts

The architecture supports adding more servers:

```python
mcp.mount("/spotify", spotify_mcp)    # Spotify integration
mcp.mount("/youtube", youtube_mcp)    # YouTube Music
mcp.mount("/obs", obs_mcp)            # OBS for streaming
mcp.mount("/twitch", twitch_mcp)      # Twitch chat/alerts
```

## License

MIT License - See LICENSE file

