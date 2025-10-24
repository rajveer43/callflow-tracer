# Creating the Extension Icon

You need to create a 128x128 PNG icon at `images/icon.png`.

## Option 1: Use an online tool
1. Go to https://www.canva.com or https://www.figma.com
2. Create a 128x128 canvas
3. Design a simple icon representing call flow (e.g., connected nodes/circles)
4. Use colors: Blue (#007ACC) and white
5. Export as PNG to `images/icon.png`

## Option 2: Use Python to generate a simple icon
Run this script in the vscode-extension directory:

```python
from PIL import Image, ImageDraw

# Create a 128x128 image
img = Image.new('RGB', (128, 128), color='#007ACC')
draw = ImageDraw.Draw(img)

# Draw simple call flow representation
# Draw circles (nodes)
draw.ellipse([32, 16, 48, 32], fill='white')
draw.ellipse([16, 56, 32, 72], fill='white')
draw.ellipse([80, 56, 96, 72], fill='white')
draw.ellipse([48, 96, 64, 112], fill='white')

# Draw lines (connections)
draw.line([(40, 32), (24, 56)], fill='white', width=3)
draw.line([(40, 32), (88, 56)], fill='white', width=3)
draw.line([(24, 72), (56, 96)], fill='white', width=3)
draw.line([(88, 72), (56, 96)], fill='white', width=3)

img.save('images/icon.png')
print("Icon created at images/icon.png")
```

## Option 3: Temporarily remove icon from package.json
Remove the `"icon": "images/icon.png",` line from package.json for now.
