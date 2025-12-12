#!/usr/bin/env python3
"""
MCP Loader for CompText Codex Bundle.
Fetches, caches, and loads the codex bundle from GitHub releases.
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import requests
except ImportError:
    print("Error: requests package not installed. Run: pip install requests")
    exit(1)


class CodexLoader:
    """Load and cache CompText codex bundle."""

    def __init__(self, bundle_url: Optional[str] = None, cache_dir: Optional[str] = None):
        self.bundle_url = bundle_url or os.getenv(
            'CODEX_BUNDLE_URL',
            'https://github.com/ProfRandom92/comptext-codex/releases/latest/download/codex.bundle.latest-stable.json'
        )
        self.cache_dir = Path(cache_dir or os.getenv('CODEX_CACHE_DIR', '/var/cache/comptext'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'codex.bundle.json'
        self.checksum_file = self.cache_dir / 'codex.bundle.json.sha256'

    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _download_bundle(self) -> None:
        """Download codex bundle from URL."""
        print(f"Downloading codex bundle from {self.bundle_url}...")
        response = requests.get(self.bundle_url, timeout=30)
        response.raise_for_status()

        # Write bundle
        with open(self.cache_file, 'wb') as f:
            f.write(response.content)

        # Compute and save checksum
        checksum = self._compute_sha256(self.cache_file)
        with open(self.checksum_file, 'w') as f:
            f.write(checksum)

        print(f"✅ Downloaded and cached codex bundle (SHA-256: {checksum[:16]}...)")

    def load(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Load codex bundle, downloading if necessary."""
        if force_refresh or not self.cache_file.exists():
            self._download_bundle()

        with open(self.cache_file, 'r') as f:
            return json.load(f)

    def get_modules(self) -> list:
        """Get list of modules."""
        bundle = self.load()
        return bundle.get('modules', [])

    def get_commands(self, module: Optional[str] = None) -> list:
        """Get list of commands, optionally filtered by module."""
        bundle = self.load()
        commands = bundle.get('commands', [])
        if module:
            commands = [cmd for cmd in commands if cmd.get('module') == module]
        return commands

    def get_profiles(self) -> list:
        """Get list of profiles."""
        bundle = self.load()
        return bundle.get('profiles', [])


def main():
    """CLI for testing the loader."""
    loader = CodexLoader()

    print("Loading CompText Codex...")
    bundle = loader.load()

    print(f"\n📦 Codex Bundle Loaded:")
    print(f"  Modules: {len(bundle.get('modules', []))}")
    print(f"  Commands: {len(bundle.get('commands', []))}")
    print(f"  Profiles: {len(bundle.get('profiles', []))}")

    print("\n📋 Modules:")
    for module in bundle.get('modules', []):
        print(f"  [{module['code']}] {module['name']} - {module.get('purpose', 'N/A')}")


if __name__ == '__main__':
    main()
