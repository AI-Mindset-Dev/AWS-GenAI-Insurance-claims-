"""
Content Filter for PII Detection and Masking
Protects sensitive information in insurance claims
"""

import re
import json

class ContentFilter:
    """Detects and masks personally identifiable information (PII)"""
    
    def __init__(self):
        """Initialize PII detection patterns"""
        self.patterns = {
            'ssn': {
                'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
                'mask': 'XXX-XX-XXXX',
                'description': 'Social Security Number'
            },
            'phone': {
                'pattern': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                'mask': 'XXX-XXX-XXXX',
                'description': 'Phone Number'
            },
            'email': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'mask': '[EMAIL_REDACTED]',
                'description': 'Email Address'
            },
            'credit_card': {
                'pattern': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                'mask': 'XXXX-XXXX-XXXX-XXXX',
                'description': 'Credit Card Number'
            },
            'address': {
                'pattern': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir)\b',
                'mask': '[ADDRESS_REDACTED]',
                'description': 'Street Address'
            },
            'zip_code': {
                'pattern': r'\b\d{5}(?:-\d{4})?\b',
                'mask': 'XXXXX',
                'description': 'ZIP Code'
            },
            'date_of_birth': {
                'pattern': r'\b(?:DOB|Date of Birth|Born):?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                'mask': 'DOB: XX/XX/XXXX',
                'description': 'Date of Birth'
            }
        }
    
    def detect_pii(self, text):
        """
        Detect PII in text without masking
        
        Args:
            text: Text to scan for PII
        
        Returns:
            dict: Detection results with counts and locations
        """
        detections = {}
        
        for pii_type, config in self.patterns.items():
            matches = re.finditer(config['pattern'], text, re.IGNORECASE)
            found = list(matches)
            
            if found:
                detections[pii_type] = {
                    'count': len(found),
                    'description': config['description'],
                    'samples': [match.group() for match in found[:3]]  # First 3 samples
                }
        
        return detections
    
    def mask_pii(self, text, pii_types=None):
        """
        Mask PII in text
        
        Args:
            text: Text to mask
            pii_types: List of PII types to mask (None = mask all)
        
        Returns:
            tuple: (masked_text, mask_report)
        """
        masked_text = text
        mask_report = {}
        
        # Determine which types to mask
        types_to_mask = pii_types if pii_types else self.patterns.keys()
        
        for pii_type in types_to_mask:
            if pii_type not in self.patterns:
                continue
            
            config = self.patterns[pii_type]
            matches = re.finditer(config['pattern'], masked_text, re.IGNORECASE)
            found = list(matches)
            
            if found:
                # Replace matches with mask
                masked_text = re.sub(config['pattern'], config['mask'], masked_text, flags=re.IGNORECASE)
                
                mask_report[pii_type] = {
                    'count': len(found),
                    'description': config['description'],
                    'masked_with': config['mask']
                }
        
        return masked_text, mask_report
    
    def validate_claim_safety(self, claim_text):
        """
        Validate if claim contains sensitive information that should be masked
        
        Args:
            claim_text: Claim document text
        
        Returns:
            dict: Safety validation report
        """
        detections = self.detect_pii(claim_text)
        
        # Determine risk level
        high_risk_types = ['ssn', 'credit_card', 'date_of_birth']
        medium_risk_types = ['phone', 'email', 'address']
        
        high_risk_count = sum(detections.get(t, {}).get('count', 0) for t in high_risk_types)
        medium_risk_count = sum(detections.get(t, {}).get('count', 0) for t in medium_risk_types)
        
        if high_risk_count > 0:
            risk_level = 'HIGH'
            recommendation = 'Mask all PII before processing or storing'
        elif medium_risk_count > 0:
            risk_level = 'MEDIUM'
            recommendation = 'Consider masking PII for privacy compliance'
        else:
            risk_level = 'LOW'
            recommendation = 'No sensitive PII detected'
        
        return {
            'risk_level': risk_level,
            'recommendation': recommendation,
            'detections': detections,
            'total_pii_found': sum(d.get('count', 0) for d in detections.values())
        }
    
    def process_claim_with_filtering(self, claim_text, auto_mask=True):
        """
        Process claim with automatic PII filtering
        
        Args:
            claim_text: Original claim text
            auto_mask: Whether to automatically mask detected PII
        
        Returns:
            dict: Processed claim with filtering report
        """
        # Validate safety
        safety_report = self.validate_claim_safety(claim_text)
        
        # Mask if needed
        if auto_mask and safety_report['total_pii_found'] > 0:
            masked_text, mask_report = self.mask_pii(claim_text)
        else:
            masked_text = claim_text
            mask_report = {}
        
        return {
            'original_text': claim_text,
            'filtered_text': masked_text,
            'safety_report': safety_report,
            'mask_report': mask_report,
            'was_filtered': len(mask_report) > 0
        }


# Test the content filter
if __name__ == "__main__":
    print("="*60)
    print("Testing Content Filter")
    print("="*60)
    
    filter = ContentFilter()
    
    # Test 1: Detect PII
    print("\n--- Test 1: PII Detection ---")
    test_text = """
    Claimant: John Doe
    SSN: 123-45-6789
    Phone: 555-123-4567
    Email: john.doe@example.com
    Address: 123 Main Street, Anytown
    ZIP: 12345
    DOB: 01/15/1980
    Credit Card: 4532-1234-5678-9010
    """
    
    detections = filter.detect_pii(test_text)
    print(f"Found {len(detections)} types of PII:")
    for pii_type, info in detections.items():
        print(f"  - {info['description']}: {info['count']} occurrence(s)")
        print(f"    Samples: {', '.join(info['samples'])}")
    
    # Test 2: Mask PII
    print("\n--- Test 2: PII Masking ---")
    masked_text, mask_report = filter.mask_pii(test_text)
    print("Masked text:")
    print(masked_text)
    print("\nMask report:")
    print(json.dumps(mask_report, indent=2))
    
    # Test 3: Safety validation
    print("\n--- Test 3: Safety Validation ---")
    safety = filter.validate_claim_safety(test_text)
    print(f"Risk Level: {safety['risk_level']}")
    print(f"Recommendation: {safety['recommendation']}")
    print(f"Total PII Found: {safety['total_pii_found']}")
    
    # Test 4: Process with filtering
    print("\n--- Test 4: Complete Processing ---")
    result = filter.process_claim_with_filtering(test_text, auto_mask=True)
    print(f"Was Filtered: {result['was_filtered']}")
    print(f"PII Types Masked: {len(result['mask_report'])}")
    
    print("\n" + "="*60)
    print("✓ Content Filter Tests Complete!")
    print("="*60)
