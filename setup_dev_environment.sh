#!/bin/bash

# =============================================================================
# Media Downloader - Quick Setup Script
# =============================================================================
# Run this once to set up the development environment for building macOS apps
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📱 Media Downloader - Quick Setup${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "❌ This setup script is for macOS only"
    exit 1
fi

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "❌ Python 3 is required but not installed"
    echo -e "   Install from: https://www.python.org/downloads/"
    exit 1
fi

echo -e "${YELLOW}▶ Setting up development environment...${NC}"

# Create virtual environment
if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    echo -e "${GREEN}✅ Created virtual environment${NC}"
fi

# Activate and install dependencies
source .venv/bin/activate
pip install --upgrade pip pyinstaller

echo -e "${GREEN}✅ Installed build dependencies${NC}"

# Make compilation script executable
chmod +x compile_macos_app.sh

echo -e "${GREEN}✅ Made compilation script executable${NC}"

# Create .gitignore if it doesn't exist
if [[ ! -f ".gitignore" ]]; then
    cat > .gitignore << 'EOF'
# Build outputs
build/
dist/
*.spec
*.app
build_info.txt
AppIcon.iconset/

# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd

# macOS
.DS_Store
*.icns

# IDE
.vscode/
.idea/
EOF
    echo -e "${GREEN}✅ Created .gitignore${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Make changes to imagedownloader.py"
echo -e "  2. Run: ${YELLOW}./compile_macos_app.sh${NC}"
echo -e "  3. Test your app from Desktop"
echo ""
echo -e "${BLUE}Quick build:${NC}"
echo -e "  ${YELLOW}./compile_macos_app.sh${NC}"
echo ""

deactivate 2>/dev/null || true