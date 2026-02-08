#!/usr/bin/env python3
"""
CompText V5.0 ULTRA Stress Test - Legacy Monster Generator
Generates a massive Java monolith with 5000+ lines and hidden bugs
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import random

def generate_method(class_name, method_num, indent="    "):
    """Generate a spaghetti method with nested if-else blocks"""
    method_name = f"process{method_num}"
    lines = []
    
    lines.append(f"{indent}public void {method_name}(String input, int value) {{")
    lines.append(f"{indent}    // Business logic for {class_name}.{method_name}")
    
    # Add random nested if-else spaghetti
    depth = random.randint(3, 6)
    for d in range(depth):
        condition = random.choice([
            f"input != null && input.length() > {random.randint(0, 10)}",
            f"value > {random.randint(0, 100)}",
            f"input.contains(\"{random.choice(['test', 'prod', 'dev', 'data'])}\")",
            f"value % {random.randint(2, 5)} == 0"
        ])
        lines.append(f"{indent}{'    ' * (d + 1)}if ({condition}) {{")
        lines.append(f"{indent}{'    ' * (d + 2)}System.out.println(\"Processing level {d}\");")
    
    # Close all the if blocks
    for d in range(depth - 1, -1, -1):
        lines.append(f"{indent}{'    ' * (d + 1)}}} else {{")
        lines.append(f"{indent}{'    ' * (d + 2)}System.out.println(\"Alternative path {d}\");")
        lines.append(f"{indent}{'    ' * (d + 1)}}}")
    
    lines.append(f"{indent}}}\n")
    return lines

def generate_class(class_num, is_secret=False, secret_line=None):
    """Generate a service class with multiple methods"""
    class_name = f"Service{chr(65 + (class_num % 26))}{class_num}"
    lines = []
    
    lines.append(f"class {class_name} {{")
    lines.append(f"    private String name = \"{class_name}\";")
    lines.append(f"    private int counter = {random.randint(0, 1000)};")
    lines.append("")
    
    # Generate 10-20 methods per class
    num_methods = random.randint(10, 20)
    for m in range(num_methods):
        # Insert secret kill switch at specific position
        if is_secret and secret_line and len(lines) >= secret_line - 50:
            lines.append("    // CRITICAL: Emergency shutdown mechanism")
            lines.append("    public void secretKillSwitch() {")
            lines.append("        System.out.println(\"CRITICAL_BUG_FOUND_BY_COMPTEXT\");")
            lines.append("        // This should NEVER be called in production!")
            lines.append("        System.exit(1);")
            lines.append("    }\n")
            is_secret = False  # Only insert once
        
        lines.extend(generate_method(class_name, m))
    
    lines.append("}\n")
    return lines

def generate_monster():
    """Generate the full LegacyMonolith.java file"""
    lines = []
    
    # File header
    lines.append("/**")
    lines.append(" * LegacyMonolith.java")
    lines.append(" * GENERATED CODE - DO NOT EDIT MANUALLY")
    lines.append(" * This is a stress test for CompText V5.0 ULTRA")
    lines.append(" * Hidden bug location: ~line 4500")
    lines.append(" */\n")
    lines.append("package com.comptext.stresstest;\n")
    lines.append("import java.util.*;")
    lines.append("import java.io.*;")
    lines.append("import java.util.concurrent.*;")
    lines.append("import java.util.stream.*;\n")
    lines.append("public class LegacyMonolith {\n")
    
    # Generate 50 classes
    current_line = len(lines)
    for c in range(50):
        # Insert secret at ~line 4500 (in class 35-40)
        is_secret = (c == 38)  # Class 38 will contain the secret
        target_line = 4500 if is_secret else None
        
        class_lines = generate_class(c, is_secret, target_line)
        lines.extend(class_lines)
        
        # Add some spacing and comments
        if c % 10 == 9:
            lines.append(f"    // ========== Services {c-9} to {c} ==========\n")
    
    # Close main class
    lines.append("    // End of legacy monolith")
    lines.append("}\n")
    
    return lines

def main():
    """Generate and write the monster file"""
    print("CompText V5.0 ULTRA Stress Test - Monster Generator")
    print("=" * 60)
    print("Generating LegacyMonolith.java...")
    
    lines = generate_monster()
    
    # Write to file
    output_file = "LegacyMonolith.java"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    line_count = len(lines)
    file_size = sum(len(line.encode('utf-8')) for line in lines)
    
    print(f"[+] Generated: {output_file}")
    print(f"[+] Lines: {line_count:,}")
    print(f"[+] Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print(f"[+] Classes: 50+")
    print(f"[+] Methods: ~750+")
    print(f"[+] Secret bug hidden at: ~line 4500")
    print("=" * 60)
    print("\nReady for CompText V5.0 ULTRA stress test!")

if __name__ == "__main__":
    main()
