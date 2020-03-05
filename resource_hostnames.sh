#!/bin/bash

available_regions=$(aws ec2 describe-regions | grep "RegionName" |tr -d "\" ")
available_regions=${available_regions//RegionName:/}
for region in ${available_regions}
do
    echo Region: ${region}
    echo rds db instances:
    aws rds describe-db-instances --region ${region} --query \
    'DBInstances[*].{DBInstance:DBInstanceIdentifier,Network:Endpoint}'
    echo ec2 instances:
    aws ec2 describe-instances --region ${region} --query \
    'Reservations[*].Instances[*].{Instance:InstanceId,PrivateHostName:PrivateDnsName,PublicHostName:PublicDnsName}'
done
