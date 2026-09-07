# renderE - The Open Source IntelliStar 1 Renderer

renderE is intended as a replacement for a VM emulating the IntelliStar 1, a system previously used by The Weather Channel to render Local on the 8s.

## renderE is far from finished! Expect bugs, issues, and crashes!

## Usage

1. Clone repository
2. Install Python dependencies
3. Run setup.py. This will guide you through setup, and allow you to change options
4. Place your background music in a folder called "bgm"
5. Run main.py.

### Arguments

The following arguments are supported by renderE:

* A positional argument will be treated as a URI for input.
* `-t` and `--trans` will give the window a transparent background (for overlaying).
* `-n` and `--noframe` will remove the window frame (useful for capture on mac).
* `-o` and `--offline` will disable fetching assets from the web.
* `-bgm` and `--bgmplayer` will play background music. This overrides stream audio.

### Commands

* Run `load.py local flavor`, replacing flavor with the i1 flavor, to load a presentation.
* Run `run.py local` to run the loaded presentation
* Run `toggleNationalLDL.py` with the next argument as either 1 or 0 to enable or disable the national LDL respectively. On Flat Rock, another argument (A or B) must be set to determine which LDL to cue.

### encodE

encodE is a data encoder bundled with RenderE. To use it, follow these instructions:

1. Set up renderE (including configuration)
2. While renderE is running, run encodE.py
3. Run a local forecast using the commands

* `-ns` and `--nosensor` disable SENSOR data that causes CC to show a mixed-case title
* `-wxs` and `--weatherscan` enable a mode that works with Weatherscan
* `-nt` and `--notraffic` disables traffic (if a key is added to the file)
* `-nb` and `--nobulletins` disables bulletins
* `-a` and `--automatic` encodes new data every 20 minutes
* `-c` and `--calm` run data encoding at a slower pace to use less CPU

## Support

Support is available in [our Discord server](https://discord.gg/tRkZFVy82u)!
