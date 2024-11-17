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

# Loop through all PNG files in the current directory
for pngfile in *.png; do
  if [ -e "$pngfile" ]; then
    FILE=`basename "$pngfile" .png`
    echo "Converting $pngfile to $FILE.svg"
    magick "$pngfile" "$FILE.pnm"
    potrace -s -o "$FILE.svg" "$FILE.pnm"
    rm "$FILE.pnm"
  else
    echo "No PNG files found in the current directory."
    exit 1
  fi
done

echo "Conversion complete."