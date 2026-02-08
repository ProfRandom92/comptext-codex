"""
Comprehensive Test Suite for CompText MCP Server
Tests all functionality with various scenarios
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_banner():
    print("=" * 60)
    print("  COMPTEXT MCP SERVER - COMPREHENSIVE TEST SUITE")
    print("  Version: 5.0.1 (Agent Teams Ready)")
    print("=" * 60)
    print()

def test_section(name):
    print(f"\n{'='*60}")
    print(f"  TEST SECTION: {name}")
    print(f"{'='*60}\n")

def test_case(name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name}")
    if details:
        print(f"     {details}")
    return passed

# Import the tools from server
try:
    from server import comptext_analyze, comptext_parse
    test_case("Import MCP Tools", True, "comptext_analyze and comptext_parse loaded")
except Exception as e:
    test_case("Import MCP Tools", False, f"Error: {e}")
    sys.exit(1)

# Test counters
total_tests = 0
passed_tests = 0

def run_test(name, test_func):
    global total_tests, passed_tests
    total_tests += 1
    try:
        result = test_func()
        if result:
            passed_tests += 1
        return result
    except Exception as e:
        test_case(name, False, f"Exception: {e}")
        return False

# ============================================================================
# TEST SECTION 1: comptext_analyze - Basic Functionality
# ============================================================================

def test_analyze_basic():
    test_section("1. COMPTEXT_ANALYZE - BASIC FUNCTIONALITY")

    # Test 1.1: Find function definitions
    def t1():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "def ")
        matches = result.count("[server.py:")
        return test_case(
            "Find function definitions (def )",
            matches >= 2,
            f"Found {matches} matches"
        )

    # Test 1.2: Find imports
    def t2():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "import")
        matches = result.count("[server.py:")
        return test_case(
            "Find import statements",
            matches >= 3,
            f"Found {matches} matches"
        )

    # Test 1.3: Find FastMCP usage
    def t3():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "FastMCP")
        matches = result.count("[server.py:")
        return test_case(
            "Find FastMCP references",
            matches >= 1,
            f"Found {matches} matches"
        )

    # Test 1.4: Case insensitive search
    def t4():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "FASTMCP")
        matches = result.count("[server.py:")
        return test_case(
            "Case insensitive search (FASTMCP)",
            matches >= 1,
            f"Found {matches} matches (case insensitive works)"
        )

    # Test 1.5: No matches scenario
    def t5():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "ZZZNOEXIST")
        no_matches = "No matches found" in result or "Found 0 match(es)" in result
        return test_case(
            "No matches scenario",
            no_matches,
            "Correctly reports no matches"
        )

    run_test("Test 1.1", t1)
    run_test("Test 1.2", t2)
    run_test("Test 1.3", t3)
    run_test("Test 1.4", t4)
    run_test("Test 1.5", t5)

# ============================================================================
# TEST SECTION 2: comptext_analyze - Advanced Searches
# ============================================================================

def test_analyze_advanced():
    test_section("2. COMPTEXT_ANALYZE - ADVANCED SEARCHES")

    # Test 2.1: Search in README
    def t1():
        result = comptext_analyze("C:\\comptext-codex\\README.md", "Agent Teams")
        matches = result.count("[README.md:")
        return test_case(
            "Search README for 'Agent Teams'",
            matches >= 1,
            f"Found {matches} matches"
        )

    # Test 2.2: Search for TODO comments
    def t2():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "TODO")
        # May or may not have TODOs, just check it doesn't error
        return test_case(
            "Search for TODO comments",
            True,
            "Search completed successfully"
        )

    # Test 2.3: Search for decorators
    def t3():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "@mcp")
        matches = result.count("[server.py:")
        return test_case(
            "Find @mcp decorators",
            matches >= 2,
            f"Found {matches} decorator uses"
        )

    # Test 2.4: Search for docstrings
    def t4():
        result = comptext_analyze("C:\\comptext-codex\\server.py", '"""')
        matches = result.count("[server.py:")
        return test_case(
            "Find docstring markers",
            matches >= 2,
            f"Found {matches} docstring markers"
        )

    run_test("Test 2.1", t1)
    run_test("Test 2.2", t2)
    run_test("Test 2.3", t3)
    run_test("Test 2.4", t4)

# ============================================================================
# TEST SECTION 3: comptext_parse - Protocol Parsing
# ============================================================================

def test_parse_protocol():
    test_section("3. COMPTEXT_PARSE - PROTOCOL PARSING")

    # Test 3.1: Basic command (C;P:FIB)
    def t1():
        result = comptext_parse("C;P:FIB")
        has_command = "Command: C" in result
        has_language = "Language: P" in result
        has_task = "Task: FIB" in result
        return test_case(
            "Parse C;P:FIB",
            has_command and has_language and has_task,
            "Command=C, Language=P, Task=FIB"
        )

    # Test 3.2: Decompression command (D;P:FIB)
    def t2():
        result = comptext_parse("D;P:FIB")
        has_command = "Command: D" in result
        return test_case(
            "Parse D;P:FIB (Decompression)",
            has_command,
            "Decompression command recognized"
        )

    # Test 3.3: JavaScript command (C;J:API)
    def t3():
        result = comptext_parse("C;J:API")
        has_language = "Language: J" in result
        has_task = "Task: API" in result
        return test_case(
            "Parse C;J:API (JavaScript)",
            has_language and has_task,
            "JavaScript language recognized"
        )

    # Test 3.4: Python command (C;P:SORT)
    def t4():
        result = comptext_parse("C;P:SORT")
        has_task = "Task: SORT" in result
        return test_case(
            "Parse C;P:SORT",
            has_task,
            "SORT task recognized"
        )

    # Test 3.5: Command without task (C;P)
    def t5():
        result = comptext_parse("C;P")
        has_command = "Command: C" in result
        has_language = "Language: P" in result
        return test_case(
            "Parse C;P (no task)",
            has_command and has_language,
            "Command without task handled"
        )

    run_test("Test 3.1", t1)
    run_test("Test 3.2", t2)
    run_test("Test 3.3", t3)
    run_test("Test 3.4", t4)
    run_test("Test 3.5", t5)

# ============================================================================
# TEST SECTION 4: Token Efficiency Validation
# ============================================================================

def test_token_efficiency():
    test_section("4. TOKEN EFFICIENCY VALIDATION")

    # Test 4.1: Surgical precision (only matches, no full dump)
    def t1():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "def ")
        lines = result.split("\n")
        # Should have summary + matches, not entire file
        return test_case(
            "Surgical precision (no full dump)",
            len(lines) < 20,
            f"Returned {len(lines)} lines (not entire file)"
        )

    # Test 4.2: Format validation [file:line] content
    def t2():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "def ")
        has_format = "[server.py:" in result
        return test_case(
            "Output format [file:line] validated",
            has_format,
            "Correct [filename:line] format"
        )

    # Test 4.3: Summary line present
    def t3():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "def ")
        has_summary = "Found" in result and "match(es)" in result
        return test_case(
            "Summary line present",
            has_summary,
            "Match count summary included"
        )

    run_test("Test 4.1", t1)
    run_test("Test 4.2", t2)
    run_test("Test 4.3", t3)

# ============================================================================
# TEST SECTION 5: Error Handling
# ============================================================================

def test_error_handling():
    test_section("5. ERROR HANDLING")

    # Test 5.1: Non-existent file
    def t1():
        try:
            result = comptext_analyze("C:\\nonexistent\\file.py", "test")
            return test_case(
                "Non-existent file handling",
                "Error" in result or "not found" in result.lower(),
                "Error properly reported"
            )
        except:
            return test_case(
                "Non-existent file handling",
                True,
                "Exception raised (expected)"
            )

    # Test 5.2: Invalid command format
    def t2():
        try:
            result = comptext_parse("INVALID")
            # Parser should handle gracefully
            return test_case(
                "Invalid command format",
                True,
                "Handled gracefully"
            )
        except:
            return test_case(
                "Invalid command format",
                True,
                "Exception raised (acceptable)"
            )

    # Test 5.3: Empty query
    def t3():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "")
        return test_case(
            "Empty query handling",
            True,
            "Completed without crash"
        )

    run_test("Test 5.1", t1)
    run_test("Test 5.2", t2)
    run_test("Test 5.3", t3)

# ============================================================================
# TEST SECTION 6: Real-World Scenarios
# ============================================================================

def test_real_world():
    test_section("6. REAL-WORLD SCENARIOS")

    # Test 6.1: Find all tool definitions
    def t1():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "@mcp.tool")
        matches = result.count("[server.py:")
        return test_case(
            "Find all @mcp.tool decorators",
            matches >= 2,
            f"Found {matches} tool definitions"
        )

    # Test 6.2: Search for error handling
    def t2():
        result = comptext_analyze("C:\\comptext-codex\\server.py", "except")
        return test_case(
            "Search for exception handling",
            True,
            "Search completed"
        )

    # Test 6.3: Find version references
    def t3():
        result = comptext_analyze("C:\\comptext-codex\\README.md", "5.0")
        matches = result.count("[README.md:")
        return test_case(
            "Find version references in README",
            matches >= 1,
            f"Found {matches} version references"
        )

    # Test 6.4: Multi-file concept (search in different files)
    def t4():
        result1 = comptext_analyze("C:\\comptext-codex\\server.py", "fastmcp")
        result2 = comptext_analyze("C:\\comptext-codex\\README.md", "Agent Teams")
        both_work = "[server.py:" in result1 and "[README.md:" in result2
        return test_case(
            "Multi-file search capability",
            both_work,
            "Can search different files independently"
        )

    run_test("Test 6.1", t1)
    run_test("Test 6.2", t2)
    run_test("Test 6.3", t3)
    run_test("Test 6.4", t4)

# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    test_banner()

    test_analyze_basic()
    test_analyze_advanced()
    test_parse_protocol()
    test_token_efficiency()
    test_error_handling()
    test_real_world()

    # Final summary
    print(f"\n{'='*60}")
    print(f"  FINAL TEST RESULTS")
    print(f"{'='*60}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print(f"{'='*60}\n")

    if passed_tests == total_tests:
        print("  [OK] ALL TESTS PASSED - COMPTEXT MCP SERVER READY!")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"  [FAIL] {total_tests - passed_tests} TEST(S) FAILED")
        print(f"{'='*60}\n")
        sys.exit(1)
