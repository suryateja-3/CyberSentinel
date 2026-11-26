"""
utils/dl_tokenizers.py
======================
Simple custom tokenizers for Deep Learning models.
Allows us to save/load vocabulary states alongside PyTorch weights.
"""

import string
from collections import Counter
import re

class CharTokenizer:
    """
    Character-level tokenizer for URL CNN.
    Maps every character to an integer index.
    """
    def __init__(self, max_len=200):
        self.max_len = max_len
        # Create vocab with standard printable ASCII chars
        self.chars = list(string.printable)
        self.char2idx = {c: i+2 for i, c in enumerate(self.chars)}
        self.char2idx['<PAD>'] = 0
        self.char2idx['<UNK>'] = 1
        self.vocab_size = len(self.char2idx)
        
    def encode(self, text: str) -> list:
        # Convert string to list of character indices
        indices = [self.char2idx.get(c, 1) for c in text[:self.max_len]]
        # Pad if necessary
        if len(indices) < self.max_len:
            indices += [0] * (self.max_len - len(indices))
        return indices


class BasicWordTokenizer:
    """
    Word-level tokenizer for Fraud LSTM.
    Builds a vocabulary based on word frequency.
    """
    def __init__(self, max_vocab_size=10000, max_len=100):
        self.max_vocab_size = max_vocab_size
        self.max_len = max_len
        self.word2idx = {'<PAD>': 0, '<UNK>': 1}
        self.vocab_size = 2
        
    def _tokenize(self, text: str) -> list:
        # Simple lowercase and alphanumeric extraction
        text = str(text).lower()
        return re.findall(r'\b\w+\b', text)
        
    def build_vocab(self, texts: list):
        counter = Counter()
        for text in texts:
            counter.update(self._tokenize(text))
            
        # Keep most common words up to max_vocab_size
        most_common = counter.most_common(self.max_vocab_size - 2)
        for word, _ in most_common:
            self.word2idx[word] = self.vocab_size
            self.vocab_size += 1
            
    def encode(self, text: str) -> tuple:
        """Returns (padded_indices, actual_length)"""
        tokens = self._tokenize(text)
        actual_len = min(len(tokens), self.max_len)
        if actual_len == 0:
            actual_len = 1 # Prevent 0-length sequences for packing
            
        indices = [self.word2idx.get(w, 1) for w in tokens[:self.max_len]]
        
        if len(indices) < self.max_len:
            indices += [0] * (self.max_len - len(indices))
            
        # Ensure at least 1 token if input was empty
        if len(indices) == 0:
            indices = [1] + [0]*(self.max_len-1)
            
        return indices, actual_len
