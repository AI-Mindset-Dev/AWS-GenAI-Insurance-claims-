"""
Prompt Template Manager
Manages reusable prompt templates with variable substitution
"""


class PromptTemplateManager:
    """Manages prompt templates for different AI tasks"""
    
    def __init__(self):
        """Initialize with predefined prompt templates"""
        self.templates = {
            'extract_info': """You are an insurance claim processor. Extract the following information from the claim document below and return ONLY valid JSON with these exact fields:

- claimant_name (string)
- policy_number (string)
- incident_date (string in YYYY-MM-DD format)
- claim_amount (number only, no currency symbols)
- incident_description (string)

Return ONLY the JSON object, no other text.

Claim Document:
{document_text}

JSON Output:""",
            
            'generate_summary': """Summarize this insurance claim in 2-3 sentences for a claims adjuster:

Claim Information:
{claim_info}

Original Document:
{document_text}

Summary:""",
            
            'policy_lookup': """Based on the following claim information, identify the relevant policy coverage and any potential issues:

Claim Information:
{claim_info}

Policy Number: {policy_number}

Analysis:"""
        }
    
    def get_prompt(self, template_name, **kwargs):
        """
        Retrieve and format a prompt template with variables
        
        Args:
            template_name (str): Name of the template to retrieve
            **kwargs: Variables to substitute in the template
            
        Returns:
            str: Formatted prompt with variables substituted
            
        Raises:
            ValueError: If template_name doesn't exist
        """
        if template_name not in self.templates:
            available = ', '.join(self.templates.keys())
            raise ValueError(f"Template '{template_name}' not found. Available templates: {available}")
        
        template = self.templates[template_name]
        
        try:
            formatted_prompt = template.format(**kwargs)
            return formatted_prompt
        except KeyError as e:
            raise ValueError(f"Missing required variable {e} for template '{template_name}'")
    
    def list_templates(self):
        """Return list of available template names"""
        return list(self.templates.keys())
    
    def add_template(self, name, template):
        """Add a new template to the manager"""
        self.templates[name] = template
        print(f"✓ Added template: {name}")


# Test the Prompt Template Manager
if __name__ == "__main__":
    print("Testing Prompt Template Manager\n")
    
    # Create manager
    manager = PromptTemplateManager()
    
    # Test 1: List available templates
    print("Available templates:")
    for template in manager.list_templates():
        print(f"  - {template}")
    
    # Test 2: Get extraction prompt
    print("\n--- Test 1: Extract Info Template ---")
    try:
        prompt = manager.get_prompt('extract_info', document_text="Sample claim document...")
        print(f"✓ Template retrieved successfully")
        print(f"✓ Prompt length: {len(prompt)} characters")
        print(f"✓ First 100 chars: {prompt[:100]}...")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Get summary prompt
    print("\n--- Test 2: Generate Summary Template ---")
    try:
        prompt = manager.get_prompt(
            'generate_summary',
            claim_info='{"claimant": "John Doe"}',
            document_text="Sample document..."
        )
        print(f"✓ Template retrieved successfully")
        print(f"✓ Prompt length: {len(prompt)} characters")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Missing template
    print("\n--- Test 3: Missing Template (should fail) ---")
    try:
        prompt = manager.get_prompt('nonexistent_template')
        print(f"✗ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly raised error: {e}")
    
    # Test 5: Missing variable
    print("\n--- Test 4: Missing Variable (should fail) ---")
    try:
        prompt = manager.get_prompt('extract_info')  # Missing document_text
        print(f"✗ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly raised error: {e}")
    
    # Test 6: Add custom template
    print("\n--- Test 5: Add Custom Template ---")
    manager.add_template('custom_test', "Hello {name}!")
    prompt = manager.get_prompt('custom_test', name="World")
    print(f"✓ Custom template works: {prompt}")
    
    print("\n" + "="*60)
    print("✓ All tests passed! Prompt Template Manager is working!")
    print("="*60)
