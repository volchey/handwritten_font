#!/bin/bash

# Check if ImageMagick and Potrace are installed
if ! command -v magick &> /dev/null; then
  echo "ImageMagick (magick) could not be found. Please install it first."
  exit 1
fi

if ! command -v potrace &> /dev/null; then
  echo "Potrace could not be found. Please install it first."
  exit 1
fi

# Set the directory to work on
if [ -n "$1" ]; then
  WORK_DIR="$1"
else
  WORK_DIR="."
fi

# Check if the directory exists
if [ ! -d "$WORK_DIR" ]; then
  echo "The specified directory does not exist: $WORK_DIR"
  exit 1
fi

# Loop through all PNG files in the specified directory
for pngfile in "$WORK_DIR"/*.png; do
  if [ -e "$pngfile" ]; then
    FILE=`basename "$pngfile" .png`
    # echo "Converting $pngfile to $WORK_DIR/$FILE.svg"
    magick "$pngfile" "$WORK_DIR/$FILE.pbm"
    potrace -s -o "$WORK_DIR/$FILE.svg" "$WORK_DIR/$FILE.pbm" --tight
    rm "$WORK_DIR/$FILE.pbm"
  else
    echo "No PNG files found in the directory: $WORK_DIR"
    exit 1
  fi
done

echo "Conversion complete."