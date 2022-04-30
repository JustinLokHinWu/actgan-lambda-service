import json
import io
import base64
import torch
import torchvision
import os
import boto3

cors_header = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET'
}

def label_to_onehot(label, num_classes):
    encoding = torch.zeros((1, num_classes))
    encoding[0, label] = 1

    return encoding

def generate_noise(noise_size):
    n = torch.randn(1, noise_size)
    return n

def transform_image(image):
    return (image / 2.0) + 0.5

def lambda_handler(event, context):
    # Query string validation
    if event['queryStringParameters'] != None:
        if 'dataset' in event['queryStringParameters']:
            dataset = event['queryStringParameters']['dataset']
        else:
            print('Missing "dataset" query parameter')
            return {
                'header': cors_header,
                'statusCode': 400,
                'body': json.dumps('Missing dataset query parameter')
            }

        if 'class_id' in event['queryStringParameters']:
            class_id = int(event['queryStringParameters']['class_id'])
        else:
            print('Missing "class_id" query parameter')
            return {
                'header': cors_header,
                'statusCode': 400,
                'body': json.dumps('Missing class_id query parameter')
            }

        if 'epoch' in event['queryStringParameters']:
            epoch = int(event['queryStringParameters']['epoch'])
        else:
            print('Missing "epoch" query parameter')
            return {
                'header': cors_header,
                'statusCode': 400,
                'body': json.dumps('Missing epoch query parameter')
            }

        if 'seed' in event['queryStringParameters']:
            seed = int(event['queryStringParameters']['seed'])
        else:
            print('Missing "seed" query parameter')
            return {
                'header': cors_header,
                'statusCode': 400,
                'body': json.dumps('Missing seed query parameter')
            }
    else:
        print('Missing query parameters')
        return {
            'header': cors_header,
            'statusCode': 400,
            'body': json.dumps('Missing query parameters')
        }
    
    # S3 Login
    try:
        bucket_name = os.environ['AWS_BUCKET_NAME']
        s3 = boto3.client('s3')
    except:
        print('Failed to access S3 bucket')
        return {
            'header': cors_header,
            'statusCode': 500,
        }

    # Open config file
    try:
        config_object = s3.get_object(
            Bucket=bucket_name, Key="{}/config.json".format(dataset))
    except:
        print('Failed to get config for dataset "{}" from S3'.format(dataset))
        return {
            'header': cors_header,
            'statusCode': 400,
            'body': json.dumps('Invalid dataset query parameter')
        }
    # Load config
    try:
        config = json.loads(config_object['Body'].read().decode())
    except:
        print('Failed to read config as json')
        return {
            'header': cors_header,
            'statusCode': 500,
        }

    # Fetch model file
    try:
        model_key = '{}/G_jit_epoch_{}'.format(dataset, epoch)
        model_object = s3.get_object(Bucket=bucket_name, Key=model_key)['Body']
    except:
        print('Failed to get model object for dataset "{}" epoch "{}" from S3'
            .format(dataset, epoch))
        return {
            'header': cors_header,
            'statusCode': 400,
            'body': json.dumps(
                'Invalid combination of dataset and epoch query parameters')
        }

    # Run model and apply transform
    try:
        torch.manual_seed(seed)
        noise = generate_noise(config['model_params']['noise_size'])
        onehot = label_to_onehot(class_id, config['model_params']['n_classes'])

        model = torch.jit.load(model_object, map_location=torch.device('cpu'))
        model.eval()

        result = transform_image(model(noise, onehot))
    except:
        print('Failed to run model')
        return {
            'header': cors_header,
            'statusCode': 500
        }

    # Convert result tensor to bytestream
    try:
        result_io = io.BytesIO()
        torchvision.utils.save_image(result, result_io, 'JPEG', quality=95)
        result_io.seek(0)
    except:
        print("Failed to convert output to bytestream")
        return {
            'header': cors_header,
            'statusCode': 500
        }
    
    return {
        'headers': cors_header | {"Content-type": "image/jpeg"},
        'statusCode': 200,
        'body': base64.b64encode(result_io.getvalue()).decode('utf-8'),
        'isBase64Encoded': True
    }

if __name__=='__main__':
    print(lambda_handler({
        "queryStringParameters": {
            "class_id": 5,
            "epoch": 180,
            "dataset": "cifar",
            "seed": 4129820
        }
    }, 0))
