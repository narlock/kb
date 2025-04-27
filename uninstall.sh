#!/bin/bash

# =================================
# KANBAN UNINSTALL SCRIPT
# author: narlock
#
# 1. Deletes the $HOME/Documents/narlock/kb directory
# 2. Removes the wrapper script from /usr/local/bin
# =================================

# Define install paths
INSTALL_DIR="$HOME/Documents/narlock/kb"
PARENT_DIR="$HOME/Documents/narlock"
BIN_PATH="/usr/local/bin/kb"

echo "Uninstalling kb..."

# Confirm uninstallation
read -p "Are you sure you want to uninstall kb? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Uninstallation cancelled."
    exit 1
fi

# Remove only the `kb` directory but leave `narlock` and `Documents` intact
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "✅ Removed $INSTALL_DIR"
else
    echo "⚠️ Installation directory not found. Skipping..."
fi

# Remove the wrapper script from /usr/local/bin
if [ -f "$BIN_PATH" ] || [ -L "$BIN_PATH" ]; then
    sudo rm "$BIN_PATH"
    echo "✅ Removed $BIN_PATH"
else
    echo "⚠️ No executable found at /usr/local/bin. Skipping..."
fi

echo "🚀 kb has been successfully uninstalled!"
