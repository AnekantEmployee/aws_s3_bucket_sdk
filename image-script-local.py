from PIL import Image
from pathlib import Path

# Device viewport dimensions (width x height)
DEVICE_VIEWPORTS = {
    'laptop': (1920, 1080),    # Standard laptop/desktop
    'tablet': (1024, 768),     # Standard tablet (landscape)
    'mobile': (375, 667),      # Standard mobile (portrait)
}

def resize_image_smart(image, target_size, maintain_aspect=True):
    """
    Resize image intelligently based on target size
    """
    if maintain_aspect:
        # Calculate the ratio to fit the image within target dimensions
        img_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            # Image is wider than target ratio
            new_width = target_size[0]
            new_height = int(target_size[0] / img_ratio)
        else:
            # Image is taller than target ratio
            new_height = target_size[1]
            new_width = int(target_size[1] * img_ratio)
            
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a new image with target size and paste resized image centered
        final_image = Image.new('RGB', target_size, (255, 255, 255))
        paste_x = (target_size[0] - new_width) // 2
        paste_y = (target_size[1] - new_height) // 2
        final_image.paste(resized, (paste_x, paste_y))
        
        return final_image
    else:
        # Stretch to fit exactly
        return image.resize(target_size, Image.Resampling.LANCZOS)

def convert_image_to_devices(input_path, output_dir):
    """
    Convert an image to different device viewport sizes
    
    Args:
        input_path: Path to input image
        output_dir: Output directory
        quality: JPEG quality (1-100)
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Load image
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            print(f"Processing image: {input_path.name}")
            print(f"Original size: {img.width}x{img.height}")
            
            # Process each device
            for device, target_size in DEVICE_VIEWPORTS.items():
                print(f"\nConverting for {device}: {target_size[0]}x{target_size[1]}")
                
                # Apply conversion method (always using smart resize)
                converted_img = resize_image_smart(img, target_size, maintain_aspect=True)
                
                # Save image
                output_filename = f"{input_path.stem}_{device}.jpg"
                output_path = output_dir / output_filename
                
                converted_img.save(
                    output_path, 
                    'JPEG', 
                    quality=100, 
                    optimize=True
                )
                
                print(f"Saved: {output_path}")
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return False
    
    return True

# Hardcoded paths - change these to your needs
input_image = "photo.jpg" # Path to your input image
output_directory = "images" # Output directory

# Convert the image
convert_image_to_devices(input_image, output_directory)

print("\nConversion completed!")