#!/usr/bin/env python3
"""Create a simple icon for the VS Code extension."""

try:
    from PIL import Image, ImageDraw
    
    # Create a 128x128 image with blue background
    img = Image.new('RGB', (128, 128), color='#007ACC')
    draw = ImageDraw.Draw(img)
    
    # Draw simple call flow representation (nodes and connections)
    # Top node
    draw.ellipse([56, 16, 72, 32], fill='white', outline='white')
    
    # Middle left node
    draw.ellipse([24, 48, 40, 64], fill='white', outline='white')
    
    # Middle right node
    draw.ellipse([88, 48, 104, 64], fill='white', outline='white')
    
    # Bottom node
    draw.ellipse([56, 80, 72, 96], fill='white', outline='white')
    
    # Draw connections (lines)
    draw.line([(64, 32), (32, 48)], fill='white', width=3)
    draw.line([(64, 32), (96, 48)], fill='white', width=3)
    draw.line([(32, 64), (64, 80)], fill='white', width=3)
    draw.line([(96, 64), (64, 80)], fill='white', width=3)
    
    # Save the icon
    img.save('images/icon.png')
    print('✓ Icon created successfully at images/icon.png')
    
except ImportError:
    print('ERROR: Pillow is not installed.')
    print('Please run: pip install Pillow')
    print('Then run this script again: python create_icon.py')
    exit(1)
