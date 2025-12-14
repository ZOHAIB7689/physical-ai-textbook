from typing import List, Dict, Any
from backend.src.services.translation_service import TranslationSetService
from backend.src.services.chapter_service import ChapterService
from backend.src.models.translation_set import TranslationSet
from sqlalchemy.orm import Session
import re


class TranslationQualityAssuranceService:
    """
    Service for ensuring translation quality through various checks and validations
    """
    
    def __init__(self):
        self.translation_service = TranslationSetService()
        self.chapter_service = ChapterService()
        # Define common quality checks
        self.quality_checks = [
            self._check_length_consistency,
            self._check_terminology_consistency,
            self._check_formatting_preservation,
            self._check_special_characters
        ]
    
    def run_quality_assurance(self, db: Session, translation_id: str) -> Dict[str, Any]:
        """
        Run quality assurance checks on a translation
        """
        translation = self.translation_service.get_translation_by_id(db, translation_id)
        if not translation:
            return {"error": "Translation not found"}
        
        # Get the original content for comparison
        original_content = self._get_original_content(db, translation)
        
        # Run all quality checks
        results = []
        for check in self.quality_checks:
            check_result = check(translation, original_content)
            results.append(check_result)
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(results)
        
        return {
            "translation_id": translation_id,
            "quality_score": quality_score,
            "checks": results,
            "status": "pass" if quality_score >= 80 else "review_needed"
        }
    
    def _get_original_content(self, db: Session, translation: TranslationSet) -> str:
        """
        Get the original content that was translated
        """
        if translation.entity_type == "chapter":
            chapter = self.chapter_service.get_chapter_by_id(db, translation.entity_id)
            if chapter and translation.language == "ur":
                return chapter.content  # Original is in English
            elif chapter and translation.language != "ur":
                # If the translation is not Urdu, we might have a different case
                return chapter.content
        # Add other entity types as needed
        
        return ""
    
    def _check_length_consistency(self, translation: TranslationSet, original: str) -> Dict[str, Any]:
        """
        Check if the translation length is reasonably consistent with the original
        """
        original_length = len(original) if original else 0
        translated_length = len(translation.translated_content)
        
        # In translation, content length can vary significantly, so we use a wide range
        if original_length == 0:
            return {
                "check_name": "length_consistency",
                "passed": translated_length < 1000,  # If original is empty, translation shouldn't be too long
                "score": 0 if translated_length >= 1000 else 100,
                "details": f"Original was empty, translation has {translated_length} characters"
            }
        
        # Calculate the ratio
        length_ratio = translated_length / original_length if original_length > 0 else 0
        
        # Reasonable range for translation length (0.5x to 2x of original)
        if 0.5 <= length_ratio <= 2.0:
            passed = True
            score = 100
            details = f"Length ratio is acceptable ({length_ratio:.2f}x)"
        else:
            passed = False
            score = max(0, 100 - abs(length_ratio - 1.0) * 100)  # Lower score based on deviation
            details = f"Length ratio is unusual ({length_ratio:.2f}x)"
        
        return {
            "check_name": "length_consistency",
            "passed": passed,
            "score": score,
            "details": details
        }
    
    def _check_terminology_consistency(self, translation: TranslationSet, original: str) -> Dict[str, Any]:
        """
        Check for consistent terminology in the translation
        """
        # Simple check: look for consistent use of key terms
        # In a real implementation, this would use a terminology database
        
        # For now, we'll check if any long words appear multiple times with different cases
        # which might indicate inconsistency
        content = translation.translated_content
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Find repeated words (potential terminology)
        word_count = {}
        for word in words:
            if len(word) > 5:  # Only consider longer words as potential terms
                word_count[word] = word_count.get(word, 0) + 1
        
        repeated_words = {word: count for word, count in word_count.items() if count > 2}
        
        passed = len(repeated_words) > 0  # Having repeated terms is good
        score = min(100, len(repeated_words) * 10)  # More repeated terms = higher score
        
        return {
            "check_name": "terminology_consistency",
            "passed": passed,
            "score": score,
            "details": f"Found {len(repeated_words)} commonly repeated terms"
        }
    
    def _check_formatting_preservation(self, translation: TranslationSet, original: str) -> Dict[str, Any]:
        """
        Check if formatting elements are preserved in the translation
        """
        # Simple check: count basic formatting elements in both original and translation
        # This is a simplified version - a full implementation would be more complex
        
        original_formatting_count = original.count('#') + original.count('*') + original.count('_') + original.count('**') + original.count('__')
        translated_formatting_count = translation.translated_content.count('#') + translation.translated_content.count('*') + translation.translated_content.count('_') + translation.translated_content.count('**') + translation.translated_content.count('__')
        
        # Check if formatting elements exist in both
        has_formatting = original_formatting_count > 0 or translated_formatting_count > 0
        
        if original_formatting_count == 0:
            # If original has no formatting, this check doesn't apply much
            passed = True
            score = 80  # Average score
            details = "Original had no formatting to preserve"
        elif abs(original_formatting_count - translated_formatting_count) <= 2:
            passed = True
            score = 100
            details = f"Formatting elements preserved ({original_formatting_count} vs {translated_formatting_count})"
        else:
            passed = False
            score = max(0, 80 - abs(original_formatting_count - translated_formatting_count) * 10)
            details = f"Formatting elements not preserved ({original_formatting_count} vs {translated_formatting_count})"
        
        return {
            "check_name": "formatting_preservation",
            "passed": passed,
            "score": score,
            "details": details
        }
    
    def _check_special_characters(self, translation: TranslationSet, original: str) -> Dict[str, Any]:
        """
        Check for appropriate handling of special characters
        """
        content = translation.translated_content
        
        # Check for unusual character sequences that might indicate encoding issues
        unusual_char_sequences = [
            '',  # Replacement character
            'â€™',  # Common encoding error for apostrophe
            'â€œ',  # Common encoding error for open quote
            'â€',  # Incomplete encoding error sequence
        ]
        
        issues_found = []
        for seq in unusual_char_sequences:
            if seq in content:
                issues_found.append(seq)
        
        passed = len(issues_found) == 0
        score = max(0, 100 - len(issues_found) * 30)  # Each issue reduces score by 30
        
        return {
            "check_name": "special_characters",
            "passed": passed,
            "score": score,
            "details": f"Found {len(issues_found)} potential encoding issues: {', '.join(issues_found) if issues_found else 'None'}"
        }
    
    def _calculate_quality_score(self, check_results: List[Dict[str, Any]]) -> float:
        """
        Calculate overall quality score based on individual check results
        """
        if not check_results:
            return 0.0
        
        total_score = sum(result.get("score", 0) for result in check_results)
        return total_score / len(check_results)
    
    def run_quality_audit_batch(self, db: Session, translation_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Run quality assurance on a batch of translations
        """
        results = []
        for trans_id in translation_ids:
            result = self.run_quality_assurance(db, trans_id)
            results.append(result)
        return results
    
    def get_quality_report(self, db: Session, language: str = None) -> Dict[str, Any]:
        """
        Generate a quality report for translations
        """
        # Get all translations for the specified language
        if language:
            translations = self.translation_service.get_translations_by_language(db, language, 0, 10000)
        else:
            # This would require a different method to get all translations
            translations = []  # Simplified for this example
        
        # Run quality checks on all translations
        audit_results = self.run_quality_audit_batch(db, [str(t.id) for t in translations])
        
        # Aggregate results
        total_translations = len(audit_results)
        passed_count = len([r for r in audit_results if r.get('status') == 'pass'])
        avg_quality_score = sum(r.get('quality_score', 0) for r in audit_results) / total_translations if total_translations > 0 else 0
        
        return {
            "total_translations": total_translations,
            "passed_translations": passed_count,
            "failed_translations": total_translations - passed_count,
            "average_quality_score": avg_quality_score,
            "pass_rate": (passed_count / total_translations * 100) if total_translations > 0 else 0
        }
    
    def suggest_improvements(self, db: Session, translation_id: str) -> List[str]:
        """
        Suggest specific improvements for a translation based on quality checks
        """
        qa_result = self.run_quality_assurance(db, translation_id)
        
        suggestions = []
        for check in qa_result.get('checks', []):
            if not check.get('passed'):
                if check['check_name'] == 'length_consistency':
                    suggestions.append("Review translation length - it may be significantly longer or shorter than the original content")
                elif check['check_name'] == 'special_characters':
                    suggestions.append("Check for encoding issues or unusual characters in the translation")
                elif check['check_name'] == 'formatting_preservation':
                    suggestions.append("Ensure formatting elements from the original content are preserved in the translation")
                elif check['check_name'] == 'terminology_consistency':
                    suggestions.append("Ensure consistent use of technical terms throughout the translation")
        
        return suggestions