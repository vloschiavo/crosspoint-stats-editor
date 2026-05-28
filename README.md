# CrossInk Global Stats Editor

A command-line tool to view and edit the `global_stats.bin` file used by **CrossInk** (and CrossPoint) e-reader software.

---

## Features

- View current global reading statistics
- Set absolute values for any stat
- **Increment** existing values (`--add-*` options)
- **Reset all stats** to zero with one flag
- Automatic backup creation (`global_stats.bin.bak`)
- Supports version 1 and 2 of the file format

edit-stats.py       =   interactive stats editor
edit-stats-cli.py   =   stats editor with command line options
decode-stats.py     =   read-only stats viewer
.crosspoint/sample-blank-global_stats.bin   = sample blank file

---

## Usage

### Basic Commands

```bash
# View current stats
python edit-stats-cli.py --view

# Reset everything to zero
python edit-stats-cli.py --reset

# Set absolute values
python edit-stats-cli.py --sessions 2500 --seconds 720000 --completed 95

# Increment existing stats
python edit-stats-cli.py --add-sessions 100 --add-seconds 3600 --add-pages 500

# Mix set and add (set first, then add)
python edit-stats-cli.py -s 1000 --add-seconds 7200

# All Options

| Option | Short | Description |
| --- | --- | --- |
| `--file` | `-f` | Path to `global_stats.bin` |
| `--sessions` | `-s` | Set total sessions |
| `--seconds` | `-t` | Set total reading time (seconds) |
| `--pages` | `-p` | Set total pages turned |
| `--completed` | `-c` | Set completed books |
| `--add-sessions` | —   | Add to total sessions |
| `--add-seconds` | —   | Add to total reading time |
| `--add-pages` | —   | Add to total pages turned |
| `--add-completed` | —   | Add to completed books |
| `--reset` | —   | Reset **all** stats to 0 |
| `--view` | `-v` | View only (no changes) |

# Examples

# Add 50 hours of reading time
python edit-stats-cli.py --add-seconds $((50*3600))

# Big boost
python edit-stats-cli.py --add-sessions 800 --add-pages 15000 --add-completed 30

# Reset then set new values
python edit-stats-cli.py --reset --sessions 500 --seconds 180000

Important: Always safely eject your sd-card after editing and restart the device.
