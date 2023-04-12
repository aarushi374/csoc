import boto3
import csv
import pandas as pd
import time
import threading
from botocore.config import Config
# List of AWS regions to gather EC2 instances data from

# Connect to S3
s3 = boto3.client('s3')
s3_client = boto3.client("s3")

def available_regions(service):

    regions = []

    client = boto3.client(service)

    response = client.describe_regions()

    for item in response["Regions"]:

        regions.append(item["RegionName"])

    return regions
# Loop through each region
#UNLEASH THE POWER OF BRAHMASTRA
def main():
    regions = available_regions("ec2")
    filename = f'/home/aarushi/.local/lib/python3.10/site-packages/gimme_aws_creds/running_instances.csv'
    with open(filename,'w') as f:

            #if the file is not yet created
            writer = csv.writer(f)
            writer.writerow(['Instance ID','AMI_ID','LAUNCHTIME', 'State', 'Region','Private IP Address', 'Public IP Address',
            'Instance Type', 'Name', 'OwnerEmail', 'BE', 'BU','AMI NAME','AMI CREATE DATE','AMIBU','RELEASE',
            'Version','POD','CPEVAL','QUALYSEVAL','APPENV'])
    for region in regions:
        # Connect to EC2 in the region
        ec2 = boto3.client('ec2', region_name=region)
        client = boto3.client("ec2", config=my_config)

        # Get a list of all running instances
        instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])['Reservations']
        instances = [instance for reservation in instances for instance in reservation['Instances']]
        ec21=boto3.Session().resource('ec2',region_name = region)
        instance_info = []

        for instance in instances:

            instance_id="Instance ID not found"
            state="State not found"
            private_ip_address="Private IP address not found"
            public_ip_address="Public IP address not found"
            instance_type="Instance type not found"
            name = 'Name not found in tags'
            owneremail = 'Owner email not found in tags'
            ibe = 'BE not found'
            ibu = 'BU not found'
            ami_name = 'AMI not found'
            ami_create_date = ''
            bu = 'AMI BU not found'
            release = 'AMI release info not available'
            release_ver = 0.0
            pod="POD not found"
            cpeval="0"
            qualyseval="0"
            applicationenv="Application Enviornment not found"

            #get info about the instance
            instance_id = instance['InstanceId']
            image_id=instance['ImageId']
            launch_time=instance['LaunchTime']
            state = instance['State']['Name']
            private_ip_address = instance.get('PrivateIpAddress', '')
            public_ip_address = instance.get('PublicIpAddress', '')
            instance_type = instance['InstanceType']

            #loop through the tags of instance
            for tags in instance['Tags']:
                if (tags['Key']).strip().upper() == 'NAME':
                    name = tags['Value']
                if (tags['Key']).strip().upper() == 'OWNEREMAIL':
                    owneremail = tags['Value']
                if (tags['Key']).strip().upper() == 'BUSINESSENTITY':
                    ibe = tags['Value']
                if (tags['Key']).strip().upper() == 'BUSINESSUNIT':
                    ibu = tags['Value']
                if (tags['Key']).strip().upper() == 'POD':
                    pod=tags['Value']
                if (tags['Key']).strip().upper() == 'CPEVAL':
                    cpeval=tags['Value']
                if (tags['Key']).strip().upper() == 'QUALYSEVAL':
                    qualyseval=tags['Value']
                if (tags['Key']).strip().upper() == 'APPLICATIONENV':
                    applicationenv=tags['Value']

            ami_date=''

            #get the ami details of the instance
            ami_details = ec21.images.filter(ImageIds=[instance['ImageId']])
            try:
                ami_name = list(ami_details)[0].name
                ami_create_date = list(ami_details)[0].creation_date

                ami_tags= list(ami_details)[0].tags

                for ami_tag1 in ami_tags:

                    if (ami_tag1['Key']).strip().upper() == 'BUSINESSUNIT':
                        bu = ami_tag1['Value']

                    if (ami_tag1['Key']).strip().upper() == 'RELEASE':
                        release = ami_tag1['Value']
                        release_ver = release[1:len(release)]

            except IndexError:
                ami_name = 'AMI not found'
                ami_create_date = ''
                ami_tags = 'AMI not found'
                bu = 'AMI BU not found'
                release = 'AMI release info not available'
                release_ver = 0.0
            except TypeError:
                release = 'AMI release info not available'
                release_ver = 0.0

            # we only need the creation date of the AMI so remove the time given
            if len(ami_create_date)!=0:
                ami_create_date_list=ami_create_date.split("T")
                print(ami_create_date_list)
                print(ami_create_date_list[0])
                ami_date=ami_create_date_list[0]

            #append all the information
            instance_info.append([instance_id,image_id,launch_time, state, region,private_ip_address,
            public_ip_address, instance_type, name, owneremail, ibe,ibu,
            ami_name,ami_date,bu,release,release_ver,pod,cpeval,qualyseval,applicationenv])

        #defining the file name


        #Implementing the concept of locks so that no two lambdas can write on the same file at the same time
        csv_writer_lock = threading.Lock()




        #appending the file
        with open(filename, 'a', newline='') as file:

            writer = csv.writer(file)


            for info in instance_info:

                writer.writerow(info)







