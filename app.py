"""
Flask Web Interface for Insurance Claim Processor
Simple UI to upload documents and view results
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from src.document_processor import process_claim_document, bucket_name, s3_client, get_document_from_s3
from src.knowledge_base import PolicyKnowledgeBase
from src.content_filter import ContentFilter
from src.feedback_manager import FeedbackManager
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize knowledge base, content filter, and feedback manager
kb = PolicyKnowledgeBase()
content_filter = ContentFilter()
feedback_manager = FeedbackManager()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page with upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process claim"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: txt, pdf, doc, docx'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Upload to S3
        s3_key = f'uploads/{filename}'
        file_content = file.read()
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file_content
        )
        
        # Process the claim
        result = process_claim_document(bucket_name, s3_key)
        
        # Get document text for enrichment and filtering
        document_text = get_document_from_s3(bucket_name, s3_key)
        
        # Check for PII
        safety_report = content_filter.validate_claim_safety(document_text)
        
        # Enrich with policy information
        enriched = kb.enrich_claim_with_policy(document_text, result['extracted_info'])
        
        return jsonify({
            'success': True,
            'filename': filename,
            'extracted_info': result['extracted_info'],
            'summary': result['summary'],
            'policy_type': enriched['policy_type'],
            'policy_context': enriched['policy_context'],
            'coverage_check': enriched['coverage_check'],
            'pii_detection': {
                'risk_level': safety_report['risk_level'],
                'total_pii_found': safety_report['total_pii_found'],
                'recommendation': safety_report['recommendation'],
                'detections': safety_report['detections']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sample/<int:sample_id>')
def process_sample(sample_id):
    """Process one of the sample documents"""
    samples = [
        'sample_documents/claim_1_auto_accident.txt',
        'sample_documents/claim_2_property_damage.txt',
        'sample_documents/claim_3_medical.txt'
    ]
    
    if sample_id < 1 or sample_id > len(samples):
        return jsonify({'error': 'Invalid sample ID'}), 400
    
    try:
        result = process_claim_document(bucket_name, samples[sample_id - 1])
        
        # Get document text for enrichment and filtering
        document_text = get_document_from_s3(bucket_name, samples[sample_id - 1])
        
        # Check for PII
        safety_report = content_filter.validate_claim_safety(document_text)
        
        # Enrich with policy information
        enriched = kb.enrich_claim_with_policy(document_text, result['extracted_info'])
        
        return jsonify({
            'success': True,
            'filename': samples[sample_id - 1].split('/')[-1],
            'extracted_info': result['extracted_info'],
            'summary': result['summary'],
            'policy_type': enriched['policy_type'],
            'policy_context': enriched['policy_context'],
            'coverage_check': enriched['coverage_check'],
            'pii_detection': {
                'risk_level': safety_report['risk_level'],
                'total_pii_found': safety_report['total_pii_found'],
                'recommendation': safety_report['recommendation'],
                'detections': safety_report['detections']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback submission"""
    try:
        data = request.json
        
        result = feedback_manager.submit_feedback(
            document_name=data.get('document_name'),
            rating=data.get('rating'),
            extraction_accurate=data.get('extraction_accurate'),
            summary_quality=data.get('summary_quality'),
            comments=data.get('comments', ''),
            model_used=data.get('model_used', 'claude-3-sonnet')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback/stats')
def get_feedback_stats():
    """Get feedback statistics"""
    try:
        stats = feedback_manager.get_stats()
        return jsonify(stats if stats else {'message': 'No feedback yet'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Starting Insurance Claim Processor Web Interface")
    print("="*70)
    print("\n📍 Open your browser to: http://localhost:5000")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
