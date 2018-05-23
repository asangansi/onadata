# Bulk data upload.

Allow bulk upload of data.

1. CSV upload to an existing blank form form (already supported)
2. Excel upload to an existing blank form (not supported)
3. Allow multiple uploads of data to an existing form that may already include data.

Example XLSForm:

    | survey  |
    |         | type              | name    | label      |
    |         | text              | a_name  | Your Name? |
    |         | begin group       | fruits  | Fruits     |
    |         | select one fruits | fruit   | Fruit      |
    |         | end group         |         |            |
    |         |                   |         |            |
    | choices | list name         | name    | label      |
    |         | fruits            | mango   | Mango      |
    |         | fruits            | orange  | Orange     |
    |         | fruits            | apple   | Apple      |

## Excel bulk data upload to an existing form

A user should be able to upload an Excel `.xls/.xlsx` file to an existing form. The data in the file is added as submissions to the existing form. The excel file should have:

1. The first row, the column header row, MUST HAVE the name that matches to a question name in the XLSForm/XForm form. Any column name that does not match a question in the form will be ignored and hence not imported.
2. The column header names MAY HAVE group or repeat name separators, if there are no separators it will be ASSUMED that the field name match be it within a group or a repeat is what is meant. For example:

    | a_name | fruits/fruit |
    | Alice  | mango        |
    | Bob    | orange       |

Without the group name will also match perfectly to the above form.

    | a_name | fruit  |
    | Alice  | mango  |
    | Bob    | orange |

3. There MUST NOT be a duplicately named column in the form or in in the data upload file. Imports will be REJECTED if there are duplicates.
4. The file MAY HAVE a `meta/instanceID` column which should uniquely identify a specific record. If present, the `meta/instanceID` will be used to identify whether the record is new or is an edit of existing records. If it does not exist, the system will create a new one for each new record added.

Questions:
1. What happens if an upload file has repeats?
2. Which Excel sheet should have the data imported?
3. Should an Excel template file be provided?

### Data upload expected behaviour

When an upload is done, three things could happen to the data.

1. The upload will add new records to the existing form.
2. The upload will edit existing records where there is a matching meta/instancID and add new records if the existing meta/instanceID is either blank or missing or does not exist.
3. The upload will overwrite existing records.

Note:

- For ANY approach, a caution/warning and a clear explanation of expected behaviour should be presented to the user on the UI.
- A the orignal data submitter information will be lost in te case of an overwrite.
- No effort will be made to link an exported file from Ona with the original submitter of the data.

#### 1. The upload will add new records to the existing form.

A data upload will add new recrds to the existing form under the following circumstances:

1. The form has NO submissions.
2. The upload file DOES NOT have the `meta/instanceID` column. (Should the user be allowed to specify a unique column?)

#### 2. The upload will edit existing records

A data upload will edit existing records in an existing form only if the upload file CONTAINS the column `meta/instanceID` and the value in this column MATCHES an existing record in the form.

Note: If themeta/instanceID is EITHER BLANK or MISSING or DOES NOT EXIST, a NEW record will be added to the form.

#### 3. The upload will OVERWRITE existing record

A data will OVERWRITE existing records if the parameter `overwrite` is `true`, `overwrite=true`, as part of the upload request. All existing records will be PARMANENTLY DELETED and the NEW data upload will become the new submissions in the form.

Questions:
- Should it be possible to REVERT this process? NO


## API implementation

Implement a `/api/v1/data/[pk]/import` or endpoint on the API.

### `POST` /data/[pk]/import

The endpoint will accept `POST` requests to upload the data CSV/Excel file.

- The uploaded file will be persisted in the database and file storage. I propose we use the `MetaData` model to keep this record, we may need to use a new key e.g `data-imports` to refer to this files. New models could be used to achieve the same effect if there is more information to be stored.
- An asynchronous task will be created to start the process of importing the records from the file.

Request:

    POST /data/[pk]/import

    {
        "upload_file": ...,  // the file to upload
        "overwrite": false, // whether to overwrite or not, accepts true or false.
        ...
    }

Response:

    Response status code 201

    {
        "xform": [xform pk],
        "upload_id": [unique record identify for the upload]
        "filename": [filename of uploaded file]
    }

#### Processing the Uploaded file.

Depending on the query parameters, the data import will be taking into account the 3 options available as described above, i.e, NEW or EDIT or OVERWRITE.

- A record of the number of records processed, successful and failed should be maintained.
- In the event of a SUCCESS or a FAILURE, a notification SHOULD be sent. The notification can be via EMAIL to the user uploading the data or to via MQTT messaging/notifications or BOTH.

## Questions

1. What happens if an upload file has repeats?
2. Which Excel sheet should have the data imported?
3. Should an Excel template file be provided?
4. Should it be possible to REVERT this process? NO
5. How should we notify the user on upload status/progress?
6. What limits should we impose on data file uploads? in megabytes or number rows?
7. Is the process supposed to be atomic - i.e all uploads go through or partial uploads will do.
8. Should data imports from exports link the submitted by user?
9. Should media links be downloaded into the new submission? Only data will be imported, media attachments will not be imported.
