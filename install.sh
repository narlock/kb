#!/bin/bash

# =================================
# KANBAN INSTALLATION SCRIPT
# author: narlock
#
# 1. Installs the contents of the application into $HOME/Documents/narlock/kb
# 2. Ensures that the main.py file is executable
# 3. Creates a wrapper to ensure that the 'kb' command runs with python3
# 4. Ensures the wrapper is executable
# =================================

# Define install paths
INSTALL_DIR="$HOME/Documents/narlock/kb"
SCRIPT_PATH="$INSTALL_DIR/kb/main.py"
BIN_PATH="/usr/local/bin/kb"

echo "Installing kb..."

# Create the install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Copy all files to the install directory
cp -r . "$INSTALL_DIR"

# Make sure the script is executable
chmod +x "$SCRIPT_PATH"

# Create a wrapper script to ensure 'mark' runs with python3
echo "#!/bin/bash" | sudo tee "$BIN_PATH" > /dev/null
echo "python3 \"$SCRIPT_PATH\" \"\$@\"" | sudo tee -a "$BIN_PATH" > /dev/null

# Make the wrapper script executable
sudo chmod +x "$BIN_PATH"

echo "🚀 Installation complete! Use 'kb' to begin."
