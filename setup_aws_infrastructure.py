"""
AWS Infrastructure Setup Script
Creates all required AWS resources using boto3
5 Services: S3, DynamoDB, Lambda, EC2, CloudWatch
"""
import boto3
import json
import time
import os
import base64

# Configuration
AWS_REGION = 'eu-north-1'
ACCOUNT_ID = '028061992080'

# Resource Names
S3_BUCKET = 'agri-forestry-bucket-028061992080'
DYNAMODB_TABLE = 'agri-forestry-logs'
LAMBDA_FUNCTION = 'agri-forestry-analyzer'
EC2_KEY_NAME = 'cloud-key-pair'
EC2_SECURITY_GROUP = 'agri-forestry-sg'
EC2_INSTANCE_NAME = 'agri-forestry-server'
AMI_ID = 'ami-0f50f13aefb6c0a5d'
INSTANCE_TYPE = 't3.small'

# Lambda function code
LAMBDA_CODE = '''
import json

def lambda_handler(event, context):
    """Analyze crop data and return insights"""
    crops = event.get('crops', [])
    
    total_area = sum(c.get('area', 0) for c in crops)
    agriculture_count = len([c for c in crops if c.get('type') == 'agriculture'])
    forestry_count = len([c for c in crops if c.get('type') == 'forestry'])
    
    analysis = {
        'total_crops': len(crops),
        'total_area': total_area,
        'agriculture_count': agriculture_count,
        'forestry_count': forestry_count,
        'recommendation': 'Diversify crops for better risk management' if len(crops) < 3 else 'Good diversification',
        'status': 'analyzed'
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(analysis)
    }
'''

def create_s3_bucket():
    """Create S3 bucket for storing images"""
    print("Creating S3 bucket...")
    s3 = boto3.client('s3', region_name=AWS_REGION)
    
    try:
        # Check if bucket exists
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"S3 bucket {S3_BUCKET} already exists")
    except:
        try:
            s3.create_bucket(
                Bucket=S3_BUCKET,
                CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
            )
            print(f"S3 bucket {S3_BUCKET} created successfully")
            
            # Enable public access for images (optional, for viewing uploaded images)
            s3.put_public_access_block(
                Bucket=S3_BUCKET,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
        except Exception as e:
            print(f"Error creating S3 bucket: {e}")
    
    return S3_BUCKET


def create_dynamodb_table():
    """Create DynamoDB table for activity logging"""
    print("Creating DynamoDB table...")
    dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
    
    try:
        # Check if table exists
        dynamodb.describe_table(TableName=DYNAMODB_TABLE)
        print(f"DynamoDB table {DYNAMODB_TABLE} already exists")
    except:
        try:
            dynamodb.create_table(
                TableName=DYNAMODB_TABLE,
                KeySchema=[
                    {'AttributeName': 'log_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'log_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"DynamoDB table {DYNAMODB_TABLE} created successfully")
            
            # Wait for table to be active
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=DYNAMODB_TABLE)
            print("DynamoDB table is now active")
        except Exception as e:
            print(f"Error creating DynamoDB table: {e}")
    
    return DYNAMODB_TABLE


def create_lambda_function():
    """Create Lambda function for serverless analysis"""
    print("Creating Lambda function...")
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    iam = boto3.client('iam', region_name=AWS_REGION)
    
    # Create IAM role for Lambda
    role_name = 'agri-forestry-lambda-role'
    role_arn = f'arn:aws:iam::{ACCOUNT_ID}:role/{role_name}'
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        iam.get_role(RoleName=role_name)
        print(f"IAM role {role_name} already exists")
    except:
        try:
            iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for Agriculture Forestry Lambda function'
            )
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            print(f"IAM role {role_name} created")
            time.sleep(10)  # Wait for role to propagate
        except Exception as e:
            print(f"Error creating IAM role: {e}")
    
    # Create Lambda function
    try:
        lambda_client.get_function(FunctionName=LAMBDA_FUNCTION)
        print(f"Lambda function {LAMBDA_FUNCTION} already exists")
    except:
        try:
            # Create zip file for Lambda code
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('lambda_function.py', LAMBDA_CODE)
            zip_buffer.seek(0)
            
            lambda_client.create_function(
                FunctionName=LAMBDA_FUNCTION,
                Runtime='python3.11',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_buffer.read()},
                Description='Crop analysis function for Agriculture & Forestry app',
                Timeout=30,
                MemorySize=128
            )
            print(f"Lambda function {LAMBDA_FUNCTION} created successfully")
        except Exception as e:
            print(f"Error creating Lambda function: {e}")
    
    return LAMBDA_FUNCTION


def create_cloudwatch_dashboard():
    """Create CloudWatch dashboard for monitoring"""
    print("Creating CloudWatch dashboard...")
    cloudwatch = boto3.client('cloudwatch', region_name=AWS_REGION)
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["AgriForestry", "UserSignups"],
                        ["AgriForestry", "UserLogins"],
                        ["AgriForestry", "CropsAdded"]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": AWS_REGION,
                    "title": "Application Metrics"
                }
            }
        ]
    }
    
    try:
        cloudwatch.put_dashboard(
            DashboardName='AgriForestry-Dashboard',
            DashboardBody=json.dumps(dashboard_body)
        )
        print("CloudWatch dashboard created successfully")
    except Exception as e:
        print(f"Error creating CloudWatch dashboard: {e}")


def create_security_group():
    """Create security group for EC2 instance"""
    print("Creating Security Group...")
    ec2 = boto3.client('ec2', region_name=AWS_REGION)
    
    # Get default VPC
    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'is-default', 'Values': ['true']}])
    vpc_id = vpcs['Vpcs'][0]['VpcId'] if vpcs['Vpcs'] else None
    
    if not vpc_id:
        vpcs = ec2.describe_vpcs()
        vpc_id = vpcs['Vpcs'][0]['VpcId'] if vpcs['Vpcs'] else None
    
    try:
        # Check if security group exists
        sgs = ec2.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': [EC2_SECURITY_GROUP]}]
        )
        if sgs['SecurityGroups']:
            sg_id = sgs['SecurityGroups'][0]['GroupId']
            print(f"Security group {EC2_SECURITY_GROUP} already exists: {sg_id}")
            return sg_id
    except:
        pass
    
    try:
        response = ec2.create_security_group(
            GroupName=EC2_SECURITY_GROUP,
            Description='Security group for Agriculture & Forestry Flask app',
            VpcId=vpc_id
        )
        sg_id = response['GroupId']
        print(f"Security group created: {sg_id}")
        
        # Add inbound rules
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                # SSH
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
                },
                # HTTP
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP access'}]
                },
                # Flask app port
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 5000,
                    'ToPort': 5000,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Flask app access'}]
                }
            ]
        )
        print("Security group rules added")
        return sg_id
    except Exception as e:
        print(f"Error creating security group: {e}")
        return None


def create_ec2_instance(sg_id):
    """Create EC2 instance for hosting the Flask app"""
    print("Creating EC2 instance...")
    ec2 = boto3.client('ec2', region_name=AWS_REGION)
    ec2_resource = boto3.resource('ec2', region_name=AWS_REGION)
    
    # Check if instance already exists
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': [EC2_INSTANCE_NAME]},
            {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopped']}
        ]
    )
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            print(f"EC2 instance {EC2_INSTANCE_NAME} already exists: {instance['InstanceId']}")
            if instance['State']['Name'] == 'stopped':
                ec2.start_instances(InstanceIds=[instance['InstanceId']])
                print("Starting stopped instance...")
            return instance['InstanceId']
    
    # User data script to setup the instance
    user_data = '''#!/bin/bash
yum update -y
yum install -y python3 python3-pip git
pip3 install flask flask-sqlalchemy werkzeug boto3 gunicorn
cd /home/ec2-user
git clone https://github.com/Prithviiixx/cpp.git app || true
cd app/flask_app
pip3 install -r requirements.txt || true
'''
    
    try:
        response = ec2.run_instances(
            ImageId=AMI_ID,
            InstanceType=INSTANCE_TYPE,
            KeyName=EC2_KEY_NAME,
            SecurityGroupIds=[sg_id],
            MinCount=1,
            MaxCount=1,
            UserData=user_data,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': EC2_INSTANCE_NAME}]
            }],
            IamInstanceProfile={
                'Name': 'EC2-AgriForestry-Role'
            } if check_instance_profile_exists() else {}
        )
        
        instance_id = response['Instances'][0]['InstanceId']
        print(f"EC2 instance created: {instance_id}")
        
        # Wait for instance to be running
        print("Waiting for instance to be running...")
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        
        # Get public IP
        instance_info = ec2.describe_instances(InstanceIds=[instance_id])
        public_ip = instance_info['Reservations'][0]['Instances'][0].get('PublicIpAddress')
        print(f"Instance is running. Public IP: {public_ip}")
        
        return instance_id
    except Exception as e:
        print(f"Error creating EC2 instance: {e}")
        return None


def check_instance_profile_exists():
    """Check if EC2 instance profile exists"""
    iam = boto3.client('iam', region_name=AWS_REGION)
    try:
        iam.get_instance_profile(InstanceProfileName='EC2-AgriForestry-Role')
        return True
    except:
        return False


def create_ec2_instance_role():
    """Create IAM role and instance profile for EC2"""
    print("Creating EC2 IAM role...")
    iam = boto3.client('iam', region_name=AWS_REGION)
    
    role_name = 'EC2-AgriForestry-Role'
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    # Create role
    try:
        iam.get_role(RoleName=role_name)
        print(f"Role {role_name} already exists")
    except:
        try:
            iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for EC2 Agriculture Forestry app'
            )
            
            # Attach policies
            policies = [
                'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                'arn:aws:iam::aws:policy/AWSLambda_FullAccess',
                'arn:aws:iam::aws:policy/CloudWatchFullAccess'
            ]
            
            for policy in policies:
                iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)
            
            print(f"Role {role_name} created with policies")
        except Exception as e:
            print(f"Error creating role: {e}")
    
    # Create instance profile
    try:
        iam.get_instance_profile(InstanceProfileName=role_name)
        print(f"Instance profile {role_name} already exists")
    except:
        try:
            iam.create_instance_profile(InstanceProfileName=role_name)
            iam.add_role_to_instance_profile(
                InstanceProfileName=role_name,
                RoleName=role_name
            )
            print(f"Instance profile {role_name} created")
            time.sleep(10)  # Wait for propagation
        except Exception as e:
            print(f"Error creating instance profile: {e}")


def get_ec2_public_ip():
    """Get the public IP of the EC2 instance"""
    ec2 = boto3.client('ec2', region_name=AWS_REGION)
    
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': [EC2_INSTANCE_NAME]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            return instance.get('PublicIpAddress')
    
    return None


def main():
    """Main function to create all AWS infrastructure"""
    print("=" * 60)
    print("Agriculture & Forestry AWS Infrastructure Setup")
    print("=" * 60)
    print(f"Region: {AWS_REGION}")
    print(f"Account ID: {ACCOUNT_ID}")
    print("=" * 60)
    
    # 1. Create S3 bucket
    create_s3_bucket()
    print()
    
    # 2. Create DynamoDB table
    create_dynamodb_table()
    print()
    
    # 3. Create Lambda function
    create_lambda_function()
    print()
    
    # 4. Create CloudWatch dashboard
    create_cloudwatch_dashboard()
    print()
    
    # 5. Create EC2 IAM role and instance profile
    create_ec2_instance_role()
    print()
    
    # 6. Create Security Group
    sg_id = create_security_group()
    print()
    
    # 7. Create EC2 instance
    if sg_id:
        instance_id = create_ec2_instance(sg_id)
        print()
    
    print("=" * 60)
    print("Infrastructure setup complete!")
    
    public_ip = get_ec2_public_ip()
    if public_ip:
        print(f"EC2 Public IP: {public_ip}")
        print(f"Application URL: http://{public_ip}:5000")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
