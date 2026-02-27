#!/usr/bin/env python3
"""
Initialize a new skill with proper directory structure.
Usage: init-skill.py <skill-name> [--resources scripts,references,assets]
"""

import argparse
import os
import sys
import re

SKILL_TEMPLATE = '''---
name: {skill_name}
description: {description}
---

# {skill_title}

Brief description of what this skill does.

## Usage

When to use this skill and how.

## Resources

{resources_section}
'''

def normalize_skill_name(name):
    """Convert to lowercase with hyphens only."""
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = name.strip('-')
    return name

def main():
    parser = argparse.ArgumentParser(description='Initialize a new skill')
    parser.add_argument('name', help='Skill name (will be normalized)')
    parser.add_argument('--path', default='.', help='Output directory')
    parser.add_argument('--resources', default='', help='Comma-separated: scripts,references,assets')
    parser.add_argument('--description', default='', help='Skill description')
    
    args = parser.parse_args()
    
    skill_name = normalize_skill_name(args.name)
    skill_title = skill_name.replace('-', ' ').title()
    
    if not skill_name:
        print("Error: Invalid skill name", file=sys.stderr)
        sys.exit(1)
    
    skill_dir = os.path.join(args.path, skill_name)
    if os.path.exists(skill_dir):
        print(f"Error: Directory already exists: {skill_dir}", file=sys.stderr)
        sys.exit(1)
    
    os.makedirs(skill_dir)
    
    resources = [r.strip() for r in args.resources.split(',') if r.strip()]
    valid_resources = {'scripts', 'references', 'assets'}
    
    resources_section = []
    for resource in resources:
        if resource in valid_resources:
            os.makedirs(os.path.join(skill_dir, resource))
            resources_section.append(f"- **{resource}/**: See [{resource}/]({resource}/) directory")
    
    description = args.description or f"Description of what {skill_name} does and when to use it"
    resources_text = '\n'.join(resources_section) if resources_section else "None yet."
    
    skill_content = SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title,
        description=description,
        resources_section=resources_text
    )
    
    with open(os.path.join(skill_dir, 'SKILL.md'), 'w') as f:
        f.write(skill_content)
    
    print(f"Created skill: {skill_dir}/")
    print(f"  - SKILL.md")
    for resource in resources:
        if resource in valid_resources:
            print(f"  - {resource}/")

if __name__ == '__main__':
    main()
