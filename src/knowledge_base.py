"""
Knowledge Base Manager for Policy Information
Provides RAG (Retrieval Augmented Generation) capabilities
"""

import json
import os

class PolicyKnowledgeBase:
    """Manages policy information and retrieval"""
    
    def __init__(self, knowledge_base_path='policy_knowledge_base.json'):
        """Initialize knowledge base from JSON file"""
        self.knowledge_base_path = knowledge_base_path
        self.policies = self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load policy information from JSON file"""
        try:
            with open(self.knowledge_base_path, 'r') as f:
                data = json.load(f)
                return data['policies']
        except FileNotFoundError:
            print(f"⚠ Warning: Knowledge base file not found at {self.knowledge_base_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"⚠ Warning: Invalid JSON in knowledge base: {e}")
            return []
    
    def get_policy_info(self, policy_type):
        """
        Retrieve policy information for a specific type
        
        Args:
            policy_type: 'auto', 'property', or 'medical'
        
        Returns:
            dict: Policy information or None if not found
        """
        policy_type = policy_type.lower()
        
        for policy in self.policies:
            if policy['policy_type'] == policy_type:
                return policy
        
        return None
    
    def detect_policy_type(self, claim_text, extracted_info):
        """
        Detect policy type from claim text and extracted information
        
        Args:
            claim_text: Original claim document text
            extracted_info: Extracted claim information
        
        Returns:
            str: Detected policy type ('auto', 'property', 'medical', or 'unknown')
        """
        claim_lower = claim_text.lower()
        description = extracted_info.get('incident_description', '').lower()
        
        # Auto insurance keywords
        auto_keywords = ['vehicle', 'car', 'auto', 'accident', 'collision', 'traffic', 'driver', 'highway']
        
        # Property insurance keywords
        property_keywords = ['home', 'house', 'property', 'roof', 'fire', 'theft', 'burglary', 'damage to residence']
        
        # Medical insurance keywords
        medical_keywords = ['medical', 'hospital', 'doctor', 'injury', 'treatment', 'emergency room', 'surgery']
        
        # Count keyword matches
        auto_score = sum(1 for keyword in auto_keywords if keyword in claim_lower or keyword in description)
        property_score = sum(1 for keyword in property_keywords if keyword in claim_lower or keyword in description)
        medical_score = sum(1 for keyword in medical_keywords if keyword in claim_lower or keyword in description)
        
        # Return type with highest score
        scores = {
            'auto': auto_score,
            'property': property_score,
            'medical': medical_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'unknown'
        
        return max(scores, key=scores.get)
    
    def enrich_claim_with_policy(self, claim_text, extracted_info):
        """
        Enrich claim with relevant policy information
        
        Args:
            claim_text: Original claim document text
            extracted_info: Extracted claim information
        
        Returns:
            dict: Enriched claim with policy context
        """
        # Detect policy type
        policy_type = self.detect_policy_type(claim_text, extracted_info)
        
        # Get policy information
        policy_info = self.get_policy_info(policy_type)
        
        if not policy_info:
            return {
                'extracted_info': extracted_info,
                'policy_type': policy_type,
                'policy_context': None,
                'coverage_check': 'Unable to determine coverage - policy type unknown'
            }
        
        # Check coverage
        claim_amount = extracted_info.get('claim_amount', 0)
        coverage_check = self._check_coverage(claim_amount, policy_info)
        
        # Build enriched result
        enriched = {
            'extracted_info': extracted_info,
            'policy_type': policy_type,
            'policy_context': {
                'coverage_limits': policy_info['coverage_limits'],
                'deductibles': policy_info['deductibles'],
                'exclusions': policy_info['exclusions'],
                'required_documentation': policy_info['required_documentation']
            },
            'coverage_check': coverage_check
        }
        
        return enriched
    
    def _check_coverage(self, claim_amount, policy_info):
        """Check if claim amount is within coverage limits"""
        coverage_limits = policy_info['coverage_limits']
        
        # Get the maximum coverage limit
        max_coverage = max(coverage_limits.values())
        
        if claim_amount <= max_coverage:
            return f"✓ Claim amount ${claim_amount:,.2f} is within coverage limits (max: ${max_coverage:,.2f})"
        else:
            return f"⚠ Claim amount ${claim_amount:,.2f} exceeds maximum coverage of ${max_coverage:,.2f}"
    
    def build_enriched_prompt(self, claim_text, extracted_info):
        """
        Build an enriched prompt with policy context for better AI analysis
        
        Args:
            claim_text: Original claim document text
            extracted_info: Extracted claim information
        
        Returns:
            str: Enriched prompt with policy context
        """
        enriched = self.enrich_claim_with_policy(claim_text, extracted_info)
        
        policy_context = enriched['policy_context']
        if not policy_context:
            return f"""Analyze this insurance claim:

Claim Information:
{json.dumps(extracted_info, indent=2)}

Original Document:
{claim_text}

Analysis:"""
        
        prompt = f"""Analyze this {enriched['policy_type']} insurance claim with the following policy context:

POLICY INFORMATION:
Coverage Limits: {json.dumps(policy_context['coverage_limits'], indent=2)}
Deductibles: {json.dumps(policy_context['deductibles'], indent=2)}
Exclusions: {', '.join(policy_context['exclusions'])}
Required Documentation: {', '.join(policy_context['required_documentation'])}

CLAIM INFORMATION:
{json.dumps(extracted_info, indent=2)}

COVERAGE CHECK:
{enriched['coverage_check']}

ORIGINAL DOCUMENT:
{claim_text}

Provide a detailed analysis including:
1. Coverage assessment
2. Potential exclusions that may apply
3. Missing documentation
4. Recommended next steps

Analysis:"""
        
        return prompt


# Test the knowledge base
if __name__ == "__main__":
    print("="*60)
    print("Testing Policy Knowledge Base")
    print("="*60)
    
    kb = PolicyKnowledgeBase()
    
    # Test 1: Load policies
    print(f"\n✓ Loaded {len(kb.policies)} policy types")
    
    # Test 2: Get auto policy
    print("\n--- Auto Policy Information ---")
    auto_policy = kb.get_policy_info('auto')
    if auto_policy:
        print(json.dumps(auto_policy, indent=2))
    
    # Test 3: Detect policy type
    print("\n--- Policy Type Detection ---")
    test_claim = "Vehicle collision on highway, front bumper damaged"
    test_extracted = {
        'claimant_name': 'John Doe',
        'policy_number': 'AUTO-12345',
        'incident_date': '2024-01-15',
        'claim_amount': 3500,
        'incident_description': test_claim
    }
    
    detected_type = kb.detect_policy_type(test_claim, test_extracted)
    print(f"Detected policy type: {detected_type}")
    
    # Test 4: Enrich claim
    print("\n--- Enriched Claim ---")
    enriched = kb.enrich_claim_with_policy(test_claim, test_extracted)
    print(json.dumps(enriched, indent=2))
    
    print("\n" + "="*60)
    print("✓ Knowledge Base Tests Complete!")
    print("="*60)
