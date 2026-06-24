---
sidebar_position: 3
---

# Command-Line Arguments


## Usage
```
peakrdl halcpp [-h] [-I INCDIR] [-t TOP] [--rename INST_NAME]
                    [-P PARAMETER=VALUE] -o OUTPUT [--ext [EXT [EXT ...]]]
                    [--list-files] [--skip-buses] [-f FILE] [--peakrdl-cfg CFG]
                    FILE [FILE ...]
```

## Arguments

|            Argument             |   Type   |Nargs|        Group        |
|---------------------------------|----------|-----|---------------------|
|[`FILE`](#FILE)                  |Positional|+    |compilation args     |
|[`-h` `--help`](#_h___help)      |Option    |    0|optional arguments   |
|[`-I`](#_I)                      |Option    |    1|compilation args     |
|[`-t` `--top`](#_t___top)        |Option    |    1|compilation args     |
|[`--rename`](#__rename)          |Option    |    1|compilation args     |
|[`-P`](#_P)                      |Option    |    1|compilation args     |
|[`--remap-state`](#__remap_state)|Option    |    1|ip-xact importer args|
|[`-o`](#_o)                      |Option    |    1|exporter args        |
|[`--ext`](#__ext)                |Option    |*    |exporter args        |
|[`--list-files`](#__list_files)  |Option    |    0|exporter args        |
|[`--skip-buses`](#__skip_buses)  |Option    |    0|exporter args        |

### `-h` `--help` {#_h___help}

show this help message and exit

### `FILE` {#FILE}

One or more input files

### `-I` {#_I}

Search directory for files included with `include "filename"

### `-t` `--top` {#_t___top}

Explicitly choose which addrmap  in the root namespace will be the top-level component. If unset, The last addrmap defined will be chosen

### `--rename` {#__rename}

Overrides the top-component's instantiated name. By default, the instantiated name is the same as the component's type name

### `-P` {#_P}

Specify value for a top-level SystemRDL parameter

### `--remap-state` {#__remap_state}

Optional remapState string that is used to select memoryRemap regions that are tagged under a specific remap state.

### `-o` {#_o}

Output path

### `--ext` {#__ext}

list of addrmap modules that have implemented {name}_EXT class in {name}_ext.h header file, used for extending functionality

### `--list-files` {#__list_files}

Don't generate files, but instead just list the files that will be generated, and external files that need to be included

### `--skip-buses` {#__skip_buses}

By default the SystemRDL hierarchy is preserved but it can be simplified by removing buses (i.e., addrmap containing only addrmaps, not registers). This is achieved by passing the --skip-buses flag.
