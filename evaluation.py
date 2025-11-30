import pandas as pd
import json
from agents.omni_support import omni_support_agent
from agents.workflow_auditor import workflow_auditor_agent
from agents.data_guardian import data_guardian_agent
from tools.analytics_tools import generate_weekly_report
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

class EnterpriseFusionEvaluator:
    def __init__(self):
        self.results = {}
    
    def evaluate_support_agent(self):
        """Evaluate Omni-Support Agent accuracy"""
        # Gold standard test data
        test_tickets = [
            {"id": 11, "customer_id": 1001, "message": "How do I reset password?", "channel": "chat"},
            {"id": 12, "customer_id": 1002, "message": "My payment failed 3 times", "channel": "email"},
            {"id": 13, "customer_id": 1003, "message": "App crashes on startup", "channel": "ticket"},
        ]
        gold_labels = ["faq", "billing", "bug"]  # Expected intents
        
        predictions = []
        for ticket in test_tickets:
            result = omni_support_agent(ticket)
            predictions.append(result['intent'])
        
        accuracy = accuracy_score(gold_labels, predictions)
        self.results['support_accuracy'] = accuracy
        self.results['support_report'] = classification_report(gold_labels, predictions, output_dict=True)
        
        return {
            "test_tickets": len(test_tickets),
            "accuracy": accuracy,
            "classification_report": self.results['support_report']
        }
    
    def evaluate_workflow_auditor(self):
        """Test workflow bottleneck detection"""
        result = workflow_auditor_agent()
        detected_bottlenecks = len(result['bottlenecks'])
        recommendations = len(result['recommendations'])
        
        self.results['bottlenecks_detected'] = detected_bottlenecks
        self.results['recommendations_generated'] = recommendations
        
        return {
            "bottlenecks_detected": detected_bottlenecks,
            "recommendations": recommendations,
            "expected_bottlenecks": 3  # From sample data
        }
    
    def evaluate_data_quality(self):
        """Test data guardian quality scoring"""
        result = data_guardian_agent()
        quality_score = result['quality_score']
        issues_found = len(result['issues'])
        
        self.results['data_quality_score'] = quality_score
        self.results['data_issues'] = issues_found
        
        return {
            "quality_score": quality_score,
            "issues_found": issues_found,
            "pass_threshold": quality_score > 0.7
        }
    
    def generate_final_report(self):
        """Comprehensive evaluation report"""
        eval_support = self.evaluate_support_agent()
        eval_workflow = self.evaluate_workflow_auditor()
        eval_data = self.evaluate_data_quality()
        analytics = generate_weekly_report()
        
        final_report = {
            "overall_score": np.mean([
                eval_support['accuracy'],
                eval_workflow['bottlenecks_detected'] / 3,
                1 if eval_data['pass_threshold'] else 0
            ]),
            "support_agent": eval_support,
            "workflow_auditor": eval_workflow,
            "data_guardian": eval_data,
            "business_metrics": analytics['metrics'],
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        # Save to file
        with open('evaluation_results.json', 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        return final_report

# Quick test function
def run_full_evaluation():
    evaluator = EnterpriseFusionEvaluator()
    return evaluator.generate_final_report()
