import pandas as pd
from ollama_ddi_analyzer import OllamaDDIAnalyzer  # Assuming you saved the previous script as ollama_ddi_analyzer.py

# Path to your drug interactions CSV file
CSV_PATH = 'drug_interactions.csv'  # Update this with your actual file path

# Initialize the analyzer
analyzer = OllamaDDIAnalyzer(CSV_PATH)

# List of drugs to check interactions
drugs_to_check = ['Trioxsalen', 'Verteporfin']

# Check interactions
alerts = analyzer.check_drug_interactions(drugs_to_check)

# Print out the alerts
print("Drug Interaction Alerts:")
for alert in alerts:
    print("\n" + "="*50)
    print(alert)
    print("="*50)