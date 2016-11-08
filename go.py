#!/usr/bin/python
import boto3
import awsutils
import sys
import os
import base64
import pprint
import credentials

pp = pprint.PrettyPrinter(indent=4)

os.environ["AWS_SECRET_ACCESS_KEY"] = credentials.config['aws_secret']
os.environ["AWS_ACCESS_KEY_ID"] = credentials.config['aws_key']

#Some configuration, leave blank for automatic
domain="awstest.majestik.org"
ami="ami-fce3c696" # Ubuntu 14.04 LTS - SSD
pubkey=None
pubkey_name="Default"

#Read .ssh/id_rsa.pub if pubkey is blank
if not pubkey:
	print("Reading id_rsa.pub from home")
	from os.path import expanduser
	home = expanduser("~")
	fh=open(home + "/.ssh/id_rsa.pub")
	pubkey=fh.read()
	fh.close()

# Create the connections
boto_session = boto3.session.Session(
        aws_access_key_id=credentials.config['aws_key'],
        aws_secret_access_key=credentials.config['aws_secret']
        )
ec2_client = boto3.client('ec2')
route53=boto3.client('route53')
autoscale=boto3.client('autoscaling')
elb = boto3.client('elb')
ec2 = boto_session.resource('ec2')

print ("Creating security groups")
awsutils.secgroup(ec2, 'external-http', [443,80], 'tcp', vpc, '0.0.0.0/0')
awsutils.secgroup(ec2, 'external-ssh', [22], 'tcp', vpc, '0.0.0.0/0')

#Create and import Key
print("\nEnsuring public key is setup")
iskey=None
for key in ec2_client.describe_key_pairs()['KeyPairs']:
	if key['KeyName'] == pubkey_name:
		iskey=True
if not iskey:
	ec2_client.import_key_pair(
		KeyName=pubkey_name,
		PublicKeyMaterial=pubkey
	)

ound=None
for instanceres in ec2_client.describe_instances()['Reservations']:
	for instance in instanceres['Instances']:
		if instance['State']['Name'] == "terminated":
			continue
		if 'Tags' in instance.keys():
			for tag in instance['Tags']:
				if tag['Key'] == "Name":
					if tag['Value'] == 'appserver':
						found=True
						main_instance=ec2.Instance(instance['InstanceId'])
						print "Instance already exists, you may need to terminate and recreate"

if not found:
	print ("Creating and tagging the instance")
	instance = ec2.create_instances(
		ImageId=ami_base,
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
