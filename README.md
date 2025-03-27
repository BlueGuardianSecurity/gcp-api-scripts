# gcp-api-scripts

scripts for bulk actions using the google api
you will need to build a service account and authorize it to make changes within the domain

1. alias-import-to-google - this will be the bulk alias upload once the parsing and additions are complete
2. alias-parse - this will examine every group name and alias, check to see if the direct domain conversion alias exists, and it will append the new alias to a new column. for any attempt to create an existing alias name, it skips it and sends the group name to an external csv
3. this gets all group names within the workplace env

You will need to add file paths and include the JSON file in the working environment
