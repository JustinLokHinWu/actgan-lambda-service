import json
import os
import boto3

def lambda_handler(event, context):
    if event['queryStringParameters'] != None and 'dataset' in event['queryStringParameters']:
        dataset = event['queryStringParameters']['dataset']
    else:
        print('Missing "dataset" query parameter')
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
        models = s3.list_objects_v2(Bucket=bucket_name, Prefix='{}/G_jit_epoch_'.format(dataset))["Contents"]
    except:
        print('Failed to get config for dataset "{}" from S3'.format(dataset))
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid dataset query parameter')
        }
    
    try:
        epochs = [int(model['Key'].split('_')[-1]) for model in models]
    except:
        print('Failed to extract list of epochs')
        return {
            'statusCode': 500,
        }

    return {
        'headers': { "content-type":"application/json" },
        'statusCode': 200,
        'body': json.dumps(epochs)
    }


if __name__=='__main__':
    lambda_handler({'queryStringParameters': {'dataset': 'cifar'}},0)