import os
import boto3
from PIL import Image
from io import BytesIO
from pathlib import Path

# Device viewport dimensions (width x height)
DEVICE_VIEWPORTS = {
    'laptop': (1920, 1080),    # Standard laptop/desktop
    'tablet': (1024, 768),     # Standard tablet (landscape)
    'mobile': (375, 667),      # Standard mobile (portrait)
}

def resize_image_smart(image, target_size, maintain_aspect=True):
    """Resize image intelligently based on target size"""
    if maintain_aspect:
        img_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            new_width = target_size[0]
            new_height = int(target_size[0] / img_ratio)
        else:
            new_height = target_size[1]
            new_width = int(target_size[1] * img_ratio)
            
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        final_image = Image.new('RGB', target_size, (255, 255, 255))
        paste_x = (target_size[0] - new_width) // 2
        paste_y = (target_size[1] - new_height) // 2
        final_image.paste(resized, (paste_x, paste_y))
        
        return final_image
    else:
        return image.resize(target_size, Image.Resampling.LANCZOS)

def lambda_handler(event, context):
    # Initialize S3 client
    s3 = boto3.client('s3')
    
    # Extract source bucket and key from event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    
    # Destination configuration (modify as needed)
    dest_bucket = 'converted-images02'  # Change to your destination bucket
    dest_prefix = 'converted/'  # Optional prefix
    
    try:
        # Get the image from S3
        response = s3.get_object(Bucket=source_bucket, Key=source_key)
        image_content = response['Body'].read()
        
        # Process the image
        with Image.open(BytesIO(image_content)) as img:
            # Convert to RGB if necessary (Pillow operations typically need RGB)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Process each device size
            for device, target_size in DEVICE_VIEWPORTS.items():
                # Resize the image
                converted_img = resize_image_smart(img, target_size)
                
                # Save to in-memory file
                in_mem_file = BytesIO()
                converted_img.save(in_mem_file, format='JPEG', quality=85)
                in_mem_file.seek(0)
                
                # Create destination key
                original_stem = Path(source_key).stem
                dest_key = f"{dest_prefix}{original_stem}_{device}.jpg"
                
                # Upload to S3
                s3.put_object(
                    Bucket=dest_bucket,
                    Key=dest_key,
                    Body=in_mem_file,
                    ContentType='image/jpeg'
                )
                print(f"Saved {device} version to s3://{dest_bucket}/{dest_key}")
        
        return {
            'statusCode': 200,
            'body': f"Successfully processed {source_key} into 3 versions"
        }
    
    except Exception as e:
        print(f"Error processing {source_key}: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error processing {source_key}: {str(e)}"
        }