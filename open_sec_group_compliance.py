import boto3
import datetime
import os
import math

# Global variables
profiles = ['054288142014','143555422618','159592469094', '217386048230', '263734463344', '707965404768', '725071466363']
regions = ['us-east-1']
delta = datetime.timedelta(days=1)
counter = 1
output = []
days = 90
for months in range(5):
    output.append(dict())
for aws_profile in profiles:
    for profile_month in range(len(output)):
        output[profile_month][aws_profile] = dict()
    for aws_region in regions:
        for region_month in range(len(output)):
            output[region_month][aws_profile][aws_region] = dict()
        session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        ec2_client = session.client("ec2")  #, verify=False)]
        config_client = session.client("config")
        cloud_client = session.client('cloudtrail')
        sgs = ec2_client.describe_security_groups(Filters=[{'Name': 'ip-permission.cidr', 'Values': ['0.0.0.0/0']}])["SecurityGroups"]
        for group in sgs:
            print("Profile:", aws_profile, "Region:", aws_region, "Security Group:", group)
            counter += 1
            # port = "all"
            # if u"ToPort" in temp:
            #     port = temp[u"ToPort"]
            name = group["GroupName"]
            group_id = group["GroupId"]
            instances = ec2_client.describe_instances(Filters=[{'Name': 'instance.group-name', 'Values': [group["GroupName"]]}])['Reservations']
            end = datetime.datetime.now()
            start = end - delta
            curr_relations = ""
            owner = ""
            found_days = -1
            for day in range(days):
                if owner == "":
                    temp_event = cloud_client.lookup_events(
                        StartTime=start, EndTime=end,
                        LookupAttributes=[{'AttributeKey': 'ResourceName', 'AttributeValue': name},
                                          {'AttributeKey': 'ResourceType',
                                           'AttributeValue': "AWS::EC2::SecurityGroup"}])['Events']
                    if len(temp_event) > 0:
                        owner = temp_event[0]["Username"]
                        if found_days < 0:
                            found_days = day
                if found_days < 0:
                    temp_relations = config_client.get_resource_config_history(
                        laterTime=end, earlierTime=start,
                        resourceType="AWS::EC2::SecurityGroup",
                        resourceId=group_id)["configurationItems"]
                    if len(temp_relations) > 0 and str(curr_relations) != str(temp_relations):
                        for relation in temp_relations[0]["relationships"]:
                            if "associated" in relation["relationshipName"]:
                                found_days = day
                        curr_relations = temp_relations
                if not owner == "" and found_days >= 0:
                    break
                start -= delta
                end -= delta

            if found_days == -1:
                output[4][aws_profile][aws_region][group_id] = ">90, " + owner
                month = 4
            else:
                month = 0
                if found_days != 0:
                    month = math.floor(found_days / 30) + 1
                output[month][aws_profile][aws_region][group_id] = str(found_days) + ", " + owner

def printer(ddl, path):
    if os.path.isfile(path):
        os.remove(path)
    file = open(path, "w")
    for profile in ddl.keys():
        print(profile, ":", file=file)
        for region in ddl[profile]:
            print(" ", region, ": ", file=file)
            for group in ddl[profile][region]:
                print("  ", str(group) + ",", ddl[profile][region][group], file=file)

count = 0
for dictionary in output:
    if count == 4:
        path = "./over90days.txt"
    else:
        path = "./under" + str(count*30) + "days.txt"
    printer(dictionary, path)
    count += 1
