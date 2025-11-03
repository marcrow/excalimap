# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Excalimap is a Python tool that converts Markdown files into interactive mindmaps for Excalidraw. It was forked from the OCD Active Directory mindmap project to enable collaborative mindmap creation using markdown as the source format. The tool parses markdown files with special syntax and generates `.excalidraw` JSON files that can be opened in Excalidraw (browser or VSCode extension).

## Common Commands

### Basic Usage
```bash
# Generate mindmap from markdown files (Excalidraw JSON format)
python3 main.py -f <source_folder> -o <output.excalidraw>

# Generate SVG format (recommended to avoid font embedding issues)
python3 main.py -f <source_folder> -o <output.svg> --format svg

# Example with specific theme and style
python3 main.py -f ./mindmap/ad/ -o output/ad.excalidraw -t dark -s classic

# SVG export example
python3 main.py -f ./mindmap/ad/ -o output/ad.svg -t dark -s classic --format svg
```

### Development Workflow
```bash
# Setup environment (first time)
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Watch mode - auto-regenerate on file changes (Excalidraw format)
./scripts/watch.py -f <mindmap_folder>

# Watch mode for SVG output
./scripts/watch.py -f <mindmap_folder> -o output/mindmap.svg --format svg

# With specific options
./scripts/watch.py -f ./mindmap/ad/ -o output/mindmap.excalidraw -t dark -s classic
```

### Available Options
- **Format**: `--format excalidraw` (default) or `--format svg`
- **Theme**: `-t dark` or `-t light` (default: dark)
- **Style**: `-s classic` or `-s handraw` (default: classic)

### Output Formats
- **Excalidraw JSON** (`.excalidraw`): Can be opened in Excalidraw web app or VSCode extension
- **SVG** (`.svg`): Direct SVG export without font embedding issues. Use this if you experience XML parsing errors when exporting from Excalidraw.

### Docker Setup for Excalidraw
```bash
# Run local Excalidraw instance
docker run --rm -dit --name excalidraw -p 5000:80 excalidraw/excalidraw:latest
```

## Architecture

### Data Flow
1. **Parsing**: Markdown files (`*.md`) → Python objects (Container, Title, Command, Info, Out)
2. **Layout**: Objects positioned in 2D grid based on `matrix` in `conf.yml`
3. **Rendering**: Python objects → Excalidraw JSON elements with coordinates, styling, arrows
4. **Output**:
   - Excalidraw format: Single `.excalidraw` JSON file
   - SVG format: Converted from Excalidraw JSON to SVG using [svg_renderer.py](svg_renderer.py)

### Core Components

#### Main Entry Point
- [main.py](main.py) - CLI entry point, orchestrates parsing and rendering
  - Loads `conf.yml` configuration
  - Parses markdown files into Container objects
  - Calls `draw()` to position elements and generate JSON
  - Writes output `.excalidraw` file

#### Parsers
- [parsermd.py](parsermd.py) - Converts markdown syntax to Python objects
  - Handles markdown hierarchy: `#` (container), `##` (title), `-` (items)
  - Parses output chains (`>>>` and `||` syntax)
  - Detects CVE markers (`@CVE@`)
  - Extracts tool names for icon matching
  - Supports multi-line code blocks (``` syntax)
- [parserjson.py](parserjson.py) - Alternative JSON input parser (legacy)

#### Models ([models/](models/))
All models inherit from [MapObject](models/mapobject.py) which provides:
- Common `draw()` interface returning `(elements, end_x, end_y)`
- Child element layout (`draw_child()`)
- Output box layout (`draw_out()`)
- Arrow generation between parent-child relationships

**Model hierarchy:**
- `Container` - Top-level section box (from `# Header`)
- `Title` - Subsection within container (from `## Header`)
- `Command` - Code/command box with optional tool icon (from `` - `command` ``)
- `Info` - Plain text box (from `- text`)
- `Out` - Output/result box (from `>>> Output`)
- `Arrow` - Connections between elements
- `Icon` - Tool icons from `/icon` folder
- `MainTitle` - Mindmap title with logo

#### Configuration
- [config.py](config.py) - Global styling and layout constants
  - Theme settings (dark/light) - colors for background, text, borders, CVE highlighting
  - Style settings (classic/handraw) - roughness and font family
  - Dimensions for all element types (width, height, padding, spacing)
  - Font sizes and line widths

#### Utilities
- [utils.py](utils.py) - Helper functions
  - Text wrapping (`split_text()`)
  - List flattening for nested elements
  - Image catalog management (tool icons)

### Layout System

**Grid-based positioning:**
- `conf.yml` defines a `matrix` - 2D array of markdown filenames
- Each column in the matrix is transposed to create vertical layout
- Elements positioned using cumulative width/height calculations
- Spacing controlled by `Config.space_width` and `Config.space_height`

**Coordinate calculation:**
1. Main title drawn at top (0, 0)
2. Containers arranged in columns based on matrix
3. Within each container: titles stacked vertically
4. Within each title: commands/info items arranged vertically
5. Child items indented horizontally by `Config.space_width`
6. Output boxes positioned to the right of their source element

### Markdown Syntax

Each markdown file = one Container. See extensive syntax documentation in [readme.md](readme.md).

**Key syntax elements:**
- `# Name` - Container (top-level section)
- `## Title` - Title within container
- `- text` - Info item (plain text)
- `` - `command` `` - Command item (code block)
- `>>> Output` - Creates output box with arrow
- `||` - Parallel outputs (branching)
- `@CVE@` - Mark as CVE (special highlighting)
- `<!-- cve -->` - HTML comment to mark following element as CVE
- `[URL](URL)` - Link attached to previous item
- Multi-line code blocks with ``` fences

**Tool detection:**
- First word of command matched against `tools:` in `conf.yml`
- If matched, tool icon and link are attached
- Icon must exist in `/icon` folder

**Output chaining:**
- `>>> A >>> B` creates sequential chain: element → A → B
- `>>> A || B` creates parallel outputs: element → A and element → B
- Can combine: `>>> A >>> B || C >>> D` creates complex trees

### Configuration File Structure

Each mindmap folder requires `conf.yml`:

```yaml
main_title: "Mindmap Title"
main_title_logo: "logo_name"  # Icon name from /icon folder

# 2D layout grid (transposed to columns)
matrix:
  - ['file1', 'file2']  # Row 1
  - ['file3', '']       # Row 2 (file3 in col 1, empty col 2)

# Tool definitions (for icon and link auto-detection)
tools:
  nmap:
    icon: nmap       # Icon filename in /icon
    link: https://nmap.org

# Color palette (hex colors)
color_id:
  color_name: "#RRGGBB"

# Container colors (by container name)
container_color:
  "Container Name": color_name

# Output box colors (by output text)
out:
  "Output Text": color_name
```

## Development Notes

### File Watching
The [watch.py](scripts/watch.py) script uses `watchdog` to monitor `.md` and `.yml` files and auto-regenerates the mindmap. Includes 1-second debounce to avoid rapid regeneration. Best used with VSCode Excalidraw extension for live preview.

### Adding New Element Types
1. Create model class in [models/](models/) inheriting from `MapObject`
2. Implement `draw(x, y)` method returning `(elements, end_x, end_y)`
3. Elements must be Excalidraw JSON format (see existing models)
4. Add parsing logic in [parsermd.py](parsermd.py)

### Modifying Styles
- Global styling constants in [config.py](config.py)
- Theme colors set via `Config.set_theme('dark'|'light')`
- Style (roughness/fonts) set via `Config.set_style('classic'|'handraw')`
- Per-element colors come from `conf.yml` configuration

### Icon Management
- Icons stored in [/icon](icon/) folder
- Must be PNG format
- Referenced by filename (without extension) in `conf.yml`
- Converted to base64 and embedded in output JSON via `Utils.images_catalog`

### Coordinate System
- Origin (0, 0) at top-left
- All positions are absolute (not relative)
- Elements return their bounding box via `end_x`, `end_y`
- Parent elements calculate total size from children's bounding boxes
- Arrows drawn after element layout using stored coordinates
