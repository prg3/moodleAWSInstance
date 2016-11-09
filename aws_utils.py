#!/usr/bin/python
import boto3
import botocore

def secgroup ( ec2, sgname, ports, proto, vpc, cidr_range ):
	boto3.resource('ec2')
	sg = None
	for group in ec2.security_groups.all():
		if group.group_name == sgname:	
			sg = group
	if sg == None:
		sg = ec2.create_security_group(
    		GroupName=sgname,
    		Description='AutoCreated Group',
    		VpcId=vpc.id
    	)
	for port in ports:
		try:
			sg.authorize_ingress(GroupId=str(sg.id), IpProtocol=proto, FromPort=port, ToPort=port, CidrIp=cidr_range)
		except (botocore.exceptions.ClientError):
			continue
