# Copyright 2020 Google Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""In this package you have 1 classes:
 - ItemBody: to handle dictionary options. You can use this class 
  to prepare body objects for Cloud Search APIs.
 - CloudStorage: to handle simple operation on Google Cloud Storage Bucket
"""

import googleapiclient.http
import os


class CloudStorage(object):
  def __init__(self, service, bucket):

    self.service = service
    self.bucket = bucket

  def list_blob_file(self):
    # Create a request to objects.list to retrieve a list of objects.
    req = self.service.objects().list(bucket=self.bucket)
    all_objects = []
    while req:
      resp = req.execute()
      items = resp.get('items', [])
      for item in items:
        all_objects.extend([item])
      req = self.service.objects().list_next(req, resp)
    return all_objects

  def download_blob_file(self, blob_item):
    file_name = os.path.basename(blob_item["name"])
    with open('%s' % file_name, "wb") as f:
      req = self.service.objects().get_media(
          bucket=blob_item.get('bucket'), object=blob_item["name"])

      downloader = googleapiclient.http.MediaIoBaseDownload(f, req)

      done = False
      while done is False:
        status, done = downloader.next_chunk()
    return
