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

"""This script insert items in a Google Cloud Search datasource using 
the Cloud Search API.


Prerequisites:
 - Google Cloud Search enable on the gSuite organization
 - Created a Google Cloud Third-party data sources ID
 - GCP project
 - Google Cloud Search API enabled in the project
 - GCS bucket (Publicly readable)
 - GCP service account

To run this script, you will need Python3 packages listed in REQUIREMENTS.txt.

You can easily install them with virtualenv and pip by running these commands:
    virtualenv -p python3 env
    source ./env/bin/activate
    pip install -r REQUIREMENTS.txt

You can than run the script as follow:
    python item_create.py  \
    --service_account_file /PATH/TO/service.json \
    --datasources YOUR_DATASOURCE_ID \
    --item_json item.json \
    --document_bucket GCS_BUCKET_NAME
"""

import argparse
import base64
import cloudsearch
import google.oauth2.credentials
import googleapiclient.http
import json
import logging
import time
import urllib.parse

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from cloudstorage import *

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('cloudsearch.item')

# Scope grants [GCS]
GCS_SCOPES = ['https://www.googleapis.com/auth/devstorage.full_control']
GCS_API_SERVICE_NAME = 'storage'
GCS_API_VERSION = 'v1'

# Scope grants [CLOUD SEARCH]
SEARCH_SCOPES = ['https://www.googleapis.com/auth/cloud_search']
SEARCH_API_SERVICE_NAME = 'cloudsearch'
SEARCH_API_VERSION = 'v1'


def get_authenticated_service(service_account_file, scope, service_name, version):
  # Create credentials from Service Account File
  credentials = service_account.Credentials.from_service_account_file(
      service_account_file, scopes=scope)
  return build(service_name, version, credentials=credentials, cache_discovery=False)


def main(service_account_file, document_bucket,
         datasources, item_json):
  LOGGER.info('Indexing documents - START')
  service_gcs = get_authenticated_service(service_account_file,
                                          GCS_SCOPES,
                                          GCS_API_SERVICE_NAME,
                                          GCS_API_VERSION)

  service_search = get_authenticated_service(service_account_file,
                                             SEARCH_SCOPES,
                                             SEARCH_API_SERVICE_NAME,
                                             SEARCH_API_VERSION)

  itemService = cloudsearch.ItemsService(service_search, datasources)

  gcsService = CloudStorage(service_gcs, document_bucket)

  # Retrieve item body template
  with open(item_json) as f:
    item_body_template = json.load(f)

  LOGGER.info('Retrieve GCS blob files')
  blob_files = gcsService.list_blob_file()

  # Loop blob files
  for blob_file in blob_files:

    # Extrapolate file information
    file_folder = os.path.dirname(blob_file["name"])
    file_name = os.path.basename(blob_file["name"])

    # Skip folders items
    if file_name == '':
      continue
    LOGGER.info('Processing file: %s - START' % file_name)

    # Save the file locally
    gcsService.download_blob_file(blob_file)

    # Create item id, we can use the GCS item id,
    # Remove '/': it is not suppoerted.
    item_id = blob_file['id'].replace('/', '')

    # Retrieve item body template from the json file
    item_to_insert = cloudsearch.ItemBody(item_body_template)

    # Set fields specific to this item
    item_to_insert.set_element(
        'item/version', base64.b64encode(b'%d' % time.time()))
    item_to_insert.set_element(
        'item/metadata/title', file_name)
    item_to_insert.set_element('item/metadata/objectType', 'document')
    item_to_insert.set_element(
        'item/metadata/sourceRepositoryUrl', 'https://storage.googleapis.com/'+document_bucket+'/'+urllib.parse.quote(blob_file["name"]))
    item_to_insert.set_element('item/structuredData/object/properties', [
        {"name": "author",
         "textValues": {"values": file_folder}}
    ])

    # Insert document in tho the Cloud Search datasource
    itemService.insert_with_media(
        item_id, item_to_insert, file_name)

    # Remove the temporary local file
    os.remove('%s' % file_name)
    LOGGER.info('Processing file: %s - END' % file_name)

  LOGGER.info('Indexing documents - END')
  return


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      description='Example to parse HTML and send to CloudSearch.')
  parser.add_argument('--service_account_file', dest='service_account_file',
                      help='File name for the service account.')
  parser.add_argument('--datasources', dest='datasources',
                      help='DataSource to update.')
  parser.add_argument('--item_json', dest='item_json',
                      help='Item JSON structure.')
  parser.add_argument('--document_bucket', dest='document_bucket',
                      help='GCS document bucket.')

  args = parser.parse_args()

  main(args.service_account_file, args.document_bucket,
       args.datasources, args.item_json)
