"""
Model Performance Comparator
Compares different Bedrock models on the same task
"""

import time
import json
from document_processor import get_document_from_s3, build_extraction_prompt, invoke_bedrock_model, bucket_name


class ModelComparator:
    """Compares performance of different Bedrock models"""
    
    def __init__(self):
        """Initialize with list of models to test"""
        # Models available in us-east-1 (Claude 3 family)
        self.models = [
            'anthropic.claude-3-sonnet-20240229-v1:0',  # Most accurate
            'anthropic.claude-3-haiku-20240307-v1:0',   # Fastest
        ]
    
    def compare_models(self, bucket_name, document_key, temperature=0.0):
        """
        Compare all models on the same document
        
        Args:
            bucket_name (str): S3 bucket name
            document_key (str): S3 document key
            temperature (float): Model temperature setting
            
        Returns:
            dict: Comparison results for all models
        """
        print(f"\n{'='*70}")
        print(f"MODEL COMPARISON: {document_key}")
        print(f"{'='*70}\n")
        
        # Retrieve document once
        print("Retrieving document from S3...")
        document_text = get_document_from_s3(bucket_name, document_key)
        prompt = build_extraction_prompt(document_text)
        print(f"✓ Document retrieved ({len(document_text)} chars)\n")
        
        results = []
        
        for i, model_id in enumerate(self.models, 1):
            print(f"[{i}/{len(self.models)}] Testing: {model_id}")
            
            result = {
                'model_id': model_id,
                'success': False,
                'execution_time': 0,
                'output_length': 0,
                'json_valid': False,
                'error': None,
                'output': None
            }
            
            try:
                # Measure execution time
                start_time = time.time()
                output = invoke_bedrock_model(prompt, model_id, temperature)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                # Record metrics
                result['success'] = True
                result['execution_time'] = round(execution_time, 2)
                result['output_length'] = len(output)
                result['output'] = output
                
                # Test JSON validity
                try:
                    # Try to parse as JSON
                    parsed = json.loads(output)
                    result['json_valid'] = True
                    print(f"  ✓ Success in {execution_time:.2f}s | Output: {len(output)} chars | JSON: Valid")
                except json.JSONDecodeError:
                    # Try to extract JSON from text
                    import re
                    json_match = re.search(r'\{.*\}', output, re.DOTALL)
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group())
                            result['json_valid'] = True
                            print(f"  ✓ Success in {execution_time:.2f}s | Output: {len(output)} chars | JSON: Valid (extracted)")
                        except:
                            result['json_valid'] = False
                            print(f"  ✓ Success in {execution_time:.2f}s | Output: {len(output)} chars | JSON: Invalid")
                    else:
                        result['json_valid'] = False
                        print(f"  ✓ Success in {execution_time:.2f}s | Output: {len(output)} chars | JSON: Invalid")
                
            except Exception as e:
                result['error'] = str(e)
                print(f"  ✗ Failed: {e}")
            
            results.append(result)
            print()
        
        return {
            'document_key': document_key,
            'models_tested': len(self.models),
            'results': results
        }
    
    def print_summary(self, comparison_results):
        """Print a formatted summary of comparison results"""
        print(f"\n{'='*70}")
        print("COMPARISON SUMMARY")
        print(f"{'='*70}\n")
        
        results = comparison_results['results']
        
        # Find fastest and slowest
        successful = [r for r in results if r['success']]
        if successful:
            fastest = min(successful, key=lambda x: x['execution_time'])
            slowest = max(successful, key=lambda x: x['execution_time'])
            
            print(f"Document: {comparison_results['document_key']}")
            print(f"Models Tested: {comparison_results['models_tested']}")
            print(f"Successful: {len(successful)}/{len(results)}\n")
            
            print("Performance Ranking (fastest to slowest):")
            sorted_results = sorted(successful, key=lambda x: x['execution_time'])
            for i, result in enumerate(sorted_results, 1):
                model_name = result['model_id'].split('.')[-1]
                json_status = "✓" if result['json_valid'] else "✗"
                print(f"  {i}. {model_name:30s} | {result['execution_time']:5.2f}s | JSON: {json_status}")
            
            print(f"\n🏆 Fastest: {fastest['model_id'].split('.')[-1]} ({fastest['execution_time']:.2f}s)")
            print(f"🐌 Slowest: {slowest['model_id'].split('.')[-1]} ({slowest['execution_time']:.2f}s)")
            
            speed_diff = slowest['execution_time'] - fastest['execution_time']
            print(f"⚡ Speed difference: {speed_diff:.2f}s ({(speed_diff/slowest['execution_time']*100):.1f}% faster)")
        
        # Show failures
        failed = [r for r in results if not r['success']]
        if failed:
            print(f"\n❌ Failed Models:")
            for result in failed:
                print(f"  - {result['model_id']}: {result['error']}")
        
        print(f"\n{'='*70}\n")


# Test the Model Comparator
if __name__ == "__main__":
    print("Testing Model Comparator\n")
    
    comparator = ModelComparator()
    
    # Test with first sample document
    test_key = 'sample_documents/claim_1_auto_accident.txt'
    
    try:
        results = comparator.compare_models(bucket_name, test_key, temperature=0.0)
        comparator.print_summary(results)
        
        print("✓ Model Comparator test complete!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
