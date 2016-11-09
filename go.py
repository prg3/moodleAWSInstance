#!/usr/bin/python
import boto3
import aws_utils
import sys
import os
import base64
import pprint
import credentials

pp = pprint.PrettyPrinter(indent=4)

os.environ["AWS_SECRET_ACCESS_KEY"] = credentials.config['aws_secret']
os.environ["AWS_ACCESS_KEY_ID"] = credentials.config['aws_key']

#Some configuration
# Preconfigure the pubkey and use the name Default
ami="ami-3de23653" # Ubuntu 16.10 - EBS - Official Image
pubkey_name="Default"

# Read in the userdata for Instance creation
fh=open("userdata.sh")
userdata=fh.read()
fh.close()

# Create the connections
ec2_client = boto3.client('ec2')
route53=boto3.client('route53')
autoscale=boto3.client('autoscaling')
elb = boto3.client('elb')
ec2 = boto3.resource('ec2', region_name='ap-northeast-2', api_version='2016-04-01')

for i in ec2.vpcs.all():
	if i.is_default:
		vpc=i

#print ("Creating security groups")
aws_utils.secgroup(ec2, 'external-http', [443,80], 'tcp', vpc, '0.0.0.0/0')
aws_utils.secgroup(ec2, 'external-ssh', [22], 'tcp', vpc, '0.0.0.0/0')

print ("Creating and tagging the instance")
instance = ec2.create_instances(
	ImageId=ami,
	MinCount=1,
	MaxCount=1,
	KeyName=pubkey_name,
	SecurityGroups=['external-ssh', 'external-http'],
	UserData=userdata,
	InstanceType='t2.micro',
	)
ec2.create_tags(
	Resources=[str(instance[0].id)],
	Tags=[{'Key': 'Name', 'Value': 'appserver'}]
	)
print ("Instance created")
main_instance=ec2.Instance(str(instance[0].id))
main_ip=main_instance.public_ip_address
int_ip=main_instance.private_ip_address

print ("Connect by running 'ssh ubuntu@%s'")%(main_ip)
print ("You can login to Moodle in a few minutes at http://%s")%(main_ip)
print ("Login with admin/myM00dleP@ssword")
