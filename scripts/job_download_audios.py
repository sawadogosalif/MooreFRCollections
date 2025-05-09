import os
import boto3
from loguru import logger
from pathlib import Path
from jwsoup.audio.scraper import download_audios
from dotenv import load_dotenv

load_dotenv()

# Configuration - download audios
start_url = "https://www.jw.org/mos/d-s%E1%BA%BDn-yiisi/biible/nwt/books/S%C9%A9ngre/1"
output_dir = "audio_files"
max_file_size = 2  # There are 1988 pages overall

logger.info("Downloading audios...")
download_audios(start_url, output_dir, max_file_size)
logger.info(f"Audio files downloaded to {output_dir}")

# Configuration - environnement S3
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
endpoint_url = os.getenv("AWS_ENDPOINT_URL_S3")

# Initialisation  S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
)

bucket_name = "moore-collection"
s3_prefix = "raw_data/"


def upload_folder_to_s3(folder_path, bucket_name, s3_prefix):
    files = list(Path(folder_path).rglob("*.mp3"))
    for file in files:
        local_path = file.as_posix()
        relative_path = os.path.relpath(local_path, folder_path)
        s3_key = os.path.join(s3_prefix, relative_path)
        s3_client.upload_file(local_path, bucket_name, s3_key)
        logger.info(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")


logger.info(f"Uploading folder {output_dir} to S3...")
upload_folder_to_s3(output_dir, bucket_name, s3_prefix)
logger.info("Upload complete!")
