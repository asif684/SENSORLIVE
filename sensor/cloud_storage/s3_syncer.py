import os
import subprocess

class S3Sync:

    def sync_folder_to_s3(self, folder, aws_bucket_url):
        if not os.path.exists(folder):
            raise Exception(f"Folder {folder} does not exist")
        command = ["aws", "s3", "sync", folder, aws_bucket_url]
        subprocess.run(command, check=True)

    def sync_folder_from_s3(self, folder, aws_bucket_url):
        if not os.path.exists(folder):
            os.makedirs(folder)
        command = ["aws", "s3", "sync", aws_bucket_url, folder]
        subprocess.run(command, check=True)
