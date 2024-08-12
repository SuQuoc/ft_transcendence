#!/bin/bash

# Function to delete files in a directory but keep subdirectories
delete_files_in_directory() {
    local directory=$1
    for item in "$directory"/*; do
        if [ -f "$item" ]; then
            rm "$item"
            echo "Deleted file: $item"
        elif [ -d "$item" ]; then
            echo "Skipped directory: $item"
        fi
    done
}

# Example usage
# Using a relative path
target_directory="../uploads/images/profile"
delete_files_in_directory "$target_directory"