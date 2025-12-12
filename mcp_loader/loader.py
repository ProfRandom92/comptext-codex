#!/usr/bin/env python3
"""
MCP Loader for CompText Codex Bundle.
"""
import json
import os
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
import hashlib

class CodexLoader:
    """Loader for CompText codex bundles."""

    def __init__(self, bundle_url=None, cache_dir=None):
        """
        Initialize loader.

        Args:
            bundle_url: URL to codex bundle JSON
            cache_dir: Local cache directory
        """
        self.bundle_url = bundle_url or os.environ.get('CODEX_BUNDLE_URL')
        self.cache_dir = Path(cache_dir or os.environ.get('CODEX_CACHE_DIR', '/tmp/comptext'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'codex.bundle.json'
        self.codex = None

    def load(self, force_refresh=False):
        """
        Load codex bundle from URL or cache.

        Args:
            force_refresh: Force download even if cache exists

        Returns:
            dict: Codex bundle data
        """
        if not force_refresh and self.cache_file.exists():
            print(f"Loading codex from cache: {self.cache_file}")
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.codex = json.load(f)
            return self.codex

        if not self.bundle_url:
            raise ValueError("No bundle URL specified")

        print(f"Downloading codex from: {self.bundle_url}")
        try:
            with urlopen(self.bundle_url) as response:
                data = response.read()
                self.codex = json.loads(data.decode('utf-8'))

                # Cache the bundle
                with open(self.cache_file, 'wb') as f:
                    f.write(data)

                print(f"Codex cached to: {self.cache_file}")
                return self.codex

        except URLError as e:
            raise Exception(f"Failed to download codex: {e}")

    def get_modules(self):
        """Get all modules."""
        if not self.codex:
            self.load()
        return self.codex.get('codex', {}).get('modules', [])

    def get_commands(self, module=None):
        """
        Get commands, optionally filtered by module.

        Args:
            module: Module code to filter by

        Returns:
            list: Commands
        """
        if not self.codex:
            self.load()

        commands = self.codex.get('codex', {}).get('commands', [])

        if module:
            return [c for c in commands if c.get('module') == module]

        return commands

    def get_profiles(self):
        """Get all profiles."""
        if not self.codex:
            self.load()
        return self.codex.get('codex', {}).get('profiles', [])

def main():
    """Example usage."""
    loader = CodexLoader()
    codex = loader.load()

    print(f"\nCodex Version: {codex.get('version')}")
    print(f"Modules: {codex.get('metadata', {}).get('modules_count', 0)}")
    print(f"Commands: {codex.get('metadata', {}).get('commands_count', 0)}")
    print(f"Profiles: {codex.get('metadata', {}).get('profiles_count', 0)}")

if __name__ == '__main__':
    main()
