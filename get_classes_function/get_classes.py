import json
import os
import boto3

def lambda_handler(event, context):
    if 'dataset' in event['queryStringParameters']:
        dataset = event['queryStringParameters']['dataset']
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing dataset query parameter')
        }
    
    try:
        bucket_name = os.environ['AWS_BUCKET_NAME']
        s3 = boto3.client('s3')
    except:
        print('Failed to access S3 bucket')
        return {
            'statusCode': 500,
        }

    try:
        config_object = s3.get_object(Bucket=bucket_name, Key="{}/config.json".format(dataset))
    except:
        print('Failed to get config for dataset "{}" from S3'.format(dataset))
        return {
            'statusCode': 500,
        }
    
    try:
        config = json.loads(config_object['Body'].read().decode())
    except:
        print('Failed to read config as json')
        return {
            'statusCode': 500,
        }

    return {
        'headers': { "content-type":"application/json" },
        'statusCode': 200,
        'body': json.dumps(config['classes'])
    }


if __name__=='__main__':
    lambda_handler(0,0)