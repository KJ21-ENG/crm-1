#!/usr/bin/env python3
"""
Generate PNG icons for the Chrome extension
Requires: pip install Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("Please install Pillow: pip install Pillow")
    exit(1)

def create_icon(size, filename):
    """Create a WhatsApp-style icon with the given size"""
    # Create a new image with a green background
    img = Image.new('RGBA', (size, size), (37, 211, 102, 255))  # WhatsApp green
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions for the phone icon
    phone_width = int(size * 0.6)
    phone_height = int(size * 0.8)
    phone_x = (size - phone_width) // 2
    phone_y = (size - phone_height) // 2
    
    # Draw phone body (rounded rectangle)
    phone_color = (255, 255, 255, 255)  # White
    
    # Draw phone body as a rectangle with rounded corners
    draw.rectangle([phone_x, phone_y, phone_x + phone_width, phone_y + phone_height], 
                   fill=phone_color, outline=phone_color)
    
    # Draw phone screen (slightly smaller)
    screen_margin = int(size * 0.05)
    screen_x = phone_x + screen_margin
    screen_y = phone_y + screen_margin
    screen_width = phone_width - 2 * screen_margin
    screen_height = phone_height - 2 * screen_margin
    
    draw.rectangle([screen_x, screen_y, screen_x + screen_width, screen_y + screen_height], 
                   fill=(240, 240, 240, 255), outline=(200, 200, 200, 255))
    
    # Draw WhatsApp dots
    dot_size = int(size * 0.08)
    dot_color = (37, 211, 102, 255)  # WhatsApp green
    
    # Position dots in the bottom right of the phone
    dot_x = phone_x + phone_width - int(size * 0.15)
    dot_y = phone_y + phone_height - int(size * 0.15)
    
    draw.ellipse([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], fill=dot_color)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Generate all required icon sizes"""
    icons_dir = "icons"
    
    # Create icons directory if it doesn't exist
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    # Generate icons for different sizes
    icon_sizes = [
        (16, "icon16.png"),
        (48, "icon48.png"),
        (128, "icon128.png")
    ]
    
    for size, filename in icon_sizes:
        filepath = os.path.join(icons_dir, filename)
        create_icon(size, filepath)
    
    print("\n✅ All icons generated successfully!")
    print("📁 Icons saved in: icons/")

if __name__ == "__main__":
    main() 