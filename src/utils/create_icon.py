from PIL import Image, ImageDraw
import os

def create_icon():
    # Create a 256x256 image with a transparent background
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle for the hand
    center = size // 2
    radius = size // 3
    draw.ellipse([center - radius, center - radius, center + radius, center + radius], 
                 fill=(52, 152, 219, 255))  # Blue color
    
    # Draw fingers
    finger_length = radius * 0.8
    finger_width = radius * 0.2
    
    # Index finger
    draw.rectangle([center + radius * 0.3, center - finger_length, 
                   center + radius * 0.3 + finger_width, center], 
                  fill=(255, 255, 255, 255))
    
    # Middle finger
    draw.rectangle([center, center - finger_length, 
                   center + finger_width, center], 
                  fill=(255, 255, 255, 255))
    
    # Ring finger
    draw.rectangle([center - radius * 0.3, center - finger_length, 
                   center - radius * 0.3 + finger_width, center], 
                  fill=(255, 255, 255, 255))
    
    # Pinky finger
    draw.rectangle([center - radius * 0.6, center - finger_length * 0.8, 
                   center - radius * 0.6 + finger_width, center], 
                  fill=(255, 255, 255, 255))
    
    # Thumb
    draw.rectangle([center + radius * 0.6, center - finger_length * 0.6, 
                   center + radius * 0.6 + finger_width, center], 
                  fill=(255, 255, 255, 255))
    
    # Save the icon
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    icon_path = os.path.join(assets_dir, 'icon.png')
    image.save(icon_path, 'PNG')
    print(f"Icon created successfully at {icon_path}")

if __name__ == '__main__':
    create_icon() 