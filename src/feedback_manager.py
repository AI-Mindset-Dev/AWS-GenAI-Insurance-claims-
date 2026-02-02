"""
Feedback Manager for Claim Processing
Tracks accuracy ratings and collects improvement feedback
"""

import json
import os
from datetime import datetime

class FeedbackManager:
    """Manages user feedback and accuracy tracking"""
    
    def __init__(self, feedback_file='feedback_data.json'):
        """Initialize feedback manager"""
        self.feedback_file = feedback_file
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self):
        """Load existing feedback from file"""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'submissions': [], 'stats': {}}
        return {'submissions': [], 'stats': {}}
    
    def _save_feedback(self):
        """Save feedback to file"""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_data, indent=2, fp=f)
    
    def submit_feedback(self, document_name, rating, extraction_accurate, 
                       summary_quality, comments='', model_used=''):
        """
        Submit feedback for a processed claim
        
        Args:
            document_name: Name of the processed document
            rating: Overall rating (1-5)
            extraction_accurate: Was extraction accurate? (True/False)
            summary_quality: Summary quality rating (1-5)
            comments: Optional user comments
            model_used: Which model was used
        
        Returns:
            dict: Feedback submission confirmation
        """
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'document_name': document_name,
            'rating': rating,
            'extraction_accurate': extraction_accurate,
            'summary_quality': summary_quality,
            'comments': comments,
            'model_used': model_used
        }
        
        self.feedback_data['submissions'].append(feedback_entry)
        self._update_stats()
        self._save_feedback()
        
        return {
            'success': True,
            'message': 'Feedback submitted successfully',
            'total_submissions': len(self.feedback_data['submissions'])
        }
    
    def _update_stats(self):
        """Update aggregate statistics"""
        submissions = self.feedback_data['submissions']
        
        if not submissions:
            self.feedback_data['stats'] = {}
            return
        
        # Calculate averages
        total = len(submissions)
        avg_rating = sum(s['rating'] for s in submissions) / total
        avg_summary_quality = sum(s['summary_quality'] for s in submissions) / total
        extraction_accuracy = sum(1 for s in submissions if s['extraction_accurate']) / total * 100
        
        # Count by rating
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[str(i)] = sum(1 for s in submissions if s['rating'] == i)
        
        # Model performance
        model_stats = {}
        for submission in submissions:
            model = submission.get('model_used', 'unknown')
            if model not in model_stats:
                model_stats[model] = {
                    'count': 0,
                    'avg_rating': 0,
                    'ratings': []
                }
            model_stats[model]['count'] += 1
            model_stats[model]['ratings'].append(submission['rating'])
        
        # Calculate model averages
        for model in model_stats:
            ratings = model_stats[model]['ratings']
            model_stats[model]['avg_rating'] = sum(ratings) / len(ratings)
            del model_stats[model]['ratings']  # Remove raw ratings
        
        self.feedback_data['stats'] = {
            'total_submissions': total,
            'average_rating': round(avg_rating, 2),
            'average_summary_quality': round(avg_summary_quality, 2),
            'extraction_accuracy_percent': round(extraction_accuracy, 1),
            'rating_distribution': rating_distribution,
            'model_performance': model_stats,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_stats(self):
        """Get current statistics"""
        return self.feedback_data['stats']
    
    def get_recent_feedback(self, limit=10):
        """Get recent feedback submissions"""
        submissions = self.feedback_data['submissions']
        return submissions[-limit:] if len(submissions) > limit else submissions
    
    def get_feedback_summary(self):
        """Get a formatted summary of feedback"""
        stats = self.get_stats()
        
        if not stats:
            return "No feedback submitted yet"
        
        summary = f"""
Feedback Summary
================
Total Submissions: {stats['total_submissions']}
Average Rating: {stats['average_rating']}/5.0 ⭐
Extraction Accuracy: {stats['extraction_accuracy_percent']}%
Summary Quality: {stats['average_summary_quality']}/5.0

Rating Distribution:
"""
        for rating, count in stats['rating_distribution'].items():
            stars = '⭐' * int(rating)
            summary += f"  {stars} ({rating}): {count} submissions\n"
        
        if stats.get('model_performance'):
            summary += "\nModel Performance:\n"
            for model, perf in stats['model_performance'].items():
                summary += f"  {model}: {perf['avg_rating']:.2f}/5.0 ({perf['count']} uses)\n"
        
        return summary
    
    def export_feedback(self, output_file='feedback_export.json'):
        """Export all feedback data"""
        with open(output_file, 'w') as f:
            json.dump(self.feedback_data, indent=2, fp=f)
        return f"Feedback exported to {output_file}"


# Test the feedback manager
if __name__ == "__main__":
    print("="*60)
    print("Testing Feedback Manager")
    print("="*60)
    
    fm = FeedbackManager('test_feedback.json')
    
    # Test 1: Submit feedback
    print("\n--- Test 1: Submit Feedback ---")
    result = fm.submit_feedback(
        document_name='claim_1_auto_accident.txt',
        rating=5,
        extraction_accurate=True,
        summary_quality=5,
        comments='Excellent extraction and summary!',
        model_used='claude-3-sonnet'
    )
    print(f"✓ {result['message']}")
    
    # Test 2: Submit more feedback
    print("\n--- Test 2: Submit More Feedback ---")
    fm.submit_feedback('claim_2_property_damage.txt', 4, True, 4, 'Good but could be better', 'claude-3-haiku')
    fm.submit_feedback('claim_3_medical.txt', 5, True, 5, 'Perfect!', 'claude-3-sonnet')
    fm.submit_feedback('claim_1_auto_accident.txt', 3, False, 3, 'Missed some details', 'claude-3-haiku')
    print("✓ Submitted 3 more feedback entries")
    
    # Test 3: Get stats
    print("\n--- Test 3: Statistics ---")
    stats = fm.get_stats()
    print(json.dumps(stats, indent=2))
    
    # Test 4: Get summary
    print("\n--- Test 4: Feedback Summary ---")
    print(fm.get_feedback_summary())
    
    # Test 5: Recent feedback
    print("\n--- Test 5: Recent Feedback ---")
    recent = fm.get_recent_feedback(limit=3)
    for entry in recent:
        print(f"  - {entry['document_name']}: {entry['rating']}/5 ⭐")
    
    # Cleanup test file
    if os.path.exists('test_feedback.json'):
        os.remove('test_feedback.json')
    
    print("\n" + "="*60)
    print("✓ Feedback Manager Tests Complete!")
    print("="*60)
