import concurrent.futures
from ollama_ddi_analyzer import OllamaDDIAnalyzer
from blockchain import get_patient_drug_history  # Assuming drug history is fetched from blockchain

# Path to your drug interactions CSV file
CSV_PATH = 'drug_interactions.csv'  # Ensure the correct path

# Initialize the Ollama-based analyzer
analyzer = OllamaDDIAnalyzer(CSV_PATH)

def check_interaction(primary_drug, secondary_drug):
    """Check interaction between two drugs and return formatted results."""
    drugs_to_check = [primary_drug, secondary_drug]
    alerts = analyzer.check_drug_interactions(drugs_to_check)
    
    result = f"Interaction between {primary_drug} and {secondary_drug}:\n"
    for alert in alerts:
        result += "\n" + "="*50 + "\n"
        result += str(alert) + "\n"
        result += "="*50 + "\n"
    
    return result

def parallel_drug_checker(patient_id, primary_drug):
    """
    Runs multiple drug interaction checks in parallel between a primary drug 
    and a patient's historical drugs.
    """
    # Fetch patient's drug history from blockchain
    patient_drug_history = get_patient_drug_history(patient_id)
    
    if not patient_drug_history:
        return [f"No drug history found for patient {patient_id}."]
    
    results = []

    # Using ThreadPoolExecutor to run checks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_drug = {
            executor.submit(check_interaction, primary_drug, drug): drug 
            for drug in patient_drug_history
        }
        
        for future in concurrent.futures.as_completed(future_to_drug):
            drug = future_to_drug[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(f"Error checking interaction with {drug}: {str(e)}")
    
    return results

# Example Usage
if __name__ == "__main__":
    patient_id = "123456"  # This will be dynamically passed in actual implementation
    primary_drug = "Verteporfin"  # Assume the doctor prescribes this

    interaction_results = parallel_drug_checker(patient_id, primary_drug)

    print(f"Drug Interaction Results for {primary_drug}:")
    for result in interaction_results:
        print(result)
        print("\n" + "-"*60 + "\n")
