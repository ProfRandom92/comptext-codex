"""Comprehensive tests for CodexStore SQLite data layer."""

import json
import os
import tempfile
import threading
import pytest

from comptext_codex.store import CodexStore


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)
    # Clean up WAL files
    for ext in ["-wal", "-shm"]:
        wal_path = path + ext
        if os.path.exists(wal_path):
            os.unlink(wal_path)


@pytest.fixture
def store(temp_db):
    """Create a CodexStore instance with temp database."""
    s = CodexStore(temp_db)
    yield s
    s.close()


class TestCodexStoreConnection:
    """Test connection management."""

    def test_init_creates_schema(self, temp_db):
        """Test that schema is created on init."""
        store = CodexStore(temp_db)
        stats = store.stats()
        assert "modules" in stats
        assert "commands" in stats
        assert "profiles" in stats
        assert "catalog" in stats
        store.close()

    def test_close_and_reopen(self, temp_db):
        """Test closing and reopening connection."""
        store = CodexStore(temp_db)
        store.upsert_module({"code": "X", "name": "Test"})
        store.close()

        # Reopen
        store2 = CodexStore(temp_db)
        module = store2.get_module("X")
        assert module is not None
        assert module["name"] == "Test"
        store2.close()

    def test_thread_local_connections(self, temp_db):
        """Test thread-local connection handling."""
        store = CodexStore(temp_db)
        store.upsert_module({"code": "T", "name": "Thread Test"})

        results = []

        def worker():
            module = store.get_module("T")
            results.append(module is not None)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(results)
        store.close()


class TestModuleCRUD:
    """Test module CRUD operations."""

    def test_upsert_module_minimal(self, store):
        """Test upserting module with minimal data."""
        store.upsert_module({"code": "A", "name": "Core"})
        module = store.get_module("A")
        assert module["code"] == "A"
        assert module["name"] == "Core"
        assert module["purpose"] == ""
        assert module["token_priority"] == "medium"
        assert module["mcp_exposed"] is True

    def test_upsert_module_full(self, store):
        """Test upserting module with all fields."""
        store.upsert_module({
            "code": "B",
            "name": "Analysis",
            "purpose": "Text analysis and insight generation",
            "token_priority": "high",
            "mcp_exposed": False,
            "security": {"pii_safe": True, "threat_model": "test"},
            "privacy": {"dp_budget": "epsilon<=0.5"},
        })
        module = store.get_module("B")
        assert module["code"] == "B"
        assert module["purpose"] == "Text analysis and insight generation"
        assert module["token_priority"] == "high"
        assert module["mcp_exposed"] is False
        assert module["security"]["pii_safe"] is True
        assert "dp_budget" in module["privacy"]

    def test_upsert_module_update(self, store):
        """Test updating existing module."""
        store.upsert_module({"code": "C", "name": "Original"})
        store.upsert_module({"code": "C", "name": "Updated", "purpose": "New purpose"})
        module = store.get_module("C")
        assert module["name"] == "Updated"
        assert module["purpose"] == "New purpose"

    def test_get_module_not_found(self, store):
        """Test getting non-existent module returns None."""
        module = store.get_module("NONEXISTENT")
        assert module is None

    def test_list_modules(self, store):
        """Test listing all modules."""
        store.upsert_module({"code": "Z", "name": "Last"})
        store.upsert_module({"code": "A", "name": "First"})
        store.upsert_module({"code": "M", "name": "Middle"})

        modules = store.list_modules()
        assert len(modules) == 3
        # Should be sorted by code
        assert modules[0]["code"] == "A"
        assert modules[1]["code"] == "M"
        assert modules[2]["code"] == "Z"


class TestCommandCRUD:
    """Test command CRUD operations."""

    def test_upsert_command_minimal(self, store):
        """Test upserting command with minimal data."""
        store.upsert_module({"code": "A", "name": "Core"})
        store.upsert_command({"module": "A", "command": "test"})

        cmd = store.get_command("A", "test")
        assert cmd["module"] == "A"
        assert cmd["command"] == "test"
        assert cmd["syntax"] == ""
        assert cmd["examples"] == []
        assert cmd["aliases"] == []
        assert cmd["token_cost_hint"] == 0

    def test_upsert_command_full(self, store):
        """Test upserting command with all fields."""
        store.upsert_module({"code": "B", "name": "Analysis"})
        store.upsert_command({
            "module": "B",
            "command": "analyze",
            "syntax": "@B:analyze[type=<type>]",
            "description": "Analyze text for insights",
            "examples": ["@B:analyze[type=sentiment]", "@B:analyze[type=topic]"],
            "aliases": ["analyse", "check"],
            "token_cost_hint": 50,
            "mcp_exposed": True,
        })

        cmd = store.get_command("B", "analyze")
        assert cmd["syntax"] == "@B:analyze[type=<type>]"
        assert cmd["description"] == "Analyze text for insights"
        assert len(cmd["examples"]) == 2
        assert "analyse" in cmd["aliases"]
        assert cmd["token_cost_hint"] == 50
        assert cmd["mcp_exposed"] is True

    def test_upsert_command_update(self, store):
        """Test updating existing command."""
        store.upsert_module({"code": "C", "name": "Formatting"})
        store.upsert_command({"module": "C", "command": "format", "description": "Old"})
        store.upsert_command({"module": "C", "command": "format", "description": "New"})

        cmd = store.get_command("C", "format")
        assert cmd["description"] == "New"

    def test_get_command_not_found(self, store):
        """Test getting non-existent command returns None."""
        store.upsert_module({"code": "A", "name": "Core"})
        cmd = store.get_command("A", "nonexistent")
        assert cmd is None

    def test_list_commands_all(self, store):
        """Test listing all commands."""
        store.upsert_module({"code": "A", "name": "Core"})
        store.upsert_module({"code": "B", "name": "Analysis"})
        store.upsert_command({"module": "A", "command": "cmd1"})
        store.upsert_command({"module": "A", "command": "cmd2"})
        store.upsert_command({"module": "B", "command": "analyze"})

        commands = store.list_commands()
        assert len(commands) == 3

    def test_list_commands_by_module(self, store):
        """Test listing commands filtered by module."""
        store.upsert_module({"code": "A", "name": "Core"})
        store.upsert_module({"code": "B", "name": "Analysis"})
        store.upsert_command({"module": "A", "command": "cmd1"})
        store.upsert_command({"module": "A", "command": "cmd2"})
        store.upsert_command({"module": "B", "command": "analyze"})

        commands = store.list_commands(module="A")
        assert len(commands) == 2
        assert all(c["module"] == "A" for c in commands)

    def test_search_commands(self, store):
        """Test searching commands."""
        store.upsert_module({"code": "A", "name": "Core"})
        store.upsert_command({"module": "A", "command": "format", "description": "Format text"})
        store.upsert_command({"module": "A", "command": "parse", "description": "Parse input"})
        store.upsert_command({"module": "A", "command": "transform", "aliases": ["fmt"]})

        # Search by command name
        results = store.search_commands("format")
        assert len(results) >= 1

        # Search by description
        results = store.search_commands("text")
        assert len(results) >= 1

        # Search by alias
        results = store.search_commands("fmt")
        assert len(results) >= 1


class TestProfileCRUD:
    """Test profile CRUD operations."""

    def test_upsert_profile_minimal(self, store):
        """Test upserting profile with minimal data."""
        store.upsert_profile({"name": "default"})
        profile = store.get_profile("default")
        assert profile["name"] == "default"
        assert profile["description"] == ""
        assert profile["enabled_modules"] == []
        assert profile["default_settings"] == {}

    def test_upsert_profile_full(self, store):
        """Test upserting profile with all fields."""
        store.upsert_profile({
            "name": "developer",
            "description": "Profile for developers",
            "enabled_modules": ["A", "B", "G"],
            "default_settings": {"verbose": True, "timeout": 30},
        })
        profile = store.get_profile("developer")
        assert profile["description"] == "Profile for developers"
        assert "A" in profile["enabled_modules"]
        assert profile["default_settings"]["verbose"] is True

    def test_upsert_profile_update(self, store):
        """Test updating existing profile."""
        store.upsert_profile({"name": "test", "description": "Old"})
        store.upsert_profile({"name": "test", "description": "New"})
        profile = store.get_profile("test")
        assert profile["description"] == "New"

    def test_get_profile_not_found(self, store):
        """Test getting non-existent profile returns None."""
        profile = store.get_profile("nonexistent")
        assert profile is None

    def test_list_profiles(self, store):
        """Test listing all profiles."""
        store.upsert_profile({"name": "z_last"})
        store.upsert_profile({"name": "a_first"})
        profiles = store.list_profiles()
        assert len(profiles) == 2
        assert profiles[0]["name"] == "a_first"


class TestCatalogCRUD:
    """Test catalog CRUD operations."""

    def test_add_catalog_entry_minimal(self, store):
        """Test adding catalog entry with minimal data."""
        entry_id = store.add_catalog_entry({"title": "Test Entry"})
        assert entry_id > 0

        catalog = store.list_catalog()
        assert len(catalog) == 1
        assert catalog[0]["title"] == "Test Entry"
        assert catalog[0]["entry_type"] == "documentation"

    def test_add_catalog_entry_full(self, store):
        """Test adding catalog entry with all fields."""
        store.add_catalog_entry({
            "title": "API Guide",
            "description": "Comprehensive API documentation",
            "module_ref": "F",
            "tags": ["api", "documentation", "guide"],
            "entry_type": "tutorial",
        })

        catalog = store.list_catalog()
        entry = catalog[0]
        assert entry["title"] == "API Guide"
        assert entry["module_ref"] == "F"
        assert "api" in entry["tags"]
        assert entry["entry_type"] == "tutorial"

    def test_list_catalog_by_type(self, store):
        """Test listing catalog filtered by entry type."""
        store.add_catalog_entry({"title": "Doc 1", "entry_type": "documentation"})
        store.add_catalog_entry({"title": "Tutorial 1", "entry_type": "tutorial"})
        store.add_catalog_entry({"title": "Doc 2", "entry_type": "documentation"})

        docs = store.list_catalog(entry_type="documentation")
        assert len(docs) == 2
        assert all(e["entry_type"] == "documentation" for e in docs)

    def test_list_catalog_by_module(self, store):
        """Test listing catalog filtered by module reference."""
        store.add_catalog_entry({"title": "Module A Doc", "module_ref": "A"})
        store.add_catalog_entry({"title": "Module B Doc", "module_ref": "B"})
        store.add_catalog_entry({"title": "Module A Guide", "module_ref": "A"})

        module_a = store.list_catalog(module_ref="A")
        assert len(module_a) == 2

    def test_list_catalog_combined_filters(self, store):
        """Test listing catalog with combined filters."""
        store.add_catalog_entry({"title": "A Doc", "module_ref": "A", "entry_type": "documentation"})
        store.add_catalog_entry({"title": "A Tutorial", "module_ref": "A", "entry_type": "tutorial"})
        store.add_catalog_entry({"title": "B Doc", "module_ref": "B", "entry_type": "documentation"})

        results = store.list_catalog(entry_type="documentation", module_ref="A")
        assert len(results) == 1
        assert results[0]["title"] == "A Doc"

    def test_search_catalog(self, store):
        """Test searching catalog."""
        store.add_catalog_entry({"title": "Python API", "description": "Python bindings"})
        store.add_catalog_entry({"title": "JavaScript SDK", "tags": ["js", "sdk"]})
        store.add_catalog_entry({"title": "CLI Guide", "description": "Command line usage"})

        # Search by title
        results = store.search_catalog("API")
        assert len(results) >= 1

        # Search by description
        results = store.search_catalog("Python")
        assert len(results) >= 1

        # Search by tag
        results = store.search_catalog("sdk")
        assert len(results) >= 1


class TestExportImport:
    """Test export and import functionality."""

    def test_export_bundle(self, store):
        """Test exporting entire store as bundle."""
        store.upsert_module({"code": "A", "name": "Core"})
        store.upsert_command({"module": "A", "command": "test"})
        store.upsert_profile({"name": "default"})
        store.add_catalog_entry({"title": "Docs"})

        bundle = store.export_bundle()
        assert "modules" in bundle
        assert "commands" in bundle
        assert "profiles" in bundle
        assert "catalog" in bundle
        assert len(bundle["modules"]) == 1
        assert len(bundle["commands"]) == 1

    def test_import_bundle(self, temp_db):
        """Test importing bundle into store."""
        bundle = {
            "modules": [
                {"code": "A", "name": "Core"},
                {"code": "B", "name": "Analysis"},
            ],
            "commands": [
                {"module": "A", "command": "cmd1"},
                {"module": "A", "command": "cmd2"},
            ],
            "profiles": [
                {"name": "default", "description": "Default profile"},
            ],
            "catalog": [
                {"title": "Entry 1"},
                {"title": "Entry 2"},
            ],
        }

        store = CodexStore(temp_db)
        counts = store.import_bundle(bundle)

        assert counts["modules"] == 2
        assert counts["commands"] == 2
        assert counts["profiles"] == 1
        assert counts["catalog"] == 2

        assert store.get_module("A") is not None
        assert store.get_module("B") is not None
        store.close()

    def test_import_bundle_idempotent(self, store):
        """Test that importing same bundle twice is idempotent."""
        bundle = {
            "modules": [{"code": "A", "name": "Core"}],
            "commands": [{"module": "A", "command": "test"}],
            "profiles": [],
            "catalog": [],
        }

        store.import_bundle(bundle)
        store.import_bundle(bundle)

        assert len(store.list_modules()) == 1
        assert len(store.list_commands()) == 1


class TestStatistics:
    """Test statistics functionality."""

    def test_stats_empty(self, store):
        """Test stats on empty database."""
        stats = store.stats()
        assert stats["modules"] == 0
        assert stats["commands"] == 0
        assert stats["profiles"] == 0
        assert stats["catalog"] == 0

    def test_stats_with_data(self, store):
        """Test stats with data."""
        store.upsert_module({"code": "A", "name": "Core"})
        store.upsert_module({"code": "B", "name": "Analysis"})
        store.upsert_command({"module": "A", "command": "cmd1"})
        store.upsert_command({"module": "A", "command": "cmd2"})
        store.upsert_command({"module": "B", "command": "analyze"})
        store.upsert_profile({"name": "default"})
        store.add_catalog_entry({"title": "Doc 1"})
        store.add_catalog_entry({"title": "Doc 2"})

        stats = store.stats()
        assert stats["modules"] == 2
        assert stats["commands"] == 3
        assert stats["profiles"] == 1
        assert stats["catalog"] == 2


class TestErrorHandling:
    """Test error handling."""

    def test_foreign_key_constraint(self, store):
        """Test that foreign key constraint is enforced."""
        with pytest.raises(Exception):
            store.upsert_command({"module": "NONEXISTENT", "command": "test"})

    def test_rollback_on_error(self, temp_db):
        """Test that transaction is rolled back on error."""
        store = CodexStore(temp_db)
        store.upsert_module({"code": "A", "name": "Core"})

        initial_count = len(store.list_commands())

        try:
            store.upsert_command({"module": "NONEXISTENT", "command": "bad"})
        except Exception:
            pass

        # Count should be unchanged
        assert len(store.list_commands()) == initial_count
        store.close()
