import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import math

# MODEL
class Model(nn.Module):
    def __init__(self, input_size, output_size, hidden_dim, n_layers):
        super(Model, self).__init__()

        # Defining some parameters
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers

        #Defining the layers
        # RNN Layer
        self.rnn = nn.RNN(input_size, hidden_dim, n_layers, batch_first=True)   
        # Fully connected layer
        self.fc = nn.Linear(hidden_dim, output_size)
    
    def forward(self, x):
        batch_size = 50

        #Initializing hidden state for first input using method defined below
        hidden = self.init_hidden()

        # Passing in the input and hidden state into the model and obtaining outputs
        out, hidden = self.rnn(x, hidden)
        
        # Reshaping the outputs such that it can be fit into the fully connected layer
        out = out.contiguous().view(-1, self.hidden_dim)
        out = self.fc(out)
        
        return out, hidden
    
    def init_hidden(self):
        # This method generates the first hidden state of zeros which we'll use in the forward pass
        hidden = torch.zeros(self.n_layers, self.hidden_dim)
         # We'll send the tensor holding the hidden state to the device we specified earlier as well
        return hidden

#this method takes a predicted rrpv outputed by the model and applies the inverse of the function used to normalize the value
def inv_normalize(num):
    num = math.pow(num, -1)
    num = num-1
    num = math.pow(10, num)
    return int(num)



