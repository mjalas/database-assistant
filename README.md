# Database Assistant

_Very early development..._

This is CLI application consisting of utility commands to help with database related tasks.

Current focus is on DynamoDB related commands.

## Useful AWS commands

Export DynamoDB table data to CSV (remember to change table name):

```shell
aws dynamodb scan --table-name <my-table> --select ALL_ATTRIBUTES --page-size 500 --max-items 100000 --output json | jq -r '.Items' | jq -r '(.[0] | keys_unsorted) as $keys | $keys, map([.[ $keys[] ].S])[] | @csv' > export.<my-table>.csv

```
