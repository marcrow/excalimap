# Excalimap Watch Script

Simple file watcher that automatically regenerates the excalidraw mindmap when markdown files change.

## Requirements

```bash
pip install watchdog
```

## Usage

```bash
# From the project root
./scripts/watch.py -f path/to/mindmap/folder

# Or from anywhere
python3 /path/to/excalimap/scripts/watch.py -f path/to/mindmap/folder
```

### Options

- `-f, --folder`: Mindmap folder to watch (default: `mindmap/llm`)
- `-o, --output`: Output file (default: `output/mindmap.excalidraw`)
- `-t, --theme`: Theme - `dark` or `light` (default: `dark`)
- `-s, --style`: Style - `classic` or `handraw` (default: `classic`)

### Example

```bash
./scripts/watch.py -f ../ocd-mindmaps/excalimap/mindmap/request_smuggling/ -o output/request_smuggling.excalidraw
```

## Workflow with VSCode

1. Install the [Excalidraw VSCode extension](https://marketplace.visualstudio.com/items?itemName=pomdtr.excalidraw-editor)
2. Run the watch script pointing to your markdown folder
3. Open the generated `.excalidraw` file in VSCode
4. Edit your markdown files
5. When you see "✓ Generated" in the terminal, close and reopen the excalidraw file in VSCode to see the updates

## How it works

The script monitors the specified folder for changes to `.md` and `.yml` files. When a change is detected, it automatically runs `main.py` to regenerate the excalidraw mindmap file. The file is updated in place, so you just need to reopen it in VSCode to see the changes.
