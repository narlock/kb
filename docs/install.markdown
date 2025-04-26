---
layout: page
title: Install Guide
permalink: /install/
---
<time>Apr 26, 2025</time>

Installing and using kb is relatively easy. However, version v1.0.0 only supports macOS and Linux computer systems.

1. Ensure that you have [Python](https://www.python.org/) installed on your computer system. You can check if you have Python installed by opening your terminal and typing `python3 --version`.
2. Download the latest release of kb from [https://github.com/narlock/kb/releases](https://github.com/narlock/kb/releases), this will be in a ZIP file.
3. Extract the ZIP file to a location on your computer. The ZIP file will contain the bash scripts for installing (`install.sh`) and uninstalling (`uninstall.sh`) the program. The "kb" directory contains the source code for the version of kb.
4. Allow executing the install script by opening the terminal in the directory that contains the install script and type: `chmod +x install.sh`.
5. Next, run the install script by entering `./install.sh`

After installing, we will see a message that reads "🚀 Installation complete! Use 'kb' to begin."

## What does the install script do?
The install script starts by making the directory to put all of the project's information. This includes the install script, uninstall script, and source code. The directory that will be made to support kb operations is located at `$HOME/Documents/narlock/kb`. Here you will find all of the code mentioned. When you run `kb` in your terminal, you will also see the `settings.json` file stored at this location.

The install script also creates a simple bash script to be ran when `kb` is typed into the terminal. The functionality is stored in `/usr/local/bin/kb` and will contain a wrapper that will execute the `python3` command to run the main file:

```sh
#!/bin/bash
python3 "/Users/narlock/Documents/narlock/kb/kb/main.py" "$@"
```

## I want to uninstall kb
If you choose not to want kb on your computer system anymore, you can simply uninstall it by running the `uninstall.sh` script. Give permission using `chmod +x uninstall.sh` similar to the install script, then run using `./uninstall.sh`.