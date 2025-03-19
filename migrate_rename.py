#!/usr/bin/env python
"""
Migration script to rename the package from novelwriter_idea to novel_writer.

This script:
1. Creates the new directory structure if it doesn't exist
2. Copies files from old structure to new structure with updated references
3. Preserves file permissions and timestamps
4. Generates a report of all changes made

Usage:
  python migrate_rename.py [--remove-old]

Options:
  --remove-old   Remove the old directories after successful migration
"""

import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
OLD_NAME = "novelwriter_idea"
NEW_NAME = "novel_writer"
OLD_IMPORT = r"(from|import)\s+(src\.)?novelwriter_idea"
NEW_IMPORT = r"\1 \2novel_writer"
OLD_MODULE = r"novelwriter_idea"
NEW_MODULE = r"novel_writer"

# Directory structure mappings
DIR_MAPPING = {
    "src/novelwriter_idea": "src/novel_writer",
    "src/novelwriter_idea/agents": "src/novel_writer/agents",
    "src/novelwriter_idea/config": "src/novel_writer/config",
    "src/novelwriter_idea/utils": "src/novel_writer/utils",
    "src/novelwriter_idea/tests": "src/novel_writer/tests",
    "src/novelwriter_idea/data": "src/novel_writer/data",
}

# Initialize counters for report
stats = {
    "directories_created": 0,
    "files_copied": 0,
    "files_modified": 0,
    "references_changed": 0,
}

def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    directory_path = Path(directory)
    if not directory_path.exists():
        directory_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
        stats["directories_created"] += 1

def copy_with_rename(source_file, target_file, replace_content=True):
    """Copy file with content replacements."""
    # Ensure target directory exists
    target_dir = os.path.dirname(target_file)
    ensure_directory(target_dir)
    
    # Check if it's a binary file
    is_binary = False
    try:
        with open(source_file, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        # This is likely a binary file, just copy it without modifications
        is_binary = True
        print(f"Binary file detected, copying without modifications: {source_file}")
        shutil.copy2(source_file, target_file)
        stats["files_copied"] += 1
        return
    
    replaced_content = content
    replacements = 0
    
    # Replace content if requested and not binary
    if replace_content and not is_binary:
        # Replace module name in various contexts
        new_content = re.sub(OLD_IMPORT, NEW_IMPORT, content)
        replacements += (new_content != content)
        content = new_content
        
        # Replace module name in strings and comments
        new_content = re.sub(OLD_MODULE, NEW_MODULE, content)
        replacements += (new_content != content)
        content = new_content
        
        replaced_content = content
    
    # Write to target file
    with open(target_file, 'w', encoding='utf-8') as file:
        file.write(replaced_content)
    
    # Copy permissions and timestamps
    shutil.copystat(source_file, target_file)
    
    # Update stats
    stats["files_copied"] += 1
    if replacements > 0:
        stats["files_modified"] += 1
        stats["references_changed"] += replacements
    
    print(f"Copied file: {source_file} -> {target_file} (replacements: {replacements})")

def copy_directory_with_rename(source_dir, target_dir):
    """Copy entire directory with content replacements."""
    # Skip if source doesn't exist
    if not os.path.exists(source_dir):
        print(f"Warning: Source directory does not exist: {source_dir}")
        return
    
    # Skip __pycache__ directories
    if os.path.basename(source_dir) == "__pycache__":
        print(f"Skipping __pycache__ directory: {source_dir}")
        return
    
    # Ensure target directory exists
    ensure_directory(target_dir)
    
    # Copy each file in the directory
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)
        
        if os.path.isdir(source_item):
            # Skip __pycache__ directories
            if os.path.basename(source_item) == "__pycache__":
                print(f"Skipping __pycache__ directory: {source_item}")
                continue
            # Recursively copy subdirectories
            copy_directory_with_rename(source_item, target_item)
        else:
            # Skip *.pyc files
            if source_item.endswith(".pyc"):
                print(f"Skipping .pyc file: {source_item}")
                continue
            # Copy file with replacements
            copy_with_rename(source_item, target_item)

def update_config_files():
    """Update the configuration files (setup.py, pyproject.toml, etc)."""
    config_files = [
        "setup.py",
        "pyproject.toml",
        "README.md",
        ".github/workflows/ci.yml",
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path):
            # Create a backup
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
            
            # Update the file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = re.sub(OLD_MODULE, NEW_MODULE, content)
            replacements = (new_content != content)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            stats["files_modified"] += replacements
            stats["references_changed"] += replacements
            
            print(f"Updated config file: {file_path} (backup: {backup_path})")

def update_tests():
    """Update test files to use the new package name."""
    test_dirs = ["tests"]
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
            
        for root, _, files in os.walk(test_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    
                    # Create a backup
                    backup_path = f"{file_path}.bak"
                    shutil.copy2(file_path, backup_path)
                    
                    # Update the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace imports
                    new_content = re.sub(OLD_IMPORT, NEW_IMPORT, content)
                    # Replace other references
                    new_content = re.sub(OLD_MODULE, NEW_MODULE, new_content)
                    
                    replacements = (new_content != content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    if replacements:
                        stats["files_modified"] += 1
                        print(f"Updated test file: {file_path} (backup: {backup_path})")

def create_init_files():
    """Create __init__.py files in the new directories."""
    for directory in DIR_MAPPING.values():
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as file:
                file.write(f'"""Package initialization for {NEW_NAME}."""\n\n')
            print(f"Created __init__.py file: {init_file}")
            stats["files_copied"] += 1

def main():
    """Main execution function."""
    start_time = datetime.now()
    print(f"Starting migration from {OLD_NAME} to {NEW_NAME} at {start_time}")
    
    # Step 1: Create new directory structure
    for old_dir, new_dir in DIR_MAPPING.items():
        ensure_directory(new_dir)
    
    # Step 2: Copy files with replacements
    for old_dir, new_dir in DIR_MAPPING.items():
        if os.path.exists(old_dir):
            copy_directory_with_rename(old_dir, new_dir)
    
    # Step 3: Create __init__.py files
    create_init_files()
    
    # Step 4: Update config files
    update_config_files()
    
    # Step 5: Update test files
    update_tests()
    
    # Generate report
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*50)
    print("Migration Report")
    print("="*50)
    print(f"Migration from {OLD_NAME} to {NEW_NAME}")
    print(f"Started: {start_time}")
    print(f"Ended: {end_time}")
    print(f"Duration: {duration}")
    print("\nStatistics:")
    print(f"  Directories created: {stats['directories_created']}")
    print(f"  Files copied: {stats['files_copied']}")
    print(f"  Files modified: {stats['files_modified']}")
    print(f"  References changed: {stats['references_changed']}")
    print("\nNext steps:")
    print("1. Test the new package structure: python -m src.novel_writer.cli --help")
    print("2. Verify imports and functionality in tests")
    
    # Check if we should remove old directories
    remove_old = "--remove-old" in sys.argv
    if remove_old:
        print("\nRemoving old directories...")
        for old_dir in DIR_MAPPING.keys():
            if os.path.exists(old_dir):
                print(f"Removing {old_dir}")
                shutil.rmtree(old_dir)
        print("Old directories removed.")
    else:
        print("3. Remove the old directory structure if everything works correctly")
        print("   Run with --remove-old to automatically remove the old directories")
    
    print("="*50)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migration script to rename the package from novelwriter_idea to novel_writer.")
    parser.add_argument("--remove-old", action="store_true", help="Remove the old directories after successful migration")
    args = parser.parse_args()
    
    main() 