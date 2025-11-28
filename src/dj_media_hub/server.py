"""
DJ Media Hub - Composite MCP Server

Mounts VirtualDJ-MCP and Plex-MCP under unified namespaces,
enabling cross-server workflows for media production.

NO HUMAN CAN MIX 8 DECKS. But AI can search Plex AND mix VirtualDJ simultaneously!
"""

import sys
from pathlib import Path
from rich.console import Console

from fastmcp import FastMCP

# Console for logging (stderr for MCP compatibility)
console = Console(file=sys.stderr)

# ============================================================================
# MAIN COMPOSITE SERVER
# ============================================================================

mcp = FastMCP(
    "DJ-Media-Hub",
    instructions="""
    DJ Media Hub - Composite MCP server for media production workflows.
    
    MOUNTED SERVERS:
    - /dj/*      : VirtualDJ-MCP (deck control, mixing, stems, beatgrid, automation)
    - /plex/*    : Plex-MCP (media library, playlists, streaming)
    
    CROSS-SERVER WORKFLOWS:
    - plex_to_deck: Search Plex -> Load track to VirtualDJ
    - record_to_plex: Record VirtualDJ mix -> Add to Plex library
    - sync_playlist: Sync Plex playlist -> VirtualDJ automix queue
    
    The AI DJ can mix 8 decks while simultaneously browsing your Plex library!
    """
)


# ============================================================================
# MOUNT COMPONENT SERVERS
# ============================================================================

def mount_servers():
    """Mount VirtualDJ and Plex MCP servers."""
    try:
        # Import VirtualDJ-MCP
        from virtualdj_mcp.server import mcp as vdj_mcp
        mcp.mount("/dj", vdj_mcp)
        console.print("[green]Mounted VirtualDJ-MCP at /dj/*[/green]")
    except ImportError as e:
        console.print(f"[yellow]VirtualDJ-MCP not available: {e}[/yellow]")
        console.print("[dim]Install: pip install -e D:/Dev/repos/virtualdj-mcp[/dim]")
    
    try:
        # Import Plex-MCP
        from plex_mcp.app import mcp as plex_mcp
        mcp.mount("/plex", plex_mcp)
        console.print("[green]Mounted Plex-MCP at /plex/*[/green]")
    except ImportError as e:
        console.print(f"[yellow]Plex-MCP not available: {e}[/yellow]")
        console.print("[dim]Install: pip install -e D:/Dev/repos/plexmcp[/dim]")


# ============================================================================
# CROSS-SERVER COMPOSITE TOOLS
# ============================================================================

@mcp.tool()
async def plex_to_deck(
    search_query: str,
    deck_id: int = 1,
    search_type: str = "track"
) -> dict:
    """
    Search Plex library and load result directly to VirtualDJ deck.
    
    This is a CROSS-SERVER workflow:
    1. Search Plex for media matching query
    2. Get file path from Plex
    3. Load track to VirtualDJ deck
    
    Args:
        search_query: What to search for (artist, track name, album)
        deck_id: VirtualDJ deck to load to (1-8)
        search_type: Type of search (track, album, artist)
    
    Returns:
        Dict with search result and load status
    """
    try:
        # Step 1: Search Plex
        from plex_mcp.services.plex_service import PlexService
        plex = PlexService()
        
        results = await plex.search(search_query, limit=1)
        
        if not results:
            return {
                "success": False,
                "error": f"No results found in Plex for: {search_query}"
            }
        
        # Get the first matching track
        track = results[0]
        file_path = track.get("file_path") or track.get("media", [{}])[0].get("parts", [{}])[0].get("file")
        
        if not file_path:
            return {
                "success": False,
                "error": "Could not get file path from Plex result"
            }
        
        # Step 2: Load to VirtualDJ
        from virtualdj_mcp.core.vdj_client import VirtualDJClient, VDJConfig
        
        config = VDJConfig()
        async with VirtualDJClient(config) as vdj:
            await vdj.load_track(deck_id, file_path)
        
        return {
            "success": True,
            "plex_result": {
                "title": track.get("title"),
                "artist": track.get("grandparentTitle"),
                "album": track.get("parentTitle"),
                "file": file_path
            },
            "vdj_deck": deck_id,
            "message": f"Loaded '{track.get('title')}' to Deck {deck_id}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def plex_playlist_to_automix(
    playlist_name: str,
    shuffle: bool = False,
    limit: int = 50
) -> dict:
    """
    Load a Plex playlist into VirtualDJ's automix queue.
    
    Cross-server workflow:
    1. Get playlist from Plex
    2. Extract all track file paths
    3. Load tracks to VirtualDJ automix queue
    
    Args:
        playlist_name: Name of Plex playlist to load
        shuffle: Randomize track order
        limit: Maximum tracks to load
    
    Returns:
        Dict with loaded tracks info
    """
    try:
        from plex_mcp.services.playlist_service import PlaylistService
        playlist_svc = PlaylistService()
        
        # Get playlist tracks
        tracks = await playlist_svc.get_playlist_tracks(playlist_name)
        
        if not tracks:
            return {
                "success": False,
                "error": f"Playlist '{playlist_name}' not found or empty"
            }
        
        if shuffle:
            import random
            random.shuffle(tracks)
        
        tracks = tracks[:limit]
        
        # Get file paths
        file_paths = []
        for track in tracks:
            path = track.get("file_path") or track.get("media", [{}])[0].get("parts", [{}])[0].get("file")
            if path:
                file_paths.append(path)
        
        # Load to VirtualDJ automix
        from virtualdj_mcp.core.vdj_client import VirtualDJClient, VDJConfig
        
        config = VDJConfig()
        async with VirtualDJClient(config) as vdj:
            for path in file_paths:
                await vdj.send_command(f"automix_add '{path}'")
        
        return {
            "success": True,
            "playlist": playlist_name,
            "tracks_loaded": len(file_paths),
            "shuffle": shuffle,
            "message": f"Loaded {len(file_paths)} tracks from '{playlist_name}' to automix"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def record_mix_to_plex(
    mix_name: str,
    plex_library: str = "Music",
    recording_id: str | None = None
) -> dict:
    """
    Save a VirtualDJ recording to Plex library.
    
    Cross-server workflow:
    1. Get recording file from VirtualDJ
    2. Copy/move to Plex music library path
    3. Trigger Plex library scan
    
    Args:
        mix_name: Name for the mix in Plex
        plex_library: Target Plex library (default: Music)
        recording_id: Specific VirtualDJ recording ID (latest if omitted)
    
    Returns:
        Dict with save status
    """
    try:
        from virtualdj_mcp.services.recording_service import RecordingService
        from plex_mcp.services.plex_service import PlexService
        import shutil
        
        rec_svc = RecordingService()
        plex_svc = PlexService()
        
        # Get recording info
        if recording_id:
            recording = await rec_svc.get_recording(recording_id)
        else:
            recordings = await rec_svc.list_recordings(limit=1)
            if not recordings:
                return {"success": False, "error": "No recordings found"}
            recording = recordings[0]
        
        source_path = Path(recording["file_path"])
        
        if not source_path.exists():
            return {"success": False, "error": f"Recording file not found: {source_path}"}
        
        # Get Plex library path
        library_info = await plex_svc.get_library_info(plex_library)
        dest_dir = Path(library_info["path"]) / "DJ Mixes"
        dest_dir.mkdir(exist_ok=True)
        
        dest_path = dest_dir / f"{mix_name}{source_path.suffix}"
        
        # Copy the file
        shutil.copy2(source_path, dest_path)
        
        # Trigger Plex scan
        await plex_svc.scan_library(plex_library)
        
        return {
            "success": True,
            "source": str(source_path),
            "destination": str(dest_path),
            "plex_library": plex_library,
            "message": f"Mix '{mix_name}' saved to Plex and library scan triggered"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def multi_deck_plex_load(
    search_queries: list[str],
    start_deck: int = 1
) -> dict:
    """
    Search Plex for multiple tracks and load them to consecutive decks.
    
    Perfect for quick setup: provide 8 search queries, get 8 decks loaded!
    
    Args:
        search_queries: List of search queries (one per deck)
        start_deck: First deck to load to (default: 1)
    
    Returns:
        Dict with load results for each deck
    
    Example:
        multi_deck_plex_load(
            ["Daft Punk Around the World", "Chemical Brothers Block Rockin"],
            start_deck=1
        )
    """
    results = []
    current_deck = start_deck
    
    for query in search_queries:
        if current_deck > 8:
            results.append({
                "deck": current_deck,
                "query": query,
                "success": False,
                "error": "Deck number exceeds maximum (8)"
            })
            continue
        
        result = await plex_to_deck(query, current_deck)
        results.append({
            "deck": current_deck,
            "query": query,
            **result
        })
        current_deck += 1
    
    successful = sum(1 for r in results if r.get("success"))
    
    return {
        "success": successful > 0,
        "decks_loaded": successful,
        "total_queries": len(search_queries),
        "results": results,
        "message": f"Loaded {successful}/{len(search_queries)} tracks from Plex to decks"
    }


@mcp.tool()
async def hub_status() -> dict:
    """
    Get status of all mounted servers and cross-server capabilities.
    
    Returns:
        Dict with server status and available workflows
    """
    status = {
        "hub_name": "DJ-Media-Hub",
        "version": "1.0.0",
        "servers": {},
        "cross_server_tools": [
            "plex_to_deck",
            "plex_playlist_to_automix",
            "record_mix_to_plex",
            "multi_deck_plex_load"
        ]
    }
    
    # Check VirtualDJ
    try:
        from virtualdj_mcp.core.vdj_client import VirtualDJClient, VDJConfig
        config = VDJConfig()
        async with VirtualDJClient(config) as vdj:
            running = await vdj.is_running()
            status["servers"]["virtualdj"] = {
                "available": True,
                "running": running,
                "mount": "/dj/*"
            }
    except Exception as e:
        status["servers"]["virtualdj"] = {
            "available": False,
            "error": str(e)
        }
    
    # Check Plex
    try:
        from plex_mcp.services.plex_service import PlexService
        plex = PlexService()
        connected = await plex.test_connection()
        status["servers"]["plex"] = {
            "available": True,
            "connected": connected,
            "mount": "/plex/*"
        }
    except Exception as e:
        status["servers"]["plex"] = {
            "available": False,
            "error": str(e)
        }
    
    return status


# ============================================================================
# HELP TOOL
# ============================================================================

@mcp.tool()
async def hub_help(topic: str = "overview") -> str:
    """
    Get help for DJ Media Hub cross-server workflows.
    
    Args:
        topic: Help topic (overview, plex, virtualdj, workflows, examples)
    
    Returns:
        Help text for the requested topic
    """
    help_texts = {
        "overview": """
# DJ Media Hub - Cross-Server MCP

This composite server mounts multiple MCP servers:
- **/dj/*** - VirtualDJ-MCP (49 tools for DJ automation)
- **/plex/*** - Plex-MCP (15 portmanteau tools for media management)

## Cross-Server Workflows

The magic happens when servers talk to each other:

| Workflow | Description |
|----------|-------------|
| `plex_to_deck` | Search Plex -> Load to VirtualDJ deck |
| `plex_playlist_to_automix` | Load Plex playlist -> VirtualDJ automix |
| `record_mix_to_plex` | Save VirtualDJ recording -> Plex library |
| `multi_deck_plex_load` | Load 8 tracks from Plex -> 8 decks! |

## Usage

All original server tools remain available under their prefixes:
- `/dj/load_track_to_deck` - VirtualDJ tool
- `/plex/plex_library` - Plex tool

Plus new cross-server tools at the root level.
""",
        
        "workflows": """
# Cross-Server Workflow Examples

## 1. DJ Set from Plex Playlist

```
# Load your "Party Mix" playlist to automix
plex_playlist_to_automix("Party Mix", shuffle=True, limit=20)

# Start automix
/dj/auto_dj_mode(duration_minutes=60)
```

## 2. Quick 8-Deck Setup

```
# Load 8 tracks from Plex in one call!
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

# Run superhuman 8-deck mix
/dj/get_performance_metrics()
```

## 3. Record and Archive

```
# Start recording
/dj/start_recording(name="Saturday_Night_Set")

# ... mix happens ...

# Stop and save to Plex
/dj/stop_recording()
record_mix_to_plex("Saturday Night Set 2025")
```
""",
        
        "examples": """
# Quick Examples

## Search Plex, Load to Deck 1
```
plex_to_deck("Daft Punk", deck_id=1)
```

## Load Playlist to Automix
```
plex_playlist_to_automix("Chill Vibes", shuffle=True)
```

## Check Everything
```
hub_status()
```

## Get VirtualDJ Help
```
/dj/show_help(level="categories")
```

## Get Plex Help
```
/plex/plex_help("overview")
```
"""
    }
    
    return help_texts.get(topic, help_texts["overview"])


# ============================================================================
# SERVER ENTRY POINTS
# ============================================================================

def main():
    """Main entry point for DJ Media Hub."""
    console.print("""
[bold magenta]
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🎧 DJ MEDIA HUB - COMPOSITE MCP SERVER 🎧               ║
║                                                                      ║
║              VirtualDJ + Plex = Unlimited Possibilities              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
[/bold magenta]""")
    
    # Mount component servers
    mount_servers()
    
    console.print("\n[green]Starting MCP server in STDIO mode...[/green]")
    console.print("[dim]Cross-server workflows enabled![/dim]\n")
    
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        console.print("\n[yellow]Server shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]Server error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()

