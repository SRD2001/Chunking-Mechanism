import hashlib

def calculate_hash(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

class MarkovModel:
    def __init__(self):
        self.transition_probabilities = {}

    def train(self, text):
        for i in range(len(text) - 1):
            char1 = text[i]
            char2 = text[i + 1]
            if char1 not in self.transition_probabilities:
                self.transition_probabilities[char1] = {}
            if char2 not in self.transition_probabilities[char1]:
                self.transition_probabilities[char1][char2] = 0
            self.transition_probabilities[char1][char2] += 1

        for char1 in self.transition_probabilities:
            total = sum(self.transition_probabilities[char1].values())
            for char2 in self.transition_probabilities[char1]:
                self.transition_probabilities[char1][char2] /= total

    def get_transition_probability(self, char1, char2):
        if char1 in self.transition_probabilities and char2 in self.transition_probabilities[char1]:
            return self.transition_probabilities[char1][char2]
        else:
            return 0.0

def double_sliding_window_chunking(data, window_size, markov_model, threshold=0.05):
    chunks = []
    start = 0
    w = window_size
    
    i = 0
    j = w
    k = 2 * w

    while k <= len(data):
        window1 = data[i:j]
        window2 = data[j:k]

        hash1 = calculate_hash(window1)
        hash2 = calculate_hash(window2)

        char1 = data[j-1]
        char2 = data[j]
        transition_probability = markov_model.get_transition_probability(char1, char2)

        if transition_probability < threshold:
            chunks.append(data[start:k])
            start = k
        
        i += w
        j += w
        k += w

    if start < len(data):
        chunks.append(data[start:])

    return chunks

import random
import string

def generate_large_file(size_in_mb):
    text = ''.join(random.choices(string.ascii_letters + string.digits, k=size_in_mb * 1024 * 1024))
    return text

if __name__ == "__main__":
    large_file_content = generate_large_file(10)

    markov_model = MarkovModel()
    markov_model.train(large_file_content)

    window_size = 1024 * 1024

    chunks = double_sliding_window_chunking(large_file_content, window_size, markov_model)

    print(f"Total chunks: {len(chunks)}")
    for idx, chunk in enumerate(chunks):
        print(f"Chunk {idx + 1}: Size = {len(chunk)} bytes, Hash = {calculate_hash(chunk)}")
