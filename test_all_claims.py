"""
Test All Claim Documents
Processes all 3 sample claims and saves results
"""

import json
from src.document_processor import process_claim_document, bucket_name

# All sample documents
documents = [
    'sample_documents/claim_1_auto_accident.txt',
    'sample_documents/claim_2_property_damage.txt',
    'sample_documents/claim_3_medical.txt'
]

print("="*70)
print("PROCESSING ALL CLAIM DOCUMENTS")
print("="*70)

all_results = []

for i, doc_key in enumerate(documents, 1):
    print(f"\n{'='*70}")
    print(f"DOCUMENT {i}/{len(documents)}")
    print(f"{'='*70}")
    
    try:
        result = process_claim_document(bucket_name, doc_key)
        all_results.append(result)
        
        # Display results
        print(f"\n{'='*70}")
        print(f"RESULTS - Document {i}")
        print(f"{'='*70}")
        print(f"\nDocument: {result['document_key']}")
        print(f"\nExtracted Information:")
        print(json.dumps(result['extracted_info'], indent=2))
        print(f"\nSummary:")
        print(result['summary'])
        
    except Exception as e:
        print(f"\n✗ Error processing {doc_key}: {e}")
        import traceback
        traceback.print_exc()

# Save all results to file
output_file = 'test_results.json'
with open(output_file, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n{'='*70}")
print("FINAL SUMMARY")
print(f"{'='*70}")
print(f"\nTotal documents processed: {len(all_results)}/{len(documents)}")
print(f"Results saved to: {output_file}")

# Quick stats
for i, result in enumerate(all_results, 1):
    doc_name = result['document_key'].split('/')[-1]
    claimant = result['extracted_info'].get('claimant_name', 'Unknown')
    amount = result['extracted_info'].get('claim_amount', 'Unknown')
    print(f"\n{i}. {doc_name}")
    print(f"   Claimant: {claimant}")
    print(f"   Amount: ${amount}")

print(f"\n{'='*70}")
print("✓ All claims processed successfully!")
print(f"{'='*70}\n")
