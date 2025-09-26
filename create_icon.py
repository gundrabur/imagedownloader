#!/usr/bin/env python3
"""
Create an icon for the Media Downloader app
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    # Create a 512x512 icon
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background gradient (blue to purple)
    for y in range(size):
        r = int(70 + (150 * y / size))
        g = int(130 + (50 * y / size))
        b = int(255 - (50 * y / size))
        color = (r, g, b, 255)
        draw.line([(0, y), (size, y)], fill=color)
    
    # Add rounded corners
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    corner_radius = size // 8
    mask_draw.rounded_rectangle([0, 0, size, size], corner_radius, fill=255)
    
    # Apply mask
    img.putalpha(mask)
    
    # Add download arrow symbol
    arrow_size = size // 3
    arrow_x = size // 2
    arrow_y = size // 2
    
    # Draw arrow shaft
    shaft_width = arrow_size // 6
    draw.rectangle([
        arrow_x - shaft_width, arrow_y - arrow_size//2,
        arrow_x + shaft_width, arrow_y + arrow_size//4
    ], fill=(255, 255, 255, 255))
    
    # Draw arrow head
    head_size = arrow_size // 3
    arrow_head = [
        (arrow_x, arrow_y + arrow_size//2),  # tip
        (arrow_x - head_size, arrow_y),      # left
        (arrow_x + head_size, arrow_y)       # right
    ]
    draw.polygon(arrow_head, fill=(255, 255, 255, 255))
    
    # Save as PNG
    img.save('app_icon.png', 'PNG')
    print("App icon created: app_icon.png")

if __name__ == "__main__":
    try:
        create_app_icon()
    except ImportError:
        print("PIL/Pillow not installed. Creating simple icon...")
        # Create a simple text-based icon instead
        with open('app_icon.icns', 'w') as f:
            f.write("# Simple icon placeholder")
        print("Created placeholder icon")