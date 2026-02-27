#!/usr/bin/env python3
"""
Package a skill into a distributable .skill file.
Usage: package-skill.py <skill-path> [output-dir]
"""

import argparse
import os
import sys
import zipfile
import re

def validate_skill(skill_path):
    """Validate skill structure."""
    errors = []
    
    if not os.path.isdir(skill_path):
        errors.append(f"Not a directory: {skill_path}")
        return errors
    
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if not os.path.isfile(skill_md):
        errors.append("Missing SKILL.md")
        return errors
    
    with open(skill_md, 'r') as f:
        content = f.read()
    
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
    else:
        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append("Invalid frontmatter format")
        else:
            frontmatter = parts[1].strip()
            
            if 'name:' not in frontmatter:
                errors.append("Missing 'name' in frontmatter")
            if 'description:' not in frontmatter:
                errors.append("Missing 'description' in frontmatter")
            
            name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                if not re.match(r'^[a-z0-9-]+$', name):
                    errors.append(f"Invalid skill name '{name}'")
    
    extraneous = ['README.md', 'INSTALLATION_GUIDE.md', 'QUICK_REFERENCE.md', 'CHANGELOG.md']
    for file in extraneous:
        if os.path.isfile(os.path.join(skill_path, file)):
            errors.append(f"Extraneous file: {file}")
    
    return errors

def package_skill(skill_path, output_dir):
    """Create .skill archive."""
    skill_name = os.path.basename(os.path.normpath(skill_path))
    output_path = os.path.join(output_dir, f"{skill_name}.skill")
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)
                zf.write(file_path, arcname)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Package a skill')
    parser.add_argument('skill_path', help='Path to skill directory')
    parser.add_argument('output_dir', nargs='?', default='.', help='Output directory')
    args = parser.parse_args()
    
    skill_path = os.path.abspath(args.skill_path)
    output_dir = os.path.abspath(args.output_dir)
    
    print(f"Validating {skill_path}...")
    errors = validate_skill(skill_path)
    
    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    
    print("Validation passed!")
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = package_skill(skill_path, output_dir)
    
    print(f"Created: {output_path}")

if __name__ == '__main__':
    main()
