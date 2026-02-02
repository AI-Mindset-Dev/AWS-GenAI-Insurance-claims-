"""
Insurance Claim Document Processor
Processes insurance claim documents using AWS Bedrock AI models
"""

# TODO: Challenge 1.1 - Initialize AWS Clients
# Challenge 1.1: Initialize AWS Clients
import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Simple approach: load_dotenv() searches parent directories automatically
load_dotenv()

# Get configuration from environment variables
aws_region = os.getenv('AWS_REGION')
bucket_name = os.getenv('AWS_BUCKET_NAME')

# Display loaded configuration
if aws_region:
    print(f"✓ Loaded AWS_REGION: {aws_region}")
else:
    aws_region = 'af-south-1'
    print(f"⚠ AWS_REGION not found, using default: {aws_region}")

if bucket_name:
    print(f"✓ Loaded AWS_BUCKET_NAME: {bucket_name}")
else:
    print(f"✗ AWS_BUCKET_NAME not found in .env file")
    print(f"✗ Make sure .env file exists in project root with:")
    print(f"   AWS_BUCKET_NAME=claim-documents-poc-awm")
    print(f"   AWS_REGION=af-south-1")
    exit(1)

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=aws_region)
# Use us-east-1 for Bedrock (better model availability)
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

print("✓ AWS clients initialized successfully!")
print(f"✓ S3 client: {s3_client}")
print(f"✓ Bedrock client: {bedrock_client}")


# Challenge 1.2: Retrieve Document from S3
def get_document_from_s3(bucket_name, document_key):
    """Retrieve document from S3 bucket"""
    response = s3_client.get_object(Bucket=bucket_name, Key=document_key)
    document_text = response['Body'].read().decode('utf-8')
    return document_text


# Challenge 1.3: Build Extraction Prompt
def build_extraction_prompt(document_text):
    """Build prompt for extracting claim information"""
    prompt = f"""You are an insurance claim processor. Extract the following information from the claim document below and return ONLY valid JSON with these exact fields:

- claimant_name (string)
- policy_number (string)
- incident_date (string in YYYY-MM-DD format)
- claim_amount (number only, no currency symbols)
- incident_description (string)

Return ONLY the JSON object, no other text.

Claim Document:
{document_text}

JSON Output:"""
    return prompt


# Challenge 1.4: Invoke Bedrock Model
def invoke_bedrock_model(prompt, model_id, temperature=0.0):
    """Invoke Bedrock model with the given prompt"""
    # Build request body for Claude models
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    # Invoke the model
    response = bedrock_client.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    response_text = response_body['content'][0]['text']
    
    return response_text


# Challenge 1.5: Complete Pipeline
def process_claim_document(bucket_name, document_key):
    """Complete processing pipeline: retrieve, extract, and summarize"""
    print(f"\n{'='*60}")
    print(f"Processing: {document_key}")
    print(f"{'='*60}")
    
    # Step 1: Retrieve document from S3
    print("\n[1/3] Retrieving document from S3...")
    document_text = get_document_from_s3(bucket_name, document_key)
    print(f"✓ Retrieved {len(document_text)} characters")
    
    # Step 2: Extract information (temperature=0.0 for consistency)
    print("\n[2/3] Extracting claim information...")
    extraction_prompt = build_extraction_prompt(document_text)
    extraction_model = 'anthropic.claude-3-sonnet-20240229-v1:0'  # Sonnet for accuracy
    
    extraction_result = invoke_bedrock_model(extraction_prompt, extraction_model, temperature=0.0)
    print(f"✓ Extraction complete")
    
    # Parse JSON from extraction
    try:
        extracted_info = json.loads(extraction_result)
    except json.JSONDecodeError:
        # If model returns text with JSON, try to extract it
        import re
        json_match = re.search(r'\{.*\}', extraction_result, re.DOTALL)
        if json_match:
            extracted_info = json.loads(json_match.group())
        else:
            extracted_info = {"error": "Failed to parse JSON", "raw": extraction_result}
    
    # Step 3: Generate summary (temperature=0.7 for creativity)
    print("\n[3/3] Generating summary...")
    summary_prompt = f"""Summarize this insurance claim in 2-3 sentences for a claims adjuster:

Claim Information:
{json.dumps(extracted_info, indent=2)}

Original Document:
{document_text}

Summary:"""
    
    summary_model = 'anthropic.claude-3-haiku-20240307-v1:0'  # Haiku for speed
    summary = invoke_bedrock_model(summary_prompt, summary_model, temperature=0.7)
    print(f"✓ Summary generated")
    
    # Return complete results
    result = {
        'document_key': document_key,
        'extracted_info': extracted_info,
        'summary': summary.strip()
    }
    
    return result


# Test Complete Pipeline (Challenge 1.5)
if __name__ == "__main__":
    test_key = 'sample_documents/claim_1_auto_accident.txt'
    
    try:
        # Run the complete pipeline
        result = process_claim_document(bucket_name, test_key)
        
        # Display results
        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}")
        print(f"\nDocument: {result['document_key']}")
        print(f"\nExtracted Information:")
        print(json.dumps(result['extracted_info'], indent=2))
        print(f"\nSummary:")
        print(result['summary'])
        print(f"\n{'='*60}")
        print("✓ Challenge 1.5 Complete!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

