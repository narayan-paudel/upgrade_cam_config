#!/bin/bash

# Check for the correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

SOURCE_DIR="$1"
DEST_DIR="$2"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' not found."
    exit 1
fi

# Check if destination directory exists, if not, create it
if [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
    echo "Created destination directory: $DEST_DIR"
fi

# Loop through all files in the source directory
for file in "$SOURCE_DIR"/*; do
    # Check if the item is a regular file
    if [ -f "$file" ]; then
        # Get the filename with its extension
        filename=$(basename -- "$file")
        
        # Get the filename without its extension
        # The '%%.*' pattern removes the longest matching suffix starting with a dot
        filename_no_ext="${filename%%.*}"

        echo $filename_no_ext

        cp "$file" "$DEST_DIR/Camera-$filename"
        # mv "$file" "$DEST_DIR"
        echo "Copied: $file -> $DEST_DIR/Camera-$filename"

    fi
done

echo "Script complete."


