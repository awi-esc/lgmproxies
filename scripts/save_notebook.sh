#!/bin/bash

daystamp=$(date +"%Y-%m-%d")
backup_dir=".ipynb-versions"
backup_dir_ipynb="$backup_dir/ipynb/$daystamp"
backup_dir_html="$backup_dir/html/$daystamp"
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")

mkdir -p "$backup_dir_ipynb"
mkdir -p "$backup_dir_html"

# List staged notebooks
# staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.ipynb$')
staged_files=$@

for file in $staged_files; do
    if [ -f "$file" ]; then
        # Optionally use nbstripout to get the cleaned version:
        # nbstripout "$file" > "$backup_dir_ipynb/$(basename "$file" .ipynb)_$timestamp.ipynb"
        \cp "$file" "$backup_dir_ipynb/$(basename "$file" .ipynb)_$timestamp.ipynb"
        # Convert to HTML
        jupyter nbconvert --to html "$file" --output-dir="$backup_dir_html" --output="$(basename "$file" .ipynb)_$timestamp.html"
    fi
done

rsync -raz ${backup_dir:-.ipynb-versions}/ maperr001@albedo1.dmawi.de:www/lgmproxies/