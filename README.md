# AI-Powered Insurance Claim Processor

> Built with AWS Bedrock, Claude 3, and Python | #awsexamprep

An enterprise-ready insurance claim processing system that uses AWS Bedrock's Claude 3 models to automatically extract structured information from claim documents and generate human-readable summaries. Features include RAG-based policy enrichment, PII detection, and a production web interface.

![Project Demo](https://img.shields.io/badge/AWS-Bedrock-orange) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Flask](https://img.shields.io/badge/Flask-Web_UI-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Project Overview

This project demonstrates practical AWS Bedrock integration for document processing and GenAI applications. Built as part of AWS certification preparation, it showcases:

- **AWS Bedrock** integration with Claude 3 models
- **Prompt engineering** for structured data extraction
- **Model comparison** (Haiku vs Sonnet performance analysis)
- **RAG implementation** with policy knowledge base
- **PII detection** for privacy compliance
- **Production web interface** with Flask

## 🚀 Key Features

### Core Functionality
- ✅ **Automated Extraction**: Extracts claimant name, policy number, incident date, claim amount, and description
- ✅ **AI Summarization**: Generates natural language summaries for claims adjusters
- ✅ **S3 Integration**: Retrieves documents from AWS S3 buckets
- ✅ **JSON Output**: Structured, parseable data for downstream systems

### Bonus Features
- 🌐 **Web Interface**: Beautiful Flask UI with drag-and-drop upload
- 📚 **RAG Knowledge Base**: Policy-aware processing with coverage validation
- 🔒 **PII Detection**: Automatic detection of sensitive information (SSN, credit cards, etc.)
- ⭐ **Feedback System**: User ratings and analytics for continuous improvement

## 📊 Performance Results

| Metric | Claude 3 Haiku | Claude 3 Sonnet |
|--------|----------------|-----------------|
| **Speed** | 1.65s (36% faster) | 2.58s |
| **Accuracy** | 100% JSON validity | 100% JSON validity |
| **Cost per claim** | $0.002 | $0.024 |
| **Recommendation** | ✅ **Optimal choice** | Use for complex edge cases |

**Key Finding**: Haiku delivers identical accuracy to Sonnet while being 36% faster and 92% cheaper!

## 🏗️ Architecture

```
User Upload → S3 Storage → AWS Bedrock (Claude 3)
                              ↓
                    Extract Info + Summary
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
            PII Detection      Knowledge Base (RAG)
            - Risk Level       - Policy Type Detection
            - Masking          - Coverage Validation
                    ↓                   ↓
                    └─────────┬─────────┘
                              ↓
                      Web UI Display
                              ↓
                      User Feedback & Analytics
```

## 🛠️ Tech Stack

- **Cloud**: AWS Bedrock, AWS S3
- **AI Models**: Claude 3 Haiku, Claude 3 Sonnet
- **Backend**: Python 3.8+, boto3, Flask
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Data**: JSON for structured output and knowledge base

## 📦 Installation

### Prerequisites
- AWS Account with Bedrock access
- Python 3.8 or higher
- AWS CLI configured with credentials

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/AI-Mindset-Dev/aws-genai-insurance-claims.git
cd aws-genai-insurance-claims
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Create .env file
echo "AWS_BUCKET_NAME=your-bucket-name" > .env
echo "AWS_REGION=us-east-1" >> .env
```

5. **Upload sample documents to S3**
```bash
aws s3 cp sample_documents/ s3://your-bucket-name/sample_documents/ --recursive
```

6. **Run the application**
```bash
# Test core functionality
python src/document_processor.py

# Start web interface
python app.py
```

7. **Open browser**
```
http://localhost:5000
```

## 📖 Usage

### Command Line
```python
from src.document_processor import process_claim_document

# Process a claim
result = process_claim_document(
    bucket_name='your-bucket',
    document_key='sample_documents/claim_1_auto_accident.txt'
)

print(result['extracted_info'])
print(result['summary'])
```

### Web Interface
1. Navigate to http://localhost:5000
2. Click a sample document button OR upload your own
3. View extracted information, policy context, and AI summary
4. Rate the results to help improve the system

### API Endpoints
- `GET /` - Web interface
- `POST /upload` - Upload and process document
- `GET /sample/<id>` - Process sample document (1-3)
- `POST /feedback` - Submit feedback
- `GET /feedback/stats` - View analytics

## 🧪 Testing

```bash
# Test document processor
python src/document_processor.py

# Test all sample documents
python test_all_claims.py

# Test model comparison
python src/model_comparator.py

# Test knowledge base
python src/knowledge_base.py

# Test PII detection
python src/content_filter.py

# Test feedback system
python src/feedback_manager.py
```

## 📁 Project Structure

```
aws-genai-insurance-claims/
├── src/
│   ├── document_processor.py    # Core Bedrock integration
│   ├── prompt_manager.py        # Template management
│   ├── model_comparator.py      # Performance testing
│   ├── knowledge_base.py        # RAG implementation
│   ├── content_filter.py        # PII detection
│   └── feedback_manager.py      # User feedback tracking
├── templates/
│   └── index.html               # Web UI
├── sample_documents/            # Test documents
├── app.py                       # Flask application
├── policy_knowledge_base.json   # Policy data for RAG
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── PROJECT-FINDINGS.md          # Detailed analysis
└── README.md                    # This file
```

## 💡 Key Learnings

### 1. Model Selection Matters
Don't assume bigger = better. Haiku matched Sonnet's accuracy for structured extraction while being significantly faster and cheaper.

### 2. Prompt Engineering is Critical
Small changes like "Return ONLY valid JSON" vs "Return JSON" improved success rate from 60% to 95%.

### 3. Temperature Tuning
- Use temperature=0.0 for structured extraction (deterministic)
- Use temperature=0.7 for summaries (creative but coherent)

### 4. Regional Considerations
Model availability varies by AWS region. us-east-1 has the best selection for Bedrock.

### 5. RAG Enhances Accuracy
Adding policy context reduced hallucinations and improved relevance of AI-generated summaries.

## 💰 Cost Analysis

**Development & Testing**: ~$0.15 total

**Production Estimates** (10,000 claims/month):
- Using Haiku: ~$20/month
- Using Sonnet: ~$240/month
- **Savings**: $220/month with Haiku

**ROI**: 2,500x cost reduction vs manual processing ($5/claim labor cost)

## 🔐 Security & Compliance

- ✅ PII detection for 7 sensitive data types
- ✅ Risk level assessment (HIGH/MEDIUM/LOW)
- ✅ Automatic masking capabilities
- ✅ HIPAA/GDPR compliance ready
- ✅ Audit trail for security reviews

## 🚀 Production Readiness

- ✅ Error handling at every layer
- ✅ Input validation and sanitization
- ✅ Secure file uploads (16MB limit)
- ✅ Modular architecture
- ✅ Comprehensive logging
- ✅ User feedback loop
- ✅ Analytics and monitoring

## 📈 Future Enhancements

- [ ] Multi-modal support (analyze damage photos with Claude Vision)
- [ ] Batch processing with SQS queue
- [ ] Real-time streaming for large documents
- [ ] Advanced RAG with vector database (Pinecone/Weaviate)
- [ ] A/B testing framework for prompt optimization
- [ ] Integration with claims management systems

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built as part of AWS Exam Prep certification preparation
- Uses AWS Bedrock and Anthropic's Claude 3 models
- Inspired by real-world insurance claim processing challenges

## 📞 Contact

**Aaron Meyer**
- LinkedIn: [linkedin.com/in/aaronwmeyer](https://linkedin.com/in/aaronwmeyer)
- GitHub: [@AI-Mindset-Dev](https://github.com/AI-Mindset-Dev)
- Project: [AWS GenAI Insurance Claims Processor](https://github.com/AI-Mindset-Dev/aws-genai-insurance-claims)

## 🏷️ Tags

`#awsexamprep` `#aws` `#bedrock` `#genai` `#claude3` `#python` `#machinelearning` `#ai` `#insurance` `#automation`

---

**⭐ If you found this project helpful, please give it a star!**

Built with ❤️ for the AWS community
