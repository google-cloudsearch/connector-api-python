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

"""In this package you have 2 classes:
 - ItemBody: Simple class to handle dictionary options. You can use this class 
  to prepare body objects for Cloud Search APIs.
 - ItemsService: Simple to handle Cloud Search APIs.
"""

import os
import copy
import json


class ItemBody(object):
  def __init__(self, body=None):
    self._body = body or {}

  def set_element(self, path, value):
    if isinstance(value, bytes):
      value = value.decode('utf-8')
    el = self._body
    tokens = path.split('/')
    for k in tokens[:-1]:
      el = el.setdefault(k, {})
    el[tokens[-1]] = value

  def get_element(self, path):
    el = self._body
    tokens = path.split('/')
    for k in tokens:
      el = el.setdefault(k, {})
    return el

  @property
  def as_string(self):
    try:
      return json.dumps(self._body)
    except TypeError:
      print(repr(self._body))
      raise


  @property
  def body(self):
    return self._body


class ItemsService(object):
  def __init__(self, service, datasources, tmp_path=None):
    self.service = service
    self.datasources = datasources
    self._tmp_path = tmp_path or 'tmp'

  @property
  def tmp_path(self):
    return self._tmp_path

  def _get_datasource_name(self):
    return "datasources/%s" % (self.datasources)

  def _get_item_name(self, item_id):
    return "datasources/%s/items/%s" % (self.datasources, item_id)

  def delete(self, item_id, version, mode='SYNCHRONOUS'):
    return self.service.indexing().datasources().items().delete(
        name=item_id,
        version=version,
        mode=mode).execute()

  def insert(self, item_id, item_body):
    return self.service.indexing().datasources().items().index(
        name=self._get_item_name(item_id),
        body=item_body).execute()

  def insert_with_media(self, item_id, item_body, media_file_path):
    session = self.service.indexing().datasources().items().upload(
        name='%s:upload' % self._get_item_name(item_id), body={}).execute()
    try:
      upload = self.service.media().upload(media_body=media_file_path,
                                           resourceName=session.get('name'),
                                           body={'resourceName': media_file_path}).execute()
    except Exception as e:
      upload = session

    item_body.set_element('item/content/contentDataRef', upload)
    item_body.set_element('item/content/contentFormat', "RAW")
    return self.service.indexing().datasources().items().index(
        name=self._get_item_name(item_id),
        body=item_body.body).execute()

  def get(self, item_id):
    return self.service.indexing().datasources().items().get(
        name=self._get_item_name(item_id)).execute()

  def push(self, item_id, body):
    return self.service.indexing().datasources().items().push(
        name=self._get_item_name(item_id),
        body=body).execute()

  def list(self):
    results = self.service.indexing().datasources().items().list(
        name=self._get_datasource_name(),
        brief=False,
        pageSize=10).execute()

    output = []
    while results:
      for result in results.get('items'):
        output.append(result)
      if results.get('nextPageToken'):
        results = self.service.indexing().datasources().items().list(
            name=self._get_datasource_name(),
            pageToken=results.get('nextPageToken'),
            brief=True,
            pageSize=10).execute()
      else:
        results = False
    return output
