import json
import io
import base64
import torch
import torchvision
from pathlib import Path
# from helpers import generate_noise, label_to_onehot
def label_to_onehot(label, num_classes):
    encoding = torch.zeros((1, num_classes))
    encoding[0, label] = 1

    return encoding

def generate_noise(noise_size):
    n = torch.randn(1, noise_size)
    return n
# You can reference EFS files by including your local mount path, and then
# treat them like any other file. Local invokes may not work with this, however,
# as the file/folders may not be present in the container.
FILE = Path("/mnt/lambda/file")

def lambda_handler(event, context):
    # probabilities = model.forward(image_transforms(np.array(image)).reshape(-1, 1, 28, 28))
    # label = torch.argmax(probabilities).item()
    model_file = 'models/cifar/G_jit_epoch_180'
    with open('configs/cifar.json') as f:
        cfg = json.load(f)
    # model_runner = GeneratorRunner(AttrDict(config['model_params']))

    # model = ACGAN_Generator(config['model_params'])
    # model.load_state_dict(torch.load(model_file))
    # model.eval()

    image_class = 0

    noise = generate_noise(cfg['model_params']['noise_size'])
    onehot = label_to_onehot(image_class, cfg['model_params']['n_classes'])


    model = torch.jit.load(model_file, map_location=torch.device('cpu'))
    model.eval()

    result = model(noise, onehot)
    # result = model_runner.evaluate(0,100,4234)

    # print(result)


    result_io = io.BytesIO()
    torchvision.utils.save_image(result, result_io, 'JPEG', quality=70)
    # # result.save(result_io, 'JPEG', quality=70)
    result_io.seek(0)
    
    return {
        'headers': { "Content-Type": "image/png" },
        'statusCode': 200,
        'body': base64.b64encode(result_io.getvalue()).decode('utf-8'),
        'isBase64Encoded': True
    }





    # wrote_file = False
    # contents = None
    # # The files in EFS are not only persistent across executions, but if multiple
    # # Lambda functions are mounted to the same EFS file system, you can read and
    # # write files from either function.
    # if not FILE.is_file():
    #     with open(FILE, 'w') as f:
    #         contents = "Hello, EFS!\n"
    #         f.write(contents)
    #         wrote_file = True
    # else:
    #     with open(FILE, 'r') as f:
    #         contents = f.read()
    # return {
    #     "statusCode": 200,
    #     "body": json.dumps({
    #         "file_contents": contents,
    #         "created_file": wrote_file
    #     }),
    # }
if __name__=='__main__':
    print(lambda_handler(0,0))
