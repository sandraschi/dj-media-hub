# dj-media-hub — User Guide

## Quick Start

### Prerequisites
- Python 3.10+ with uv
- virtualdj-mcp package installed (editable: `pip install -e D:/Dev/repos/virtualdj-mcp`)
- plex-mcp package installed (editable: `pip install -e D:/Dev/repos/plexmcp`)
- VirtualDJ Pro running with MCP integration enabled
- Plex Media Server running and accessible

### Installation
```bash
git clone https://github.com/sandraschi/dj-media-hub
cd dj-media-hub
uv sync
pip install -e D:/Dev/repos/virtualdj-mcp
pip install -e D:/Dev/repos/plexmcp
```

### Start the Server
```bash
uv run python -m dj_media_hub
```
The server starts in stdio mode and mounts both VirtualDJ and Plex servers automatically.

### Register with Claude Desktop
```json
{
  "mcpServers": {
    "dj-media-hub": {
      "command": "uv",
      "args": ["run", "--directory", "D:/Dev/repos/dj-media-hub", "python", "-m", "dj_media_hub"],
      "env": { "PYTHONPATH": "${workspaceFolder}/src" }
    }
  }
}
```

## Tutorials

### Tutorial 1: Check Server Status
Verify both mounted servers are available:
```
hub_status()
```
This confirms VirtualDJ and Plex connectivity. If either is unavailable, check the respective server's configuration and network.

### Tutorial 2: Search Plex and Load a Track to a Deck
Find a track in Plex and load it to VirtualDJ Deck 1:
```
plex_to_deck(search_query="Daft Punk Around the World", deck_id=1)
```
Plex is searched, the first matching track's file path is extracted and loaded to Deck 1. The response shows the track title, artist, album, and which deck it was loaded to.

### Tutorial 3: Load a Specific Track to Deck 3
Target a specific track to a higher deck:
```
plex_to_deck(search_query="Chemical Brothers Block Rockin Beats", deck_id=3)
```
Use this to stage tracks on different decks before mixing.

### Tutorial 4: Load a Full Playlist to Automix
Take a Plex playlist and feed it into VirtualDJ's automix for hands-free mixing:
```
plex_playlist_to_automix(playlist_name="Party Mix", shuffle=True, limit=30)
```
This loads up to 30 tracks from the "Party Mix" playlist in random order into the automix queue.

### Tutorial 5: Load a Calm Playlist Without Shuffle
For a curated set that should play in order:
```
plex_playlist_to_automix(playlist_name="Sunday Chill", shuffle=False, limit=20)
```

### Tutorial 6: Record a Mix and Save to Plex
After recording a mix in VirtualDJ, archive it in Plex:
```
# First, start recording in VirtualDJ
/dj/start_recording(name="Saturday_Night_Set")

# ... mix for an hour ...

# Stop recording
/dj/stop_recording()

# Archive to Plex
record_mix_to_plex(mix_name="Saturday Night Set 2025", plex_library="Music")
```
The recording is copied to your Plex Music library under a "DJ Mixes" folder and the library is automatically scanned.

### Tutorial 7: The Legendary 8-Deck Simultaneous Load
Load 8 different tracks from Plex to all 8 VirtualDJ decks in one call:
```
multi_deck_plex_load(
  search_queries=[
    "Daft Punk Around the World",
    "Chemical Brothers Block Rockin",
    "Fatboy Slim Praise You",
    "Prodigy Firestarter",
    "Underworld Born Slippy",
    "Orbital Halcyon",
    "Aphex Twin Windowlicker",
    "Massive Attack Teardrop"
  ],
  start_deck=1
)
```
This demonstrates the key advantage of AI over human DJs: loading 8 decks from a library search in seconds.

### Tutorial 8: Partial Multi-Deck Load (4 Decks)
Load a smaller set for a more manageable mix:
```
multi_deck_plex_load(
  search_queries=["Daft Punk", "Chemical Brothers", "Fatboy Slim", "Prodigy"],
  start_deck=1
)
```

### Tutorial 9: Mix Using VirtualDJ Controls via /dj/
While Plex tracks are loaded, control the mix:
```
# Start auto DJ mode
/dj/auto_dj_mode(duration_minutes=30)

# Check deck performance
/dj/get_performance_metrics()

# Control individual decks
/dj/mixer_set_eq(deck=1, band="low", value=0.8)
/dj/mixer_set_crossfader(position=0.3)
/dj/beatgrid_adjust(deck=2, bpm=128)
```

### Tutorial 10: Browse Plex Library via /plex/
Use the full Plex toolset through the mounted namespace:
```
# List libraries
/plex/plex_library(operation="list")

# Get recently added music
/plex/plex_media(operation="get_recent", library_id="2", limit=20)

# Search for specific artist
/plex/plex_search(operation="search", query="Bonobo")

# View playlist details
/plex/plex_playlist(operation="list")
```

### Tutorial 11: Full Workflow — Party Mode Setup
Complete party setup workflow:
```
# Step 1: Check status
hub_status()

# Step 2: Create a party playlist in Plex first via Plex tools
/plex/plex_playlist(operation="create", title="Party Mode 2025", items=["track1", "track2", "track3"])

# Step 3: Load entire playlist to automix
plex_playlist_to_automix(playlist_name="Party Mode 2025", shuffle=True, limit=50)

# Step 4: Start auto DJ
/dj/auto_dj_mode(duration_minutes=120)

# Step 5: Start recording
/dj/start_recording(name="Party_Mode_2025")

# Step 6: Monitor performance while it plays
/dj/get_performance_metrics()
```

### Tutorial 12: Cross-Server Help and Discovery
Get help on any topic:
```
hub_help(topic="overview")
hub_help(topic="workflows")
hub_help(topic="examples")
```
Or get help specific to mounted servers:
```
/dj/show_help(level="categories")
/plex/plex_help(operation="quickstart")
```

## API Reference

The DJ Media Hub does not expose a REST API directly. All operations are MCP tools. Mounted namespace tools are called using the /dj/ and /plex/ prefixes.

### Cross-Server Tool Reference

| Tool | Purpose | Avg Duration |
|------|---------|-------------|
| plex_to_deck | Search Plex + load to deck | 0.5-2s |
| plex_playlist_to_automix | Load playlist to automix | 2-30s |
| record_mix_to_plex | Archive recording to Plex | 1-10s |
| multi_deck_plex_load | Load N tracks to N decks | 1-15s |
| hub_status | Check all servers | 0.5-2s |
| hub_help | Get documentation | Instant |

### Return Format
All composite tools return:
```json
{
  "success": true,
  "message": "Loaded 'Around the World' to Deck 1",
  "plex_result": { "title": "...", "artist": "...", "album": "...", "file": "..." },
  "vdj_deck": 1
}
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| VirtualDJ tools not found | virtualdj-mcp not installed | `pip install -e D:/Dev/repos/virtualdj-mcp` |
| Plex tools not found | plex-mcp not installed | `pip install -e D:/Dev/repos/plexmcp` |
| "No results found in Plex" | Query doesn't match | Broaden search terms |
| "Could not get file path" | Plex track has no local file | Check Plex media file paths |
| Deck load fails | VirtualDJ not running | Start VirtualDJ Pro first |
| Automix queue not playing | Auto DJ not started | Use /dj/auto_dj_mode() after loading |
| "Deck number exceeds maximum (8)" | Too many decks requested | Limit to 8 decks |
| Recording not found | No recordings exist | Start a recording first |
| Slow playlist load | Large playlist | Reduce limit parameter |

## FAQ

**Q: Do I need VirtualDJ Pro?**
A: Yes. VirtualDJ Pro with MCP integration is required for deck control. The free version may not expose the necessary API.

**Q: Can I use this without Plex?**
A: The cross-server tools require Plex. Without Plex, only standalone VirtualDJ tools (under /dj/) are available.

**Q: What's the max number of decks?**
A: VirtualDJ supports up to 8 decks. multi_deck_plex_load will refuse queries beyond deck 8.

**Q: Can I load songs from other sources?**
A: Currently Plex is the only supported media source. The architecture could be extended to support other libraries.

**Q: Do I need the full audio files or is streaming enough?**
A: VirtualDJ needs actual audio files on disk. Plex must have local file paths, not just streaming URLs.

**Q: Can I pre-cue tracks?**
A: Yes. Load tracks to specific decks, then use /dj/ controls to manage cue points and monitoring.

**Q: How do I stop automix?**
A: Use /dj/auto_dj_mode(duration_minutes=0) or the VirtualDJ GUI.

**Q: Can I save multiple recordings?**
A: Yes. Each recording is given a unique name. List recordings with /dj/list_recordings().

## Advanced Workflow Examples

### Wedding Reception DJ Workflow
Complete wedding reception workflow from setup to archive:
```
# Pre-event: Create reception playlist in Plex
# (Use Plex web UI or /plex/plex_playlist to create)

# Check both servers are ready
hub_status()

# Load first dance song and special moments to decks
plex_to_deck(search_query="First Dance Song Name", deck_id=1)

# Load dinner music playlist to automix
plex_playlist_to_automix(playlist_name="Dinner Jazz", shuffle=true, limit=30)

# Start recording the reception
/dj/start_recording(name="Smith_Wedding_2025")

# Transition to party mode
plex_playlist_to_automix(playlist_name="Party Dance Hits", shuffle=true, limit=60)

# Load the next keynote song
plex_to_deck(search_query="Cake Cutting Song", deck_id=2)

# Monitor levels
/dj/get_performance_metrics()

# End of night: stop recording
/dj/stop_recording()

# Archive mix to Plex
record_mix_to_plex(mix_name="Smith Wedding Reception", plex_library="Music")

# Save final status
hub_status()
```

### Radio Show Production Workflow
Produce a weekly radio show with consistent format:
```
# Step 1: Load intro and theme music
plex_to_deck(search_query="Show Intro Theme", deck_id=1)
plex_to_deck(search_query="Voiceover Intro Track", deck_id=2)

# Step 2: Build the main set from a curated Plex playlist
plex_playlist_to_automix(playlist_name="Radio Show Week 12", shuffle=false, limit=20)

# Step 3: Load station IDs and ad breaks at specific decks
plex_to_deck(search_query="Station ID 2025", deck_id=7)
plex_to_deck(search_query="Ad Break Package", deck_id=8)

# Step 4: Start recording
/dj/start_recording(name="Radio_Show_Week12")

# Step 5: Run auto DJ for the main set
/dj/auto_dj_mode(duration_minutes=60)

# Step 6: Stop and archive
/dj/stop_recording()
record_mix_to_plex(mix_name="Radio Show Week 12 - April 2025")
```

### Club Night Preparation Workflow
Prepare for a multi-genre club night:
```
# Check system
hub_status()

# Load warm-up set (house/deep house)
multi_deck_plex_load(
  search_queries=[
    "Deep House Warm Up 1", "Deep House Warm Up 2",
    "Melodic Techno Transition", "Peak Time Banger 1",
    "Peak Time Banger 2", "Hard Techno Closer",
    "Encore Track", "Final Track"
  ],
  start_deck=1
)

# Prepare backup playlist
plex_to_deck(search_query="Emergency Backup Track", deck_id=8)

# Start recording for the full night
/dj/start_recording(name="Club_Night_2025_04_12")
```

### Multi-Room Music Distribution Workflow
For venues with multiple rooms or zones:
```
# Room 1: Main room peak time
plex_to_deck(search_query="Peak Time Track 1", deck_id=1)
plex_to_deck(search_query="Peak Time Track 2", deck_id=2)

# Room 2: Lounge/chill zone (via different VirtualDJ instance)
# Note: Would require a second VDJ instance or audio routing
plex_to_deck(search_query="Lounge Chill Track", deck_id=3)
plex_to_deck(search_query="Ambient Background", deck_id=4)

# Manage transitions between rooms
/dj/mixer_set_eq(deck=1, band="low", value=0.8)
/dj/mixer_set_eq(deck=3, band="high", value=0.5)

# Start recording main room only
/dj/start_recording(name="Main_Room_Set")
```

### Beatmatching and Harmonic Mixing Workflow
Use the /dj/ namespace tools for technical mixing:
```
# After loading tracks with plex_to_deck, use VDJ tools:
/dj/analyze_track(deck_id=1)    # Get BPM, key, cue points
/dj/analyze_track(deck_id=2)    # Get BPM, key for second track

/dj/beatgrid_sync(deck_id=2, source_deck=1)  # Sync BPM
/dj/key_lock(deck_id=2, enable=true)          # Preserve original key
/dj/mixer_set_eq(deck=2, band="low", value=0.5)  # EQ incoming track
/dj/mixer_set_crossfader(position=0.7)  # Smooth blend

# Monitor sync accuracy
/dj/get_deck_sync_offset(deck_id=2)
```

### Podcast Production Workflow
Record and archive a podcast using the cross-server tools:
```
# Step 1: Load podcast intro/outro
plex_to_deck(search_query="Podcast Intro Music", deck_id=1)

# Step 2: Set up voice track
# (Voice input is typically routed through VirtualDJ's mic channel)

# Step 3: Start recording
/dj/start_recording(name="Episode_42_Future_of_AI")

# Step 4: Load background music (low volume)
plex_to_deck(search_query="Podcast Background Bed", deck_id=2)
/dj/mixer_set_eq(deck=2, band="low", value=0.7)
/dj/mixer_set_eq(deck=2, band="mid", value=0.3)
/dj/mixer_set_eq(deck=2, band="high", value=0.3)
/dj/set_deck_volume(deck=2, volume=0.15)

# Step 5: Record, then stop
/dj/stop_recording()

# Step 6: Archive to Plex podcast library
record_mix_to_plex(mix_name="Episode 42 - Future of AI", plex_library="Podcasts")
```

## System Architecture

### Composite Server Design Pattern
The DJ Media Hub uses FastMCP's mount mechanism to compose two independent MCP servers into a unified namespace. The mount system creates namespace prefixes (/dj/ and /plex/) that transparently route tool calls to the appropriate backend server. This is fundamentally different from a proxy or bridge — the mounted servers run in the same Python process, sharing the same event loop and database of tool registrations. The composite server then adds its own root-level tools that orchestrate calls across both mounted servers internally.

The architecture enables cross-server workflows without any network overhead between the servers — they share the same process memory. Plex search results are passed directly to VirtualDJ control functions as Python objects, never serialized over the network. This makes the cross-server tools faster than any external orchestration could be.

### Namespace Resolution
When a tool call comes in with a prefixed name like /dj/load_track_to_deck, FastMCP strips the prefix and routes it to the VirtualDJ server's load_track_to_deck function. When an unprefixed tool like plex_to_deck is called, it executes in the composite server's own code, which can import and call functions from both mounted servers directly.

## VirtualDJ Deck Mapping

| Deck ID | Purpose | Default Key | Typical Use |
|---------|---------|-------------|-------------|
| 1 | Main Deck (Left) | C#m | Current playing track |
| 2 | Main Deck (Right) | F#m | Next track, pre-cue |
| 3 | Sample/Effects Deck | G#m | Loops, samples, acapellas |
| 4 | Extra Deck | Bbm | Additional track for quick switching |
| 5-8 | Performance Decks | Various | Multi-deck mixing, stems, show tracks |

## Plex-MCP Namespace Tool Reference

The mounted Plex tools provide comprehensive media server management accessible under the /plex/ prefix. The plex_library tool handles library CRUD with operations including list all libraries, get library details by ID, create new libraries with specific types and paths, update library settings with language and agent preferences, delete libraries, scan for new content, refresh metadata, optimize database, empty trash, clean bundles, add and remove library locations, and organize library content. Each operation has specific parameter requirements and returns structured results.

The plex_media tool provides media item operations including browse library contents with filtering by type and sort options, search for media across libraries with text queries, get detailed media information with cast, crew, ratings, and technical specs, get recently added items with configurable limits, and update metadata for specific items. The browse operation supports pagination through offset and limit parameters.

The plex_search tool provides advanced search capabilities including keyword search, multi-parameter advanced search combining genre, year, actor, director, rating, and content rating filters, suggestion queries for autocomplete-style partial matches, recent searches history, and saved searches for frequently used query patterns. The advanced search supports complex Boolean combinations of up to 12 filter parameters.

## VirtualDJ-MCP Namespace Tool Reference

The mounted VirtualDJ tools provide complete DJ control accessible under the /dj/ prefix. Deck operations include loading tracks from filesystem paths, play/pause/stop control per deck, cue point management (set, recall, clear), beatgrid synchronization between decks, key detection and lock, and deck volume and EQ control.

The automix system provides queue management (add, remove, reorder tracks), auto DJ mode with configurable transition styles (cut, fade, blend, spin, backspin, echo out), transition duration from 1-32 beats, and fadeout timing. The crossfader can be controlled with configurable curve settings.

Recording operations include start and stop recording with configurable format (WAV, MP3, AAC), quality settings, and automatic file naming. The recording library provides listing, sorting, and metadata access.

Effect chains support up to four effects per deck with configurable parameters and dry/wet mix. Available effects include flanger, phaser, reverb, echo, beat delay, filter, autopan, bitcrusher, distortion, and custom effect chains created through the VirtualDJ UI.

## Comprehensive Workflow Guide

### Scenario: Live Broadcast Production
Setting up a live radio or streaming broadcast requires precise coordination between Plex music discovery and VirtualDJ mixing. Start by checking both servers with hub_status. Create a broadcast playlist using Plex tools or an existing curated playlist. Load the playlist to automix for hands-free continuous music. Load specific tracks to decks 1 and 2 for live transitions, talk segments, and station IDs. Use deck 3 for jingles and sound effects loaded from a Plex search for your station's audio assets. Deck 4 can hold emergency backup tracks. Start recording to capture the broadcast for later podcast distribution.

### Scenario: DJ Battle Preparation
For competitive DJ battles, load tracks to all 8 decks for quick access during performance. Use specific decks for different genres or energy levels: decks 1-2 for main battling, deck 3 for acapellas, deck 4 for instrumental versions, decks 5-6 for backup tracks, and decks 7-8 for special effects and transition samples. The multi_deck_plex_load tool loads all tracks simultaneously from Plex search results.

### Scenario: Music Library Audit
Use the Plex tools to audit your music library and identify gaps. List all playlists to see what's organized. Search for specific artists or genres to check coverage. Identify tracks that could be used for specific gig types. Create targeted playlists for different events (weddings, corporate, clubs, lounges). The Plex integration provides full metadata for informed playlist curation.

### Scenario: Automated Podcast Publishing
Create a workflow for podcast production: record episodes with /dj/start_recording, produce the mix with automix and live elements, stop recording, archive to Plex with record_mix_to_plex, and the mix is immediately available through Plex for podcast clients. The recording quality can be configured through VirtualDJ's recording settings.

### Scenario: Multi-Venue Music Distribution
For DJs working across multiple venues, use Plex as the central music repository. Each venue's setup can be prepared in advance with venue-specific playlists. On arrival, connect the laptop, check hub_status, load the venue's playlist to automix, and have music playing within minutes. The Plex integration ensures consistent music availability across all venues.

### Scenario: Collaborative Remote DJ Session
Two or more DJs can collaborate remotely by sharing access to the same Plex library. Each DJ connects their own DJ Media Hub instance. Playlists created by one DJ are immediately visible to all others. Tracks loaded to decks are independent per instance. This enables collaborative playlist curation and coordinated multi-DJ sets.

## Restoration and Recovery Procedures

If a cross-server workflow fails mid-operation, the recovery procedure depends on where the failure occurred. If a plex_to_deck search succeeded but the deck load failed, retry the deck load directly with /dj/load_track_to_deck using the file path from the failed response. If a plex_playlist_to_automix partially loaded tracks, verify the automix queue and reload missing tracks individually. If a record_mix_to_plex file copy failed, check disk space and retry. If a recording was lost, check VirtualDJ's recording directory for the original file.

## Performance Tuning Guide

For optimal performance, ensure the Plex Media Server and VirtualDJ are running on the same machine or on the same high-speed local network. Network file paths between Plex and VirtualDJ must be consistent and accessible. Large playlists over 100 tracks should be loaded in batches of 50 to avoid timeout issues. The multi_deck_plex_load tool is rate-limited to prevent overwhelming the Plex server with parallel search requests. Recording quality settings in VirtualDJ affect file size and conversion time for record_mix_to_plex operations; use 320kbps MP3 for broadcast quality or WAV for archival quality.

## Monitoring and Debugging

Monitor cross-server workflow performance using hub_status for server availability, /dj/get_performance_metrics for VirtualDJ system load, and Plex's own monitoring tools for library health. If workflows are slow, check Plex server load (concurrent streams, transcoding), VirtualDJ CPU usage (effect chains, stems processing), and network latency between services. Log all operations for post-event analysis and workflow optimization. Use the hub_status tool before and after major operations to verify system health.

## Advanced Effect Chains and Transitions

VirtualDJ supports complex effect chains that can be applied to individual decks or the master output. Common effect chains for creative mixing include: filter sweep (low-pass filter automating from open to closed), echo fade (increasing echo feedback while decreasing volume), reverb wash (full reverb mix with decay automation), beat repeat (stutter effect synced to beat divisions), and brake effect (gradual slowdown to stop). Each effect has configurable parameters accessible through the /dj/effects tools.

Transition types available in Auto DJ mode include: cut (instant switch between tracks), fade (short crossfade), blend (long crossfade with EQ blending), spin (outgoing track spins down), backspin (outgoing track backspins), echo out (echo effect on outgoing track), and scratch (scratch transition). The transition duration can be set from 1 to 32 beats. The mix timing can match phrase boundaries for seamless transitions.

## Network Topology Requirements

For reliable cross-server operation, ensure both Plex Media Server and VirtualDJ are accessible from the same network. Plex typically runs on port 32400. VirtualDJ's MCP interface uses a configurable port (default varies by installation). Both services must be resolvable by hostname or IP address from the machine running DJ Media Hub. File paths between Plex and VirtualDJ must use consistent path formats. If Plex is on a different machine, ensure the media files are accessible over the network with the same path structure (network share, mapped drive, or symlinks).

## Workflow Automation Patterns

Common automation patterns for DJ Media Hub include: scheduled playlist rotation where different playlists load to automix at different times of day, event-driven transitions that switch between pre-cued tracks based on external triggers, and adaptive mixing that adjusts playlist energy levels based on time of night or crowd response monitoring. These patterns can be implemented by combining the hub's tools with external scheduling or event systems.

## Resource Management

VirtualDJ can use significant CPU resources when processing stems, running multiple effects, and managing 8 decks simultaneously. Monitor CPU usage with /dj/get_performance_metrics during heavy usage. Close unnecessary applications on the DJ machine to free resources. Reduce stems quality or disable stems processing on decks that do not require it. Use effect chains sparingly on master output as they affect all decks. Consider using a dedicated audio interface for lower latency and better performance.

## Backup and Recovery

Backup strategies for DJ Media Hub include: regularly export Plex playlists to external format, maintain a backup copy of the music library, save VirtualDJ configuration files, and document the automation rules and cross-server workflows. In case of system failure, restore the Plex library first, then reconfigure VirtualDJ, reconnect DJ Media Hub, and verify the cross-server tools with hub_status.

## Composing Effect Chains for Creative Mixing

Creating effective effect chains requires understanding how effects interact. A common chain for build-ups is filter + echo + reverb: start with the filter closing (low-pass at 200Hz), add echo at 50% feedback with 1/4 note timing, and apply reverb at 60% mix for space. The effects are applied in series, so the order matters. Use /dj/effects_set to configure each effect's parameters independently. Monitor the effect output using deck EQ adjustments to maintain clarity. For drops, reverse the effect chain: remove reverb first, then echo, then open the filter, creating a sense of release and energy.

## Creating Seamless Transitions with Beatgrind Sync

Beatgrid synchronization is essential for seamless transitions between tracks. After loading two tracks with plex_to_deck, analyze both with /dj/analyze_track to verify BPM and key detection. Adjust beatgrids with /dj/beatgrid_adjust if the detected BPM is incorrect. Use /dj/beatgrid_sync to match the incoming deck's tempo to the playing deck. Enable key lock on the incoming deck to preserve its original pitch. Use EQ to blend: reduce low frequencies on the incoming deck during the intro, then gradually bring them up as you reduce the outgoing deck's lows. The crossfader provides the final blend at the transition point.

## Performance Optimization for 8-Deck Mixing

Running 8 decks simultaneously requires significant processing power. To optimize performance: disable stems processing on decks that do not need it (stems separation uses significant CPU). Use lower quality effects on secondary decks. Close unnecessary background applications. Use a dedicated audio interface with ASIO drivers for lower latency. Monitor system performance with /dj/get_performance_metrics and reduce deck count if CPU exceeds 80%. Consider using 4 active decks with 4 standby decks rather than all 8 playing simultaneously.

## Integration with External Systems

The DJ Media Hub can be integrated with external event systems, lighting controllers, and broadcast automation through the MCP bridge mechanism. External tools can call the MCP tools through HTTP if the hub is running in HTTP mode. Lighting systems can receive beat-synchronized triggers for visual effects synchronized with the music. Broadcast systems can automate recording start/stop synchronized with show schedules. The MCP protocol provides a standardized interface for external system integration.

## Troubleshooting Specific Cross-Server Errors

If plex_to_deck returns "No results found in Plex", broaden the search query or verify Plex has media matching the query. If it returns "Could not get file path", the Plex media item may be a streaming-only item without local files. If it returns "VirtualDJ not running", start VirtualDJ Pro and ensure the MCP plugin is enabled in VirtualDJ's settings.

If plex_playlist_to_automix loads fewer tracks than expected, check that the tracks in the Plex playlist have accessible file paths. Some tracks may be streaming-only or have moved since the playlist was created. The limit parameter also caps the number of tracks loaded.

If record_mix_to_plex fails to find a recording, verify that a recording was started with /dj/start_recording before attempting to save. If the recording file was moved or deleted, the tool reports a file not found error.

If multi_deck_plex_load reports deck overflow errors, verify that the start_deck plus the number of search queries does not exceed 8.

## Additional Use Cases

The DJ Media Hub can be used for music discovery and library exploration workflows. Search for unfamiliar artists in Plex and load them to preview decks for quick auditioning. Build playlists based on BPM ranges for energy-matched sets. Use key detection for harmonic mixing recommendations. The cross-server tools enable rapid music discovery and experimentation without interrupting the main mix.

## Workflow Performance Benchmarks

Typical response times for cross-server tools under normal conditions: plex_to_deck completes in 500-1500ms including Plex search and VirtualDJ deck load. plex_playlist_to_automix takes 2-3 seconds for a 20-track playlist plus 100ms per additional track. record_mix_to_plex takes 1-10 seconds depending on file size (1 second per 100MB approximately). multi_deck_plex_load with 8 queries takes 4-12 seconds total. hub_status completes in 200-500ms. hub_help returns instantly. Factors that increase response time include Plex server load, network latency between services, and VirtualDJ CPU usage during complex mixing operations.

## Advanced Automation Patterns

For recurring events, create automation sequences that combine the hub's tools with external scheduling. A weekly radio show workflow: load the weekly playlist from Plex to automix, set automix to run for the show duration, start recording at show start time, archive the recording to Plex after the show ends, and log the operation for show notes. These steps can be orchestrated through the MCP tools with appropriate timing between each step.

## Cross-Server Workflow Design Principles

When designing custom workflows using the hub's tools, follow these principles: always verify server availability with hub_status before starting a workflow. Handle partial failures gracefully - if one deck load fails, continue with the remaining queries. Monitor timing between operations - allow sufficient time for VirtualDJ to process each track load before sending the next command. Use the response messages from each tool to inform the next step in the workflow.

## Audio Routing and Output Configuration

VirtualDJ supports multiple audio output configurations for different venue setups. Configure audio routing through VirtualDJ's settings panel for stereo output, multi-channel output for zone mixing in different rooms, or separate headphone output for cue monitoring. The server does not configure audio routing directly but the loaded tracks play through VirtualDJ's currently configured audio outputs.

## VirtualDJ Plugin Configuration

The VirtualDJ MCP plugin must be enabled for the server to connect. In VirtualDJ, open Settings, navigate to the MCP/API section, and ensure the MCP server option is enabled. Note the port number displayed as it must match the configuration in the virtualdj_mcp package. The plugin enables external control of VirtualDJ through the MCP protocol, which is the communication channel used by DJ Media Hub's /dj/ namespace tools.

## System Requirements

The DJ Media Hub requires Python 3.10 or later, access to a running VirtualDJ Pro instance with MCP plugin enabled, and access to a running Plex Media Server with valid authentication. Both VirtualDJ and Plex can run on the same machine or on separate machines accessible over the local network. File paths between the two systems must be consistent and accessible from the machine running DJ Media Hub.

## DJ Media Hub Architecture Summary

The DJ Media Hub composite server architecture provides unified access to VirtualDJ deck control and Plex media library management through a single MCP server connection. Cross-server tools enable powerful workflows that would be difficult to orchestrate manually, including simultaneous multi-deck loading from Plex search results and automated playlist-to-automix conversion.

The DJ Media Hub mounts both servers under namespaced prefixes for direct access while providing cross-server composite tools that orchestrate operations across both systems simultaneously.
