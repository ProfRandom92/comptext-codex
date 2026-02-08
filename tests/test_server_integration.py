#!/usr/bin/env python3
"""Test CompText MCP Server Tools"""
import sys
import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from server import comptext_analyze, comptext_parse

print("="*60)
print("COMPTEXT MCP SERVER - TOOL TEST")
print("="*60)
print()

# Test 1: comptext_analyze
print("TEST 1: Analyzing server.py for 'def comptext'")
print("-" * 60)
result = comptext_analyze(os.path.join(ROOT_DIR, 'server.py'), 'def comptext')
# Remove emojis for console compatibility
result_clean = result.replace('✅', '[OK]').replace('🔍', '[SEARCH]').replace('❌', '[ERROR]')
print(result_clean)
print()

# Test 2: comptext_parse
print("TEST 2: Parsing CompText command 'C;P:FIB'")
print("-" * 60)
result2 = comptext_parse('C;P:FIB')
result2_clean = result2.replace('✅', '[OK]').replace('❌', '[ERROR]')
print(result2_clean)
print()

# Test 3: Search in README
print("TEST 3: Searching README.md for 'Agent Teams'")
print("-" * 60)
result3 = comptext_analyze(os.path.join(ROOT_DIR, 'README.md'), 'Agent Teams')
result3_clean = result3.replace('✅', '[OK]').replace('🔍', '[SEARCH]').replace('❌', '[ERROR]')
print(result3_clean)
print()

print("="*60)
print("ALL TESTS COMPLETED")
print("="*60)
