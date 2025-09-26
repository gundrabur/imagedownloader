#!/bin/bash

echo "📱 Media Downloader - macOS App Builder"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Building native macOS app...${NC}"

# Create app structure
APP_NAME="Media Downloader.app"
APP_DIR="$APP_NAME/Contents"
MACOS_DIR="$APP_DIR/MacOS"
RESOURCES_DIR="$APP_DIR/Resources"

echo -e "${YELLOW}Creating app bundle structure...${NC}"
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy executables
echo -e "${YELLOW}Copying executables...${NC}"
if [ -f "dist/MediaDownloader" ]; then
    cp "dist/MediaDownloader" "$MACOS_DIR/"
    chmod +x "$MACOS_DIR/MediaDownloader"
    echo -e "${GREEN}✓ Console executable copied${NC}"
else
    echo -e "${RED}✗ Console executable not found. Run 'pyinstaller --onefile imagedownloader.py' first${NC}"
fi

if [ -f "simple_gui.py" ]; then
    cp "simple_gui.py" "$MACOS_DIR/"
    echo -e "${GREEN}✓ GUI script copied${NC}"
else
    echo -e "${RED}✗ GUI script not found${NC}"
fi

# Set permissions
echo -e "${YELLOW}Setting permissions...${NC}"
chmod +x "$MACOS_DIR/MediaDownloaderGUI" 2>/dev/null || true
chmod +x "$MACOS_DIR/MediaDownloader" 2>/dev/null || true

# Create a deployment package
echo -e "${YELLOW}Creating deployment package...${NC}"
if [ -d "$APP_NAME" ]; then
    echo -e "${GREEN}✓ App bundle created successfully${NC}"
    echo -e "${BLUE}App location: $(pwd)/$APP_NAME${NC}"
    
    # Show app contents
    echo -e "${YELLOW}App contents:${NC}"
    find "$APP_NAME" -type f | while read file; do
        echo "  📄 ${file#$APP_NAME/}"
    done
    
    # Copy to Desktop for easy access
    if [ -d "$HOME/Desktop" ]; then
        cp -r "$APP_NAME" "$HOME/Desktop/"
        echo -e "${GREEN}✓ App copied to Desktop${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 BUILD SUCCESSFUL!${NC}"
    echo -e "${BLUE}To install:${NC}"
    echo "  1. Drag 'Media Downloader.app' to your Applications folder"
    echo "  2. Double-click to run (may need to allow in Security & Privacy)"
    echo ""
    echo -e "${BLUE}To run from Finder:${NC}"
    echo "  • Double-click the app icon"
    echo "  • Enter a website URL when prompted"
    echo "  • Files will be downloaded to your Downloads folder"
    
else
    echo -e "${RED}✗ Failed to create app bundle${NC}"
    exit 1
fi