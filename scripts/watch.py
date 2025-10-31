#!/usr/bin/env python3
"""
Simple file watcher that regenerates the excalidraw mindmap when markdown files change.
Use with VSCode Excalidraw extension for live preview.
"""

import os
import sys
import time
import argparse
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MindmapWatcher(FileSystemEventHandler):
    def __init__(self, mindmap_folder, output_file, theme='dark', style='classic'):
        self.mindmap_folder = mindmap_folder
        self.output_file = output_file
        self.theme = theme
        self.style = style
        self.last_generation = 0
        self.debounce_seconds = 1

    def generate_mindmap(self):
        current_time = time.time()
        if current_time - self.last_generation < self.debounce_seconds:
            return

        self.last_generation = current_time
        print(f"\n[{time.strftime('%H:%M:%S')}] Regenerating mindmap...")

        # Get the project root directory (parent of scripts/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)

        cmd = [
            'python3', os.path.join(project_root, 'main.py'),
            '-f', self.mindmap_folder,
            '-t', self.theme,
            '-s', self.style,
            '-o', self.output_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
            if result.returncode == 0:
                print(f"[{time.strftime('%H:%M:%S')}] ✓ Generated: {os.path.abspath(self.output_file)}")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] ✗ Generation failed")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ✗ Exception: {e}")

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.md', '.yml')):
            file_name = os.path.basename(event.src_path)
            print(f"[{time.strftime('%H:%M:%S')}] Changed: {file_name}")
            self.generate_mindmap()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.md', '.yml')):
            file_name = os.path.basename(event.src_path)
            print(f"[{time.strftime('%H:%M:%S')}] Created: {file_name}")
            self.generate_mindmap()

def main():
    parser = argparse.ArgumentParser(description='Watch mindmap folder and auto-regenerate excalidraw file')
    parser.add_argument('-f', '--folder', default='mindmap/llm', help='Mindmap folder to watch')
    parser.add_argument('-o', '--output', default='output/mindmap.excalidraw', help='Output file')
    parser.add_argument('-t', '--theme', choices=['dark', 'light'], default='dark', help='Theme')
    parser.add_argument('-s', '--style', choices=['classic', 'handraw'], default='classic', help='Style')

    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: Folder '{args.folder}' does not exist")
        sys.exit(1)

    print("=" * 70)
    print("Excalimap Watcher")
    print("=" * 70)
    print(f"Watching:  {args.folder}")
    print(f"Output:    {args.output}")
    print(f"Theme:     {args.theme}")
    print(f"Style:     {args.style}")
    print()

    # Initial generation
    watcher = MindmapWatcher(args.folder, args.output, args.theme, args.style)
    watcher.generate_mindmap()

    abs_output = os.path.abspath(args.output)

    print()
    print("=" * 70)
    print("📄 Open this file in VSCode with Excalidraw extension:")
    print(f"   {abs_output}")
    print("=" * 70)
    print()
    print("📝 The file will auto-regenerate when you edit .md/.yml files")
    print("   Just reopen the file in VSCode to see updates!")
    print()
    print("Press Ctrl+C to stop")
    print()

    # Start watching
    observer = Observer()
    observer.schedule(watcher, args.folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        observer.stop()

    observer.join()
    print("Stopped.")

if __name__ == "__main__":
    main()
