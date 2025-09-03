import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from botocore.config import Config
import os

from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region_name = os.getenv("AWS_S3_REGION")
bucket_name = os.getenv("AWS_S3_BUCKET")


def upload_png_to_s3(file_path, object_name=None):
    """
    Upload a PNG file to an AWS S3 bucket.

    :param file_path: Path to the local PNG file
    :param bucket_name: S3 bucket name
    :param object_name: S3 object name. If not specified, file_path's basename is used
    :param aws_access_key_id: AWS access key ID (optional, uses default if not provided)
    :param aws_secret_access_key: AWS secret access key (optional, uses default if not provided)
    :param region_name: AWS region (optional)
    :return: True if file was uploaded, else False
    """

    if object_name is None:
        object_name = os.path.basename(file_path)

    print(f"S3 Upload - Bucket: {bucket_name}, Region: {region_name}", flush=True)

    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        s3_client = session.client(
            "s3", config=Config(connect_timeout=10, read_timeout=30)
        )
        with open(file_path, "rb") as f:
            print(f"Uploading file to S3: {file_path}", flush=True)
            s3_client.upload_fileobj(
                f,
                bucket_name,
                object_name + ".png",
                ExtraArgs={"ContentType": "image/png"},
            )
        # Return a public URL (bucket policy allows public read access)
        url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{object_name}.png"
        print(f"S3 upload successful: {url}", flush=True)
        return url
    except FileNotFoundError:
        print("The file was not found.")
        return False
    except NoCredentialsError:
        print("Credentials not available.")
        return False
    except ClientError as e:
        print(f"Client error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
