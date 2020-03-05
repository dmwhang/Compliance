# Compliance
Two projects to help find non compliant resources in AWS
 
## open_sec_group_compliance.py

Generates 5 files that catalogue secuirty groups that are open to the internet 
and groups them based on when they were last used

in order to change which profiles and regions that should be looked at, 
edit lines 7 and 8 accordingly

```
python3 open_sec_group_compliance.py
```

## resource_hostnames.sh

Prints out the hostnames of the EC2 and RDS instances of all regions for whichever
AWS profile is currently set in the environment

```
./resource_hostnames.sh
```
