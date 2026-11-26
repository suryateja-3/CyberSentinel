"""
utils/dl_models.py
==================
Deep Learning architectures in PyTorch for CyberSentinel.

1. URLCharCNN: 1D Convolutional Neural Network for character-level URL analysis.
2. FraudLSTM: Bidirectional LSTM for sequence modelling of SMS/text.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# ---------------------------------------------------------------------------
# 1D CNN for Malicious URLs
# ---------------------------------------------------------------------------
class URLCharCNN(nn.Module):
    """
    Treats a URL as a sequence of characters. 
    Applies multiple 1D convolutions of varying window sizes to detect local patterns.
    """
    def __init__(self, vocab_size: int, embed_dim: int, n_filters: int, filter_sizes: list, output_dim: int, dropout: float = 0.5):
        super().__init__()
        # padding_idx=0 means the embedding for token 0 is always a zero vector
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        # A ModuleList of 1D Conv layers
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embed_dim, out_channels=n_filters, kernel_size=fs)
            for fs in filter_sizes
        ])
        
        self.fc = nn.Linear(len(filter_sizes) * n_filters, output_dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, text):
        # text shape: [batch_size, sequence_length]
        
        embedded = self.embedding(text) 
        # embedded shape: [batch_size, sequence_length, embed_dim]
        
        # Conv1d expects input shape: [batch_size, in_channels, sequence_length]
        embedded = embedded.permute(0, 2, 1)
        
        # Apply convolution + ReLU
        # conved[n] shape: [batch_size, n_filters, sequence_length - filter_size[n] + 1]
        conved = [F.relu(conv(embedded)) for conv in self.convs]
        
        # Max-over-time pooling
        # pooled[n] shape: [batch_size, n_filters]
        pooled = [F.max_pool1d(conv, conv.shape[2]).squeeze(2) for conv in conved]
        
        # Concatenate pooled features
        cat = self.dropout(torch.cat(pooled, dim=1))
        # cat shape: [batch_size, n_filters * len(filter_sizes)]
        
        return self.fc(cat)


# ---------------------------------------------------------------------------
# Bi-LSTM for Fraud / SMS
# ---------------------------------------------------------------------------
class FraudLSTM(nn.Module):
    """
    Treats an SMS message as a sequence of words.
    Uses a bidirectional LSTM to capture sequence dependencies forward and backward.
    """
    def __init__(self, vocab_size: int, embed_dim: int, hidden_dim: int, output_dim: int, n_layers: int, bidirectional: bool, dropout: float = 0.3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        self.lstm = nn.LSTM(
            embed_dim, 
            hidden_dim, 
            num_layers=n_layers, 
            bidirectional=bidirectional, 
            dropout=dropout if n_layers > 1 else 0,
            batch_first=True
        )
        
        # If bidirectional, the hidden state size is doubled
        lstm_out_dim = hidden_dim * 2 if bidirectional else hidden_dim
        
        self.fc = nn.Linear(lstm_out_dim, output_dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, text, text_lengths):
        # text shape: [batch_size, seq_len]
        # text_lengths: actual length of each sequence in the batch (for packing)
        
        embedded = self.dropout(self.embedding(text))
        
        # Pack sequence to ignore padding elements during LSTM processing
        packed_embedded = nn.utils.rnn.pack_padded_sequence(
            embedded, text_lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        
        packed_output, (hidden, cell) = self.lstm(packed_embedded)
        
        # hidden shape: [num_layers * num_directions, batch_size, hidden_dim]
        # We extract the final hidden state of the top layer
        if self.lstm.bidirectional:
            # Concatenate the final forward and backward hidden states
            hidden = self.dropout(torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1))
        else:
            hidden = self.dropout(hidden[-1,:,:])
            
        # Pass through linear layer
        return self.fc(hidden)
