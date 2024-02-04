import pandas as pd

# Load the Excel sheet
data = pd.read_csv('Formatted_Medical_Advice_Proper_Sentences.csv', encoding='ISO-8859-1')

# Convert the data into a dictionary
symptom_advice_dict = pd.Series(data.Response.values, index=data.Prompts).to_dict()

def analyze_symptoms(user_input):
    user_input = user_input.lower()  # Convert to lowercase for comparison
    for symptom, advice in symptom_advice_dict.items():
        if symptom.lower() in user_input:  # Check if the symptom is mentioned in the user input
            return advice
    return "I'm not sure what the issue could be. It's best to consult a healthcare professional."