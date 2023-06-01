# Data Importer

## Utility AWS commands

Export DynamoDB table data to CSV (remember to change table name):

```shell
aws dynamodb scan --table-name <my-table> --select ALL_ATTRIBUTES --page-size 500 --max-items 100000 --output json | jq -r '.Items' | jq -r '(.[0] | keys_unsorted) as $keys | $keys, map([.[ $keys[] ].S])[] | @csv' > export.<my-table>.csv

```
