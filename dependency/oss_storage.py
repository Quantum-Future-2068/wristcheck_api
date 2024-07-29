from datetime import datetime

import oss2
import requests


class OSSManager:
    def __init__(
        self, access_key_id, access_key_secret, endpoint, bucket_name, subdirectory=None
    ):
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)
        self.subdirectory = subdirectory

    def stream_upload_avatar_from_url(self, filename, url):
        """
        Streams the upload of a user's avatar from a remote URL to the OSS bucket,
        using a timestamp as a version identifier.

        :param filename: The ID of the user whose avatar is being uploaded.
        :param url: The URL of the avatar image.
        """
        image_suffix = "jpg"
        version_identifier = str(datetime.now().timestamp()).replace(".", "")[-6:]
        object_key = (
            f"{self.subdirectory}/{filename}_{version_identifier}.{image_suffix}"
        )

        # Define a generator that streams the content from the URL
        def stream_generator():
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            for chunk in response.iter_content(chunk_size=8192):
                yield chunk

        # Upload the image to OSS using the stream generator
        self.bucket.put_object(object_key, stream_generator())
        return dict(
            url=self.bucket.sign_url("GET", object_key, 60),
            bucket=self.bucket.bucket_name,
            subdirectory=self.subdirectory,
            filename=filename,
            version_identifier=version_identifier,
            image_suffix=image_suffix,
            object_key=object_key,
        )
