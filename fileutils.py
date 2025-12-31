import time, uuid, boto3
from django.conf import settings

BUCKET_NAME = 'sl-templates'


def clean_path(path):
    return path.split('/')[-1]


def _client():
    """ returns s3 client """
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

def _resource():
    """ returns s3 resource """
    return boto3.resource(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

def get_file(template):
    """ gets file from s3 data store """
    obj = _client().get_object(
        Bucket=BUCKET_NAME,
        Key=clean_path(template.path)
    )
    file = obj.get('Body').read().decode('utf8')
    return file


def store_file(file, use_timestamp=True):
    """
    Stores a file on a given path. if use_time_stamp = True
    the current millisecond timestamp will be used as filename.
    returns: file path
    :param file: file from request
    :param use_timestamp: bool
    :return:
    """

    if use_timestamp:
        timestamp = round(time.time() * 1000)
        filename = '{}.html'.format(timestamp)
    else:
        filename = file.name

    return upload_to_s3(file, filename)


def copy_file(key):
    new_key = uuid.uuid4().hex.upper()[0:6]
    _resource().Object(
        BUCKET_NAME, new_key
    ).copy_from(CopySource='{}/{}'.format(BUCKET_NAME, key))
    return new_key


def upload_to_s3(target_file, filename):
    """ uploads file to amazon s3 and returns file key """
    key = clean_path(filename)
    delete(key)
    _client().put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=target_file.read()
    )
    return key


def upload_to_s3_raw(raw_data, filename):
    """ uploads file to amazon s3 and returns file key """
    key = clean_path(filename)
    delete(key)
    _client().put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=raw_data
    )
    return filename


def delete(filename):
    """ deletes files from s3 """
    key = clean_path(filename)
    _client().delete_object(
        Bucket=BUCKET_NAME,
        Key=key
    )
