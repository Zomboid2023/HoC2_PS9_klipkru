import pandas as pd
import ollama
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaDDIAnalyzer:
    def __init__(self, csv_path, model='llama2'):
        """Initialize DDI Analyzer with Ollama"""
        self.df = pd.read_csv(csv_path)
        self.model = model
        self._verify_ollama_connection()
        
        self.severity_levels = {
            'CRITICAL': ['fatal', 'severe', 'life-threatening', 'extreme risk'],
            'HIGH': ['major', 'significant', 'dangerous'],
            'MODERATE': ['moderate', 'potential', 'caution'],
            'LOW': ['minor', 'slight', 'minimal']
        }
    
    def _verify_ollama_connection(self):
        """Verify Ollama model availability"""
        try:
            models = ollama.list()
            available_models = [m['name'] for m in models['models']]
            
            if self.model not in available_models:
                logger.warning(f"Model {self.model} not found. Pulling the model...")
                ollama.pull(self.model)
            
            logger.info(f"Using Ollama model: {self.model}")
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            raise

    def classify_interaction_severity(self, interaction_description):
        """Determine severity level of a drug interaction"""
        description_lower = interaction_description.lower()
        for severity, keywords in self.severity_levels.items():
            if any(keyword in description_lower for keyword in keywords):
                return severity
        return 'LOW'

    def _get_llm_interaction_details(self, drug1, drug2, original_description):
        """Enhance interaction details using Ollama AI"""
        try:
            prompt = f"""
            Provide a professional-level explanation of the interaction between {drug1} and {drug2}. 
            Original description: {original_description}
            Include:
            - Mechanism of interaction
            - Clinical implications
            - Recommended precautions
            Response should be concise and medically accurate.
            """
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content']
        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            return original_description

    def generate_interaction_alert(self, drug1, drug2, interaction_description):
        """Generate an alert message for drug interaction"""
        severity = self.classify_interaction_severity(interaction_description)
        alert_templates = {
            'CRITICAL': f"🚨 CRITICAL ALERT 🚨\nDrugs: {drug1} & {drug2}\nSeverity: CRITICAL\nImmediate consultation required!",
            'HIGH': f"⚠ HIGH-RISK INTERACTION ⚠\nDrugs: {drug1} & {drug2}\nSeverity: HIGH\nSeek medical advice.",
            'MODERATE': f"🟠 MODERATE INTERACTION 🟠\nDrugs: {drug1} & {drug2}\nSeverity: MODERATE\nMonitor symptoms.",
            'LOW': f"🟢 LOW-RISK INTERACTION 🟢\nDrugs: {drug1} & {drug2}\nSeverity: LOW\nMinimal risk detected."
        }
        enhanced_description = self._get_llm_interaction_details(drug1, drug2, interaction_description)
        return f"{alert_templates[severity]}\n\nDetails: {enhanced_description}"

    def check_drug_interactions(self, drugs):
        """Check interactions for a list of drugs"""
        alerts = []
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                interaction = self.df[
                    ((self.df['Drug 1'] == drugs[i]) & (self.df['Drug 2'] == drugs[j])) |
                    ((self.df['Drug 1'] == drugs[j]) & (self.df['Drug 2'] == drugs[i]))
                ]
                if not interaction.empty:
                    alert = self.generate_interaction_alert(drugs[i], drugs[j], interaction['Interaction Description'].values[0])
                    alerts.append(alert)
        return alerts
