import torch

def load_model():
    model = torch.load("model.pt")
    return model


def boe():
    model = load_model()
    state0 = torch.tensor()