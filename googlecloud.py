import os
from google.cloud import storage

def remove_file():
    #path = "imgpool_reloaded"
    path = "imgpool"
    for file in os.listdir(path):
        os.remove(path + "/" + file)
def download_blob():
    bucket_name = "skdev-356007.appspot.com"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'skdev-356007-70b2ea60723d.json'
    storage_client = storage.Client()
    prefix="IMG/user_profile/"
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)

    for blob in blobs:
        x = blob.name
        #storage_client.bucket(bucket_name).blob(blob.name).download_to_filename(x.replace("IMG/user_profile/","imgpool_reloaded/"))
        storage_client.bucket(bucket_name).blob(blob.name).download_to_filename(x.replace("IMG/user_profile/", "imgpool/"))

remove_file()
download_blob()