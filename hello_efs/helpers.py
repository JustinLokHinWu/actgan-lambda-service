import torch

from hello_efs.app import lambda_handler

def label_to_onehot(label, num_classes):
    encoding = torch.zeros((1, num_classes), device='cpu')
    encoding[0, label] = 1

    return encoding

def generate_noise(noise_size):
    n = torch.randn(1, noise_size, device='cpu')
    return 
