# Gazoo <!-- omit in toc -->

Wrap Minecraft Bedrock server to make proper backups.

- [Rationale](#rationale)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Similar projects](#similar-projects)


## Rationale

The Minecraft Bedrock server expects input from STDIN in order to perfrom
backups properly.  Since no other form of IPC exists, a wrapper is used to
automate sending the save commands to the Bedrock server's STDIN.  The wrapper
also forwards all STDIO transparently, so the wrapper acts as a drop-in
replacement.


## Installation

Gazoo is [published][pypi-gazoo] to the [Python Package Index (PyPI)][pypi-home]
and can be installed with [pip][pip-home].

```bash
pip install gazoo
```


## Configuration

Gazoo writes all its files to a `gazoo` subdirectory in the current working
directory.  Running `gazoo` for the first time will create a `gazoo.cfg` file in
the `gazoo` subdirectory, among other setup.  The configuration file is a simple
[INI-style][wikipedia-ini] file with only a few options:

- `backup_interval`
  - Time between backups (in seconds)
  - Default value: `600` (10 minutes)
- `cleanup_interval`
  - Time between cleanups (in seconds)
  - Default value: `86400` (24 hours)
- `debug`
  - Whether to output debug information
  - Default value: `false`


## Usage

Please note:  `gazoo` requires being run in the context of the Bedrock server
root directory.  This means you will need to `cd` to the Bedrock server root
directory before calling `gazoo`, or set `PWD`, or something else appropriate
for your situation.

By default (without any additional arguments), `gazoo` wraps the Bedrock server
transparently (with all STDIO forwarded).  Saving and cleanup is performed
automatically as configured in the `gazoo.cfg` file.

For convenience, two commands are also provided:  `cleanup`, and `restore`.

The `cleanup` command simply runs the cleanup portion of the program and then
exits.  This is useful if there are backups that need to be cleaned up, but you
don't want to start the Bedrock server.

The `restore` command restores saves made by gazoo.  If used without any
additional arguments, `restore` restores the most recent save.  An integer
argument can be provided to restore the nth most recent save.  E.g. passing `1`
restores the first most recent save (and is equivalent to passing nothing),
passing `2` restores the second most recent save, etc.  Alternatively, a file
path to a backup can be specified.


## Similar projects

[github.com/debkbanerji/minecraft-bedrock-server][github-debkbanerji-minecraft-bedrock-server]
may provide some similar functionality (untested/unvetted).


<!-- Links -->

[github-debkbanerji-minecraft-bedrock-server]:
https://github.com/debkbanerji/minecraft-bedrock-server
"GitHub - debkbanerji/minecraft-bedrock-server"

[pip-home]:
https://pip.pypa.io/en/stable/
"Home - pip documentation"


[pypi-home]:
https://pypi.org/
"PyPI - The Python Package Index"

[pypi-gazoo]:
https://pypi.org/project/gazoo/
"gazoo - PyPI"


[wikipedia-ini]:
https://en.wikipedia.org/wiki/INI_file
"INI file - Wikipedia"
