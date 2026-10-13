# dj-media-hub — MCP Server Capabilities

## Server Overview

DJ Media Hub is a composite MCP server that mounts multiple specialized MCP servers under unified namespaces, enabling cross-server workflows for professional media production and DJ automation. It bridges VirtualDJ-MCP (deck control, mixing, stems analysis, beatgrid, automix) with Plex-MCP (media library management, playlists, streaming) to create powerful multi-deck workflows that no single human could perform alone — searching a media library of thousands of tracks while simultaneously loading up to 8 decks with precision.

The server mounts VirtualDJ-MCP at the /dj/ prefix and Plex-MCP at the /plex/ prefix, making all original tools from both servers available under those namespaces. On top of this, DJ Media Hub provides 6 cross-server composite tools that chain operations across both systems: searching Plex and loading directly to a deck, converting entire Plex playlists into automated DJ sets, saving recorded mixes back to the Plex library, the legendary 8-deck simultaneous load workflow, and more.

The architecture allows the LLM to simultaneously browse Plex libraries, search for tracks, load decks, control mixing parameters, monitor performance, and manage recordings — all through a single MCP server connection. The hub_status tool reports the availability of all mounted servers and their cross-server capabilities.

## Tools

### plex_to_deck (Cross-Server Workflow)
Searches Plex library and loads the result directly to a VirtualDJ deck.
- **Parameters:**
  - search_query (str, required) — What to search for (artist, track name, album).
  - deck_id (int, optional, default 1) — VirtualDJ deck to load to (1-8).
  - search_type (str, optional, default "track") — Type of search: track, album, artist.
- **Returns:** {success, plex_result: {title, artist, album, file}, vdj_deck, message}
- **Behavior:** Searches Plex via PlexService, extracts the file path from the first result, and loads it to the specified VirtualDJ deck using VDJClient. If Plex has no results, returns a clear error.

### plex_playlist_to_automix (Cross-Server Workflow)
Loads a Plex playlist into VirtualDJ's automix queue for hands-free mixing.
- **Parameters:**
  - playlist_name (str, required) — Name of Plex playlist to load.
  - shuffle (bool, optional, default false) — Randomize track order before loading.
  - limit (int, optional, default 50) — Maximum number of tracks to load.
- **Returns:** {success, playlist, tracks_loaded, shuffle, message}
- **Behavior:** Retrieves all tracks from the named Plex playlist, extracts file paths, optionally shuffles them, then sequentially loads each track into VirtualDJ's automix queue.

### record_mix_to_plex (Cross-Server Workflow)
Saves a VirtualDJ recording to a Plex music library.
- **Parameters:**
  - mix_name (str, required) — Name for the mix in Plex (becomes the filename).
  - plex_library (str, optional, default "Music") — Target Plex library section.
  - recording_id (str, optional) — Specific VirtualDJ recording ID (uses latest if omitted).
- **Returns:** {success, source, destination, plex_library, message}
- **Behavior:** Gets the recording file path from VirtualDJ, copies it to the Plex library's "DJ Mixes" subdirectory with the given name, and triggers a Plex library scan to make it immediately available.

### multi_deck_plex_load (Cross-Server Workflow)
Loads multiple tracks from Plex to consecutive VirtualDJ decks in one call.
- **Parameters:**
  - search_queries (list[str], required) — List of search queries, one per deck.
  - start_deck (int, optional, default 1) — First deck to load to.
- **Returns:** {success, decks_loaded, total_queries, results: [{deck, query, success, ...}], message}
- **Behavior:** Iterates through each query, calls plex_to_deck internally for each, incrementing the deck ID. Stops at deck 8. Reports per-deck success/failure.

### hub_status
Gets the status of all mounted servers and cross-server capabilities.
- **Parameters:** None
- **Returns:** {hub_name, version, servers: {virtualdj: {available, running, mount}, plex: {available, connected, mount}}, cross_server_tools: [list]}
- **Behavior:** Probes VirtualDJ via VDJClient.is_running() and Plex via PlexService.test_connection().

### hub_help
Gets help and documentation for DJ Media Hub.
- **Parameters:** topic (str, optional, default "overview") — Help topic: overview, workflows, examples, plex, virtualdj.
- **Returns:** Formatted markdown help text.

## Mounted Namespaced Tools

### /dj/ (VirtualDJ-MCP) — 49 Tools
All VirtualDJ operations available under the /dj/ prefix:
- /dj/load_track_to_deck — Load audio file to a specific deck
- /dj/auto_dj_mode — Start/stop automatic mixing
- /dj/start_recording / /dj/stop_recording — Session recording
- /dj/get_performance_metrics — Deck performance data
- /dj/show_help — VirtualDJ tool documentation
- /dj/beatgrid_* — Beatgrid analysis and adjustment
- /dj/stems_* — Stems separation (vocals, drums, bass, other)
- /dj/mixer_* — EQ, crossfader, gain control
- /dj/playlist_* — VirtualDJ playlist management
- /dj/effects_* — DJ effects control
- /dj/config_* — VirtualDJ configuration

### /plex/ (Plex-MCP) — 15 Portmanteau Tools
All Plex operations available under the /plex/ prefix:
- /plex/plex_library — Library CRUD and scanning
- /plex/plex_media — Browse, search, metadata
- /plex/plex_search — Advanced search with filters
- /plex/plex_playlist — Playlist CRUD and management
- /plex/plex_collections — Collection management
- /plex/plex_streaming — Playback control and sessions
- /plex/plex_server — Server health and maintenance
- /plex/plex_user — User account management
- /plex/plex_performance — Transcoding and quality
- /plex/plex_metadata — Metadata refresh and update
- /plex/plex_organization — Library organization
- /plex/plex_quality — Quality profiles
- /plex/plex_reporting — Statistics and reports
- /plex/plex_rag — Semantic search and indexing
- /plex/plex_natural_assistant — Natural language Plex help

## Configuration

**Environment Variables:**
- VirtualDJ-MCP configuration via virtualdj_mcp package config
- Plex-MCP configuration via plex_mcp package config (PLEX_URL, PLEX_TOKEN)
- MCP_BRIDGE_URLS — Additional MCP bridge proxy URLs

**Dependencies:**
The server requires both virtualdj-mcp and plex-mcp packages to be installed and accessible:
```
pip install -e D:/Dev/repos/virtualdj-mcp
pip install -e D:/Dev/repos/plexmcp
```

**Default Ports:**
- The composite server itself runs on stdio or configurable HTTP port
- VirtualDJ typically communicates on its own protocol port
- Plex communicates on port 32400

## Data Sources

- **Plex Media Server** — Music library, playlists, metadata, file paths
- **VirtualDJ** — Deck state, loaded tracks, automix queue, recording files, performance data
- **Filesystem** — Track audio files (via Plex file paths and VirtualDJ recording output)

## Error Handling

All composite tools return consistent error patterns:
- Plex search failure: `{"success": false, "error": "No results found in Plex for: query"}`
- File path missing: `{"success": false, "error": "Could not get file path from Plex result"}`
- Recording not found: `{"success": false, "error": "No recordings found"}`
- File not found on disk: `{"success": false, "error": "Recording file not found: path"}`
- Deck overflow: `{"success": false, "error": "Deck number exceeds maximum (8)"}`

## Mounted Server Details

### VirtualDJ-MCP Namespace (/dj/)
The VirtualDJ integration provides 49 tools organized into the following categories, all accessible under the /dj/ prefix:

**Deck Control** — Load, unload, play, pause, stop, cue, and sync tracks on any of 8 decks. Each deck has independent transport controls, beatgrid synchronization, and waveform display data. The load_track_to_deck tool accepts a file path and deck number, automatically analyzing the track for BPM, key, and beat grid on load.

**Mixer Control** — Three-band EQ (low, mid, high) with adjustable frequency ranges and slopes per deck. Crossfader with configurable curve (linear, constant power, constant loudness, scratch). Gain and trim controls with peak limiting. Per-channel routing to main, monitor, or both outputs.

**Effects Engine** — Apply and chain effects on individual decks or the master output. Effects include flanger, phaser, reverb, echo/delay, beat delay, filter, autopan, bitcrusher, distortion, and custom effect chains. Parameters are fully controllable with dry/wet mix, rate, feedback, and effect-specific parameters.

**Stems and Analysis** — Real-time stems separation (vocals, drums, bass, other) using machine learning. BPM analysis with manual override. Key detection with Camelot wheel notation. Beatgrid creation and adjustment with downbeat detection. Waveform analysis with permanent display updates.

**Automation** — Auto DJ mode with configurable transition types (cut, fade, blend, spin, backspin, echo out, etc.), transition duration, and mix timing. Automix queue management for pre-planned setlists. Scheduled transitions between tracks based on beat matching.

**Playlist and Recording** — VirtualDJ playlist management including creation, editing, and reordering. Session recording in multiple formats (WAV, MP3, AAC) with configurable quality settings. Recording library with metadata (name, date, duration, file size).

**Performance Monitoring** — Real-time metrics including deck load percentage, CPU usage per effect chain, audio latency, buffer status, and overall system performance. Useful for identifying when the system is approaching its mixing limits.

### Plex-MCP Namespace (/plex/)
The Plex integration provides 15 portmanteau tools under the /plex/ prefix, each with multiple operations:

**Library Management** — Full CRUD for media libraries: create new libraries by type (movie, show, music, photo), update existing library settings (agent, scanner, language), delete libraries, scan for new content, refresh metadata, empty trash, optimize database, and clean bundles. The library tool has 12 operations covering the complete library lifecycle.

**Media Browsing** — Browse library contents with genre, year, rating, and unwatched filters. Search across all libraries with text queries. Get detailed media information including cast, crew, ratings, plot summaries, technical specs, file paths, and local artwork. Recently added items feed with configurable lookback.

**Playlist Management** — Complete playlist CRUD with add/remove items, reorder tracks, and share playlists with other users. Playlist analytics showing total duration, track count, genre distribution, and play history.

**Collection Management** — Create themed collections from cross-library items. Collections can be auto-populated based on metadata criteria (genre, year, actor, director) or manually curated.

**Advanced Search** — Multi-parameter Boolean search combining genre, year range, rating range, actor, director, studio, country, language, content rating, and collection membership. Saved searches for frequently used queries. Search suggestions for partial queries.

**Streaming Control** — List active sessions with client details, media info, transcode reason, and bandwidth usage. Remote playback control including play, pause, stop, seek, skip, volume adjustment, audio track selection, subtitle selection, and quality override.

**RAG and Metadata** — Semantic search using vector embeddings across metadata and subtitle content. External metadata enrichment from Wikipedia, TMDB, TVDB, and OMDb. The RAG system indexes titles, plots, genres, actors, directors, and subtitle dialogue for deep content discovery.

## Cross-Server Workflow Architecture

The composite architecture enables workflows that span both servers transparently. Here is how each cross-server tool chains operations:

**plex_to_deck** — This tool first calls the PlexService.search() method with the search query and limit=1. It extracts the file path from the first Plex result's media parts. Then it creates a VirtualDJClient connection and calls load_track(deck_id, file_path) to load the track. The entire operation requires both services to be available and the track file to be accessible from the VirtualDJ host machine.

**plex_playlist_to_automix** — The tool retrieves the complete track list for the named Plex playlist using PlaylistService. Each track's file path is extracted. If shuffle is enabled, the track list is randomized using Python's random.shuffle(). The track list is then capped to the limit parameter. Each file path is loaded into VirtualDJ's automix queue by sending automix_add commands sequentially. The automix queue then plays through the loaded tracks automatically.

**record_mix_to_plex** — The tool gets the recording file path from VirtualDJ's RecordingService, either by recording_id or by taking the latest recording. The file is then copied using shutil.copy2 to the Plex library's DJ Mixes subdirectory. Finally, PlexService.scan_library() is called to trigger a refresh so the new mix appears in the Plex UI immediately.

**multi_deck_plex_load** — This tool simply calls plex_to_deck in a loop, incrementing the deck ID for each query. It caps at 8 decks as VirtualDJ does not support more. Each query is independent, so if one fails (e.g., track not found), the others continue. The response includes per-query success/failure for detailed diagnostics.

## Error Handling Patterns

Each cross-server tool has specific error handling:

**Plex Connection Errors** — If PlexService fails to initialize or connect, the tool returns `{"success": false, "error": "Plex connection failed"}`. This typically means Plex_URL or PLEX_TOKEN is misconfigured or the Plex server is not running.

**VirtualDJ Connection Errors** — If VDJClient fails to connect, the tool returns `{"success": false, "error": "VirtualDJ not running or port unreachable"}`. Start VirtualDJ Pro with MCP integration enabled.

**File Access Errors** — If the track file extracted from Plex is not accessible from the VirtualDJ machine (e.g., networked drive not mounted), the deck load will fail with a file access error. Ensure both Plex and VirtualDJ can access the media files using the same paths.

**Deck Limits** — multi_deck_plex_load enforces the 8-deck limit. Any query beyond deck 8 is returned with a clear error message in the results array but does not abort the entire operation.

## Performance Notes

- plex_to_deck averages 500-2000ms depending on Plex server response time
- multi_deck_plex_load with 8 queries may take 4-15 seconds total
- record_mix_to_plex file copy time depends on recording size
- plex_playlist_to_automix with large playlists (200+ tracks) may take 30+ seconds
- All tools are async and non-blocking; the MCP server remains responsive

## Cross-Server Tool Response Details

The plex_to_deck tool returns the following detailed response structure: success boolean, plex_result object containing title (string name of the track loaded), artist (grandparentTitle from Plex), album (parentTitle from Plex), and file (the full file path extracted from Plex media parts). The vdj_deck field indicates which VirtualDJ deck the track was loaded to. The message field provides a human-readable summary.

The plex_playlist_to_automix tool returns success boolean, playlist string (the name of the playlist loaded), tracks_loaded integer count of tracks successfully added to the automix queue, shuffle boolean indicating whether the order was randomized, and a message field with a human-readable summary of the operation.

The record_mix_to_plex tool returns success boolean, source string (the original recording file path from VirtualDJ), destination string (the copied file path in the Plex library), plex_library string (the Plex library section used), and a message field with a summary.

The hub_status tool returns a comprehensive status object with hub_name and version strings, a servers object with virtualdj and plex entries each containing availability, running/connected status, mount prefix, and error information if the server is unavailable. The cross_server_tools array lists the tools that orchestrate across both mounted servers.

## VirtualDJ Advanced Control Reference

The mounted VirtualDJ tools under /dj/ provide access to all common DJ operations. Deck control includes load_track_to_deck which takes a file path and deck ID (1-8), analyzes the track for BPM and key automatically, and prepares it for playback. The play_pause and stop commands control individual deck transport. Auto DJ mode creates continuous mixing with configurable transition styles and durations.

The mixer controls include three-band EQ per deck (low, mid, high) with adjustable frequency ranges, a crossfader with configurable curve types (linear, constant power, constant loudness, and scratch curves), and per-deck gain with peak limiting. The effects engine supports chaining multiple effects per deck with adjustable dry/wet mix.

Beatgrid tools automatically detect BPM and beat positions on track load, with manual adjustment tools for fine-tuning. Key detection uses the Camelot wheel system for harmonic mixing guidance. Stems separation provides real-time extraction of vocals, drums, bass, and other melodic elements from any track.

## Plex-MCP Advanced Reference

The Plex tools under /plex/ provide complete media server management. Library operations include creating libraries by type (movie, show, music, photo, homevideos), configuring agents and scanners, managing folder locations, and performing maintenance like scanning, optimizing, emptying trash, and cleaning bundles.

Media discovery includes browsing by library with optional filters for genre, year, rating, and recently added items. Advanced search combines multiple parameters including title, actor, director, genre, year range, rating range, content rating, studio, country, language, and collection membership. Search suggestions provide autocomplete-style results.

Playback control enables listing active sessions with client and media details, remote play/pause/stop/seek, volume adjustment, subtitle and audio track selection, and quality override for bandwidth management.

## Configuration Requirements

The server requires both virtualdj-mcp and plex-mcp packages to be installed and importable as Python packages. These are typically installed as editable packages from their respective repository directories. The VirtualDJ Pro application must be running with MCP integration enabled for deck operations to function. The Plex Media Server must be accessible with a valid authentication token.

VirtualDJ configuration is managed through the virtualdj_mcp package's VDJConfig class, which reads environment variables and configuration files for the VirtualDJ connection parameters including host, port, and authentication. Plex configuration uses the PLEX_URL environment variable for the server URL and PLEX_TOKEN for authentication. These can also be provided directly in the package's configuration.

## Error Recovery Patterns

When a cross-server tool fails, the recovery approach depends on which service is unavailable. If Plex is unreachable, verify PLEX_URL and PLEX_TOKEN and ensure the Plex Media Server is running. If VirtualDJ is unreachable, ensure VirtualDJ Pro is running and the MCP plugin is enabled. If a track file path from Plex is not accessible from VirtualDJ, check that both applications can access the media files using the same network paths. If a recording is not found, verify that a recording was started with /dj/start_recording before calling record_mix_to_plex.

## Server Architecture and Design Decisions

The DJ Media Hub uses FastMCP's mount() mechanism to compose two independent MCP servers into a unified namespace. This is fundamentally different from a proxy or bridge approach. The mounted servers run in the same Python process, sharing the same event loop and tool registration database. This eliminates network overhead between the servers and enables direct Python function calls across server boundaries. The cross-server composite tools are implemented in the hub server's own code and import functions from both virtualdj_mcp and plex_mcp packages directly.

The mount system creates namespace prefixes (/dj/ and /plex/) that transparently route tool calls. When a client calls /dj/load_track_to_deck, FastMCP strips the /dj/ prefix and routes the call to VirtualDJ-MCP's load_track_to_deck function. This routing is invisible to the client, which simply calls tools by their prefixed names. The composite server's own tools (plex_to_deck, hub_status, etc.) do not have any prefix and are called directly by their names.

## Security and Access Control

The server inherits all security characteristics of the mounted servers. VirtualDJ authentication is managed by the virtualdj_mcp package. Plex authentication uses the configured PLEX_TOKEN. The server does not add its own authentication layer as it is designed to run on localhost. For remote access, run the server through a reverse proxy with authentication. The server does not expose any ports by default in stdio mode. In HTTP mode, bind to 127.0.0.1 to restrict access to localhost only.

## Cross-Server Tool Failure Modes

Each cross-server tool has specific failure modes that produce clear error messages. The plex_to_deck tool fails if PlexService.search returns zero results (returns message "No results found in Plex for: query"). It also fails if the Plex result has no file path in its media parts (returns message "Could not get file path from Plex result"). The VirtualDJClient may fail to connect if VirtualDJ is not running (returns message "VirtualDJ not running or port unreachable").

The plex_playlist_to_automix tool fails if the named playlist does not exist in Plex (returns message "Playlist not found or empty"). It may partially succeed if some tracks have missing file paths - those tracks are skipped with warnings in the server log.

The record_mix_to_plex tool fails if there are no recordings available in VirtualDJ (returns message "No recordings found"). It fails if the recording file no longer exists on disk (returns message "Recording file not found"). File copy failures are caught and reported with the specific filesystem error.

The multi_deck_plex_load tool never completely fails - it always returns per-query results even if individual deck loads fail. The overall success field is true if at least one deck load succeeded. This partial-failure behavior ensures that a single missing track does not prevent the other decks from loading.

## Testing and Verification

Before a performance, verify cross-server tool operation with a simple test: call hub_status to confirm both servers are available, then call plex_to_deck with a known track followed by /dj/get_performance_metrics to confirm the track loaded correctly. For automix verification, call plex_playlist_to_automix with a small test playlist and confirm tracks appear in the automix queue. For recording verification, start and stop a short recording, then verify it with record_mix_to_plex.

## Dependency Management

The server requires two external Python packages that are not included in its own dependencies. VirtualDJ-MCP must be installed from its repository at D:/Dev/repos/virtualdj-mcp or an equivalent location. Plex-MCP must be installed from its repository at D:/Dev/repos/plexmcp or D:/Dev/repos/plexmcp. Both packages must be importable at runtime. If either package is missing, the corresponding namespace mount fails with a logged warning and the cross-server tools that depend on that server return appropriate error messages. The server starts successfully even with partial mounts, allowing use of the remaining available functionality.

## Server Logging and Monitoring

The server logs all operations to stderr using the Rich console library. Each mounted server's import status is logged with success or failure details. Cross-server tool calls are logged with their parameters and results. Error conditions including connection failures, missing dependencies, and file access errors are logged with full stack traces for debugging. The server does not write log files by default; redirect stderr to a file for persistent logging. The hub_status tool provides a structured view of server health including mounted server status and cross-server tool availability.

## Environment Variable Configuration

The server inherits all configuration from the mounted server packages. VirtualDJ-MCP configuration uses VDJSERVER_HOST and VDJSERVER_PORT environment variables for the VirtualDJ connection endpoint. Plex-MCP configuration uses PLEX_URL and PLEX_TOKEN for Plex Media Server authentication. Additional MCP connections can be configured through MCP_TRANSPORT for HTTP mode, MCP_HTTP_PORT for the HTTP listener, and MCP_BRIDGE_URLS for additional proxy providers. The server itself does not require environment variables beyond those inherited from the mounted packages.
