import json
import os
import boto3

def lambda_handler(event, context):
    # try:
    #     bucket_name = os.environ['AWS_BUCKET_NAME']
    #     s3 = boto3.client('s3')
    #     bucket = s3.list_objects(Bucket=bucket_name, Delimiter='/')

    #     prefixes = [prefix_obj.get('Prefix')[:-1] for prefix_obj in bucket.get('CommonPrefixes')]
    # except:
    #     print('Failed to get datasets from S3')
    #     return {
    #         'statusCode': 500,
    #         'body': 'Failed to get datasets'
    #     }

    # print(prefixes)
    return {
        'statusCode': 200,
        'body': prefixes
    }

if __name__=='__main__':
    lambda_handler(0,0)