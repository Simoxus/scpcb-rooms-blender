# i'm sorry this is crappy clanker garbage, but i'm not writing all this myself D:

import bpy
import os
import sys
from pathlib import Path

# ============================================================
# Resource Relinker
# ============================================================

class ResourceRelinker:
    def __init__(self, blend_path: Path):
        self.blend_path = blend_path
        self.blend_dir = blend_path.parent
        self.search_paths = []
        print("[Relinker] ============================================================")
        print(f"[Relinker] Starting relativize and relink process for {blend_path}")
        print("[Relinker] ============================================================")

    # ------------------------------------------------------------
    # Setup search paths (default + nearby folders)
    # ------------------------------------------------------------
    def setup_search_paths(self):
        print("[Relinker] Setting up search paths...")

        # Add default search locations (recursive upwards for 3 levels)
        default_paths = []
        current = self.blend_dir
        for _ in range(3):
            default_paths.extend([
                current,
                current / "textures",
                current / "Textures",
                current / "assets",
                current / "Assets",
                current / "images",
                current / "Images",
                current / "sounds",
                current / "Sounds",
                current / "fonts",
                current / "Fonts",
            ])
            if current.parent == current:
                break
            current = current.parent

        self.search_paths = [p for p in default_paths if p.exists()]
        print(f"[Relinker] Using {len(self.search_paths)} default search locations.")

    # ------------------------------------------------------------
    # Recursive file finder
    # ------------------------------------------------------------
    def find_file(self, filename):
        """Search for a file in all search paths (recursively)."""
        if not filename:
            return None

        filename = Path(filename).name
        found_path = None

        for search_dir in self.search_paths:
            if not search_dir.exists():
                continue

            # Direct check
            candidate = search_dir / filename
            if candidate.exists():
                return str(candidate)

            # Recursive search
            try:
                for path in search_dir.rglob(filename):
                    if path.is_file():
                        found_path = path
                        break
            except (PermissionError, OSError):
                continue

            if found_path:
                break

        return str(found_path) if found_path else None

    # ------------------------------------------------------------
    # Process resources
    # ------------------------------------------------------------
    def process(self):
        print(f"[Relinker] Searching in {len(self.search_paths)} locations for missing files")
        print("[Relinker] Processing images...")

        stats = {
            "images": {"found": 0, "missing": 0, "relinked": 0},
            "libraries": {"found": 0, "missing": 0, "relinked": 0},
            "sounds": {"found": 0, "missing": 0, "relinked": 0},
            "fonts": {"found": 0, "missing": 0, "relinked": 0},
            "volumes": {"found": 0, "missing": 0, "relinked": 0},
            "movies": {"found": 0, "missing": 0, "relinked": 0},
        }

        def process_collection(collection, name, attr):
            for item in collection:
                filepath = getattr(item, attr, None)
                if not filepath:
                    continue
                if os.path.exists(bpy.path.abspath(filepath)):
                    stats[name]["found"] += 1
                    continue
                stats[name]["missing"] += 1
                filename = os.path.basename(filepath)
                newpath = self.find_file(filename)
                if newpath:
                    setattr(item, attr, bpy.path.relpath(newpath))
                    stats[name]["relinked"] += 1
                else:
                    print(f"[Relinker]   ✗ Could not find: {filename}")

        process_collection(bpy.data.images, "images", "filepath")
        process_collection(bpy.data.libraries, "libraries", "filepath")
        process_collection(bpy.data.sounds, "sounds", "filepath")
        process_collection(bpy.data.fonts, "fonts", "filepath")
        process_collection(bpy.data.volumes, "volumes", "filepath")
        process_collection(bpy.data.movieclips, "movies", "filepath")

        for key, stat in stats.items():
            print(f"[Relinker] {key.title()}: {stat['found']} relativized, {stat['missing']} missing, {stat['relinked']} relinked")

        print("[Relinker] ============================================================")
        print("[Relinker] Process complete!")
        print("[Relinker] ============================================================")

# ============================================================
# Main entry
# ============================================================

def main():
    args = sys.argv
    if "--" in args:
        idx = args.index("--") + 1
        targets = args[idx:]
    else:
        targets = args[1:]

    if not targets:
        print("ERROR: No target provided!")
        return

    # First argument: target file or folder
    target_path = Path(targets[0]).resolve()
    # Remaining arguments: optional extra search paths
    extra_search_paths = [Path(p).resolve() for p in targets[1:] if Path(p).exists()]

    print("[Relinker] Target:", target_path)
    if extra_search_paths:
        print("[Relinker] Extra search paths:")
        for p in extra_search_paths:
            print("   ", p)

    blend_files = []

    if target_path.is_dir():
        # Collect all .blend files recursively
        blend_files = list(target_path.rglob("*.blend"))
    elif target_path.suffix == ".blend":
        blend_files = [target_path]
    else:
        print("ERROR: Target is neither a .blend file nor a directory.")
        return

    if not blend_files:
        print("No .blend files found.")
        return

    for blend_file in blend_files:
        print()
        print(f"Processing: {blend_file}")
        bpy.ops.wm.open_mainfile(filepath=str(blend_file))
        relinker = ResourceRelinker(blend_path=blend_file)
        relinker.setup_search_paths()

        # Add extra paths from command line
        for extra in extra_search_paths:
            if extra not in relinker.search_paths:
                relinker.search_paths.append(extra)

        relinker.process()
        bpy.ops.wm.save_mainfile(filepath=str(blend_file))

# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    main()
