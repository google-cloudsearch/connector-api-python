# Google Cloud Search Connector API - Python Example 
[Google Cloud Search](https://developers.google.com/cloud-search/docs/guides/) allows users to search and retrieve information from a data repository. To handle items in Google Cloudsearch, you can create custom connector using the Google Cloudsearch SDK or API.

In this repository you can find an example of a working custom connector written in Python using the Cloudsearch API. This connector is not an offcial and supported connector, it wants to show the steps and the order of queries you need to implement to be able create your own custom connector. 

In this example, files will be store in a GCS bucket with the following structure:
```
bucket
  |--> Folder A
  |     |---> file_1.pdf
  |     |---> file_2.pdf        
  |--> Folder B
  |     |---> file_3.pdf
  |     |---> file_4.pdf        
```
Folder name will be saved as metadata proprty in the Schema.

## Prerequisites
* gSuite Domain whitelisted for CloudSearch
* Google Cloudsearch API enabled ([link](https://developers.google.com/cloud-search/docs/guides/project-setup))
* configured a custom Datasource in CloudSearch ([link](https://support.google.com/a/answer/7056471?hl=en))
* Project sotring files to be indexed in GCS. Files are expected to be within a folder structured as mentioned above
* Service Account configured in the project with access to the project.

# Configure virtualenv
We suggest you to use Python Virtualenv to run the following script (Installation guide [link](https://virtualenv.pypa.io/en/latest/installation/)). Create a dedicated Virtualend with the following commands:
```
$ virtualenv -p python3 env
$ . env/bin/activate
```

Install all packages in the [REQUIREMENTS.txt](REQUIREMENTS.txt) file. You can use the following command:
```
(env) $ pip install -r REQUIREMENTS.txt
```

Once concluded, to deactivate and exit from the virtualenv, use the following command:
```
$ deactivate
```

## Schemas operations
For a given Google Cloudsearch datasource, you can specify a schema. To handle the schema in your datasource you can use the following API:
- [updateSchema](https://developers.google.com/cloud-search/docs/reference/rest/v1/indexing.datasources/updateSchema)
- [deleteSchema](https://developers.google.com/cloud-search/docs/reference/rest/v1/indexing.datasources/deleteSchema)
- [getSchema](https://developers.google.com/cloud-search/docs/reference/rest/v1/indexing.datasources/getSchema)

Once you have specified the schema structure of the item you want to index in the ```schema.json``` file you can:
- Create or update the schema with the following command:
```
(env) $ python schema_create_or_update.py \
  --service_account_file service.json \
  --datasources YOUR_DATASOURCE_ID \
  --schema_json schema.json 
```
- delete the schema with the following command:
```
(env) $ python schema_delete.py \
  --service_account_file service.json \
  --datasources YOUR_DATASOURCE_ID 
```

## Items operations
For a given Google Cloudsearch datasource and schema, you can handle items you want to index with the following api:
- [item.Index](https://developers.google.com/cloud-search/docs/reference/rest/v1/indexing.datasources.items/index)
- [item.list](https://developers.google.com/cloud-search/docs/reference/rest/v1/indexing.datasources.items/list)
- [item.delete](https://developers.google.com/cloud-search/docs/reference/rest/v1/indexing.datasources.items/delete)

If you are in the case to index content larger than 100KiB this is the full set of API you have to call:
- [items.upload](https://developers.google.com/cloud-search/docs/reference/rest/v1/indexing.datasources.items/upload)
- [media.upload](https://developers.google.com/cloud-search/docs/reference/rest/v1/media/upload)
- [item.Index](https://developers.google.com/cloud-search/docs/reference/rest/v1/indexing.datasources.items/index)

Once you have specified the item basic structure of the item you want to index in the ```item.json``` file you can:
- Insert Items present in the GCS bucket with the following command:
```
(env) $ python item_create.py  \
  --service_account_file service.json \
  --datasources YOUR_DATASOURCE_ID \
  --item_json item.json \
  --document_bucket GCS_BUCKET_NAME
  ```
- list Items present in the datasource with the following command:
```
(env) $ python item_list.py \
  --service_account_file service.json \
  --datasources YOUR_DATASOURCE_ID
```
- delete all Items present in the datasource with the following command:
```
(env) $ python item_delete.py \
  --service_account_file service.json \
  --datasources YOUR_DATASOURCE_ID 
```

## Create a custom search application
Now that you have a Google Cloud datasource populated with your documents, you can create a custom search application following the procedure described [here](https://developers.google.com/cloud-search/docs/tutorials/end-to-end/setup-app#creating_the_search_application_credentials).
