
## AWS S3 Sdk & Lambda
This is a code for the amazon s3 bucket integration with aws sdk as boto3 & lambda code for the conversion between images from normal image to laptop, mobile and tablet versions.

### Files & Folders
| File/Folder | Description                |
| :-------- | :------------------------- |
| `.gitignore` | `files to be ignored on commit` |
| `pillow_layer` | `contains zip which is to be attached to the lambda as a layer` |
| `services` | `aws sdk boto3 integration services` |
| `app.py` | `main scipt of the sdk project` |
| `requirements.txt` | `requirements of python for the sdk project` |
| `lambda.py` | `lambda script for the conversions` |
| `images` | `converted images in 3 formats` |
| `image-script-local.py` | `testing code of python for the conversions` |
| `photo.jpg` | `testing photo for the conversions` |

### How to run project
1. Create a file .env for the sdk project which store the access keys

    ACCESS_KEY="XXXX"

    SECRET_ACCESS_KEY="xxxx"

2. pip install -r requirements.txt 
3. streamlit run app.py (for the sdk project)
4. python image-script-local.py (to test the image conversion scipt)
 

### How to configure aws
#### 1. AWS Sdk Project
    i. create s3 bucket
    
    ii. change the code accordingly
    
    iii. host it on aws ec2 instance (optional as you can run on local also)


#### 2. AWS Lambda Image Conversion Project
    i. create 2 bucket in s3
    
    ii. configure code
    
    iii. create a lambda script for the code (having trigger as the s3 bucket & layer for the dependencies)
    
    iv. upload image on s3 and it'll store that to another bucket
