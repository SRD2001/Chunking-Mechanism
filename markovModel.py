import numpy as np

data = ["S", "M", "L", "S", "M", "S", "M", "L", "M", "S", "M", "L", "S", "M", "S", "M", "S", "M", "L", "S", "S", "S", "S"]
     
Sdata = []
Mdata = []
Ldata = []

for i in range(len(data) - 1):
    if data[i] == "S":
        Sdata.append(data[i + 1])
    elif data[i] == "M":
        Mdata.append(data[i + 1])
    elif data[i] == "L":
        Ldata.append(data[i + 1])

def count_transitions(next_data):
    SS, SM, SL = 0, 0, 0
    for item in next_data:
        if item == "S":
            SS += 1
        elif item == "M":
            SM += 1
        elif item == "L":
            SL += 1
    return SS, SM, SL

SS, SM, SL = count_transitions(Sdata)
MS, MM, ML = count_transitions(Mdata)
LS, LM, LL = count_transitions(Ldata)

def calculate_probabilities(SS, SM, SL):
    total = SS + SM + SL
    if total == 0:
        return 0, 0, 0
    return SS / total, SM / total, SL / total

p11, p12, p13 = calculate_probabilities(SS, SM, SL)
p21, p22, p23 = calculate_probabilities(MS, MM, ML)
p31, p32, p33 = calculate_probabilities(LS, LM, LL)

P = np.array([[p11, p12, p13],
              [p21, p22, p23],
              [p31, p32, p33]])

initial_state = [1, 0, 0]  

def markov_prediction(initial_state, P, steps=1):
    current_state = np.array(initial_state)
    for _ in range(steps):
        current_state = np.dot(current_state, P)
        predicted_state = np.argmax(current_state)  
    
        if predicted_state == 0:
            return "S"
        elif predicted_state == 1:
            return "M"
        elif predicted_state == 2:
            return "L"

predicted_chunk = markov_prediction(initial_state, P)
print(f"Predicted next chunking type: {predicted_chunk}")