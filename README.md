# Survivor static site generator

This project generates a static `index.html` page from local images in `survivor_files`.

The site is built with Python and can be updated from the command line.

## Eliminated player state

The generator can persist eliminated players in `site_state.json`.

Behavior summary:

- If `--clear-eliminated` is used, the eliminated list is reset.
- If `--eliminated` is provided, that list is used for the current run.
- If neither is provided, the script loads the saved state.
- If no saved state exists or it cannot be read, the script falls back to its built-in default eliminated list.

## Project structure

- `survivor.py` - main static site generator
- `survivor_files/` - source images used in the generated page
- `index.html` - generated output file
- `site_state.json` - optional saved eliminated-player state
- `README.md` - project documentation