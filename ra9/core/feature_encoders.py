"""
Feature Encoders - Primary cortex analogue
Handles multimodal feature extraction and encoding
"""

from typing import List, Dict, Any, Optional, Union
import numpy as np
from .schemas import Percept, ModalityType


class FeatureEncoder:
    """Base class for feature encoders"""
    
    def encode(self, percept: Percept) -> Dict[str, Any]:
        """Encode percept into features"""
        raise NotImplementedError


class TextEncoder(FeatureEncoder):
    """Text feature encoder - handles natural language"""
    
    def __init__(self):
        self.feature_extractors = [
            self._extract_semantic_features,
            self._extract_syntactic_features,
            self._extract_linguistic_features,
            self._extract_contextual_features
        ]
    
    def encode(self, percept: Percept) -> Dict[str, Any]:
        """Encode text percept into features"""
        features = {
            'modality': 'text',
            'embedding': percept.embedding,
            'tokens': percept.tokens,
            'raw_text': percept.raw_text
        }
        
        # Extract various feature types
        for extractor in self.feature_extractors:
            features.update(extractor(percept))
        
        return features
    
    def _extract_semantic_features(self, percept: Percept) -> Dict[str, Any]:
        """Extract semantic meaning features"""
        text = percept.raw_text.lower()
        
        # Topic indicators
        topic_indicators = {
            'technology': ['code', 'programming', 'software', 'algorithm', 'data', 'ai', 'machine learning'],
            'science': ['research', 'experiment', 'hypothesis', 'theory', 'analysis', 'study'],
            'business': ['strategy', 'marketing', 'sales', 'revenue', 'profit', 'management'],
            'personal': ['feel', 'think', 'believe', 'experience', 'personal', 'myself'],
            'creative': ['design', 'art', 'creative', 'imagine', 'inspire', 'beautiful']
        }
        
        topic_scores = {}
        for topic, keywords in topic_indicators.items():
            score = sum(1 for keyword in keywords if keyword in text) / len(keywords)
            topic_scores[f'topic_{topic}'] = score
        
        return {
            'semantic_features': {
                'topic_scores': topic_scores,
                'abstractness': self._calculate_abstractness(text),
                'concreteness': self._calculate_concreteness(text)
            }
        }
    
    def _extract_syntactic_features(self, percept: Percept) -> Dict[str, Any]:
        """Extract syntactic structure features"""
        text = percept.raw_text
        
        # Sentence structure
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        
        # Question patterns
        is_question = '?' in text
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        question_word_count = sum(1 for word in question_words if word in text.lower())
        
        # Imperative patterns
        imperative_indicators = ['please', 'can you', 'help me', 'do this', 'make']
        is_imperative = any(indicator in text.lower() for indicator in imperative_indicators)
        
        return {
            'syntactic_features': {
                'avg_sentence_length': avg_sentence_length,
                'is_question': is_question,
                'question_word_count': question_word_count,
                'is_imperative': is_imperative,
                'sentence_count': len(sentences)
            }
        }
    
    def _extract_linguistic_features(self, percept: Percept) -> Dict[str, Any]:
        """Extract linguistic complexity features"""
        text = percept.raw_text
        words = text.split()
        
        # Vocabulary complexity
        unique_words = set(word.lower() for word in words)
        vocabulary_richness = len(unique_words) / max(1, len(words))
        
        # Word length distribution
        word_lengths = [len(word) for word in words]
        avg_word_length = sum(word_lengths) / max(1, len(word_lengths))
        
        # Technical terms
        technical_terms = ['algorithm', 'function', 'variable', 'parameter', 'method', 'class', 'object']
        technical_term_count = sum(1 for term in technical_terms if term in text.lower())
        
        return {
            'linguistic_features': {
                'vocabulary_richness': vocabulary_richness,
                'avg_word_length': avg_word_length,
                'technical_term_count': technical_term_count,
                'total_words': len(words),
                'unique_words': len(unique_words)
            }
        }
    
    def _extract_contextual_features(self, percept: Percept) -> Dict[str, Any]:
        """Extract contextual and pragmatic features"""
        text = percept.raw_text
        
        # Politeness markers
        politeness_markers = ['please', 'thank you', 'thanks', 'appreciate', 'sorry', 'excuse me']
        politeness_score = sum(1 for marker in politeness_markers if marker in text.lower())
        
        # Uncertainty markers
        uncertainty_markers = ['maybe', 'perhaps', 'might', 'could', 'possibly', 'unclear', 'not sure']
        uncertainty_score = sum(1 for marker in uncertainty_markers if marker in text.lower())
        
        # Confidence markers
        confidence_markers = ['definitely', 'certainly', 'sure', 'absolutely', 'clearly', 'obviously']
        confidence_score = sum(1 for marker in confidence_markers if marker in text.lower())
        
        return {
            'contextual_features': {
                'politeness_score': politeness_score,
                'uncertainty_score': uncertainty_score,
                'confidence_score': confidence_score,
                'emotional_tone': self._assess_emotional_tone(text)
            }
        }
    
    def _calculate_abstractness(self, text: str) -> float:
        """Calculate abstractness score"""
        abstract_words = ['concept', 'idea', 'theory', 'principle', 'philosophy', 'abstract', 'general']
        concrete_words = ['table', 'chair', 'car', 'house', 'book', 'computer', 'specific']
        
        abstract_count = sum(1 for word in abstract_words if word in text)
        concrete_count = sum(1 for word in concrete_words if word in text)
        
        total = abstract_count + concrete_count
        return abstract_count / max(1, total)
    
    def _calculate_concreteness(self, text: str) -> float:
        """Calculate concreteness score (inverse of abstractness)"""
        return 1.0 - self._calculate_abstractness(text)
    
    def _assess_emotional_tone(self, text: str) -> str:
        """Assess emotional tone of the text"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'frustrated']
        neutral_words = ['okay', 'fine', 'normal', 'average', 'standard']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        neu_count = sum(1 for word in neutral_words if word in text_lower)
        
        if pos_count > neg_count and pos_count > neu_count:
            return 'positive'
        elif neg_count > pos_count and neg_count > neu_count:
            return 'negative'
        else:
            return 'neutral'


class CodeEncoder(FeatureEncoder):
    """Code feature encoder - handles programming languages"""
    
    def encode(self, percept: Percept) -> Dict[str, Any]:
        """Encode code percept into features"""
        features = {
            'modality': 'code',
            'embedding': percept.embedding,
            'tokens': percept.tokens,
            'raw_text': percept.raw_text
        }
        
        # Extract code-specific features
        features.update(self._extract_language_features(percept))
        features.update(self._extract_structure_features(percept))
        features.update(self._extract_complexity_features(percept))
        
        return features
    
    def _extract_language_features(self, percept: Percept) -> Dict[str, Any]:
        """Extract programming language features"""
        text = percept.raw_text
        
        # Language detection
        language_indicators = {
            'python': ['def ', 'import ', 'class ', 'if __name__', 'print(', 'lambda '],
            'javascript': ['function ', 'const ', 'let ', 'var ', '=>', 'console.log'],
            'java': ['public class', 'public static void', 'System.out.println', 'private '],
            'cpp': ['#include', 'int main()', 'std::', 'namespace ', 'class '],
            'sql': ['SELECT ', 'FROM ', 'WHERE ', 'INSERT ', 'UPDATE ', 'DELETE ']
        }
        
        language_scores = {}
        for lang, indicators in language_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text) / len(indicators)
            language_scores[lang] = score
        
        detected_language = max(language_scores, key=language_scores.get) if language_scores else 'unknown'
        
        return {
            'language_features': {
                'detected_language': detected_language,
                'language_scores': language_scores,
                'confidence': max(language_scores.values()) if language_scores else 0.0
            }
        }
    
    def _extract_structure_features(self, percept: Percept) -> Dict[str, Any]:
        """Extract code structure features"""
        text = percept.raw_text
        lines = text.split('\n')
        
        # Basic structure metrics
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#') or line.strip().startswith('//')])
        
        # Indentation analysis
        indentation_levels = []
        for line in lines:
            if line.strip():  # Non-empty line
                indent = len(line) - len(line.lstrip())
                indentation_levels.append(indent)
        
        avg_indentation = sum(indentation_levels) / max(1, len(indentation_levels))
        max_indentation = max(indentation_levels) if indentation_levels else 0
        
        return {
            'structure_features': {
                'total_lines': total_lines,
                'non_empty_lines': non_empty_lines,
                'comment_lines': comment_lines,
                'comment_ratio': comment_lines / max(1, non_empty_lines),
                'avg_indentation': avg_indentation,
                'max_indentation': max_indentation
            }
        }
    
    def _extract_complexity_features(self, percept: Percept) -> Dict[str, Any]:
        """Extract code complexity features"""
        text = percept.raw_text
        
        # Cyclomatic complexity indicators
        control_flow_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'case', 'switch']
        control_flow_count = sum(1 for keyword in control_flow_keywords if keyword in text)
        
        # Function/method count
        function_patterns = ['def ', 'function ', 'public ', 'private ', 'protected ']
        function_count = sum(1 for pattern in function_patterns if pattern in text)
        
        # Variable count (rough estimate)
        variable_patterns = ['=', 'let ', 'const ', 'var ', 'int ', 'string ', 'float ']
        variable_count = sum(1 for pattern in variable_patterns if pattern in text)
        
        return {
            'complexity_features': {
                'control_flow_count': control_flow_count,
                'function_count': function_count,
                'variable_count': variable_count,
                'complexity_score': (control_flow_count + function_count) / max(1, len(text.split('\n')))
            }
        }


class MultimodalEncoder(FeatureEncoder):
    """Multimodal feature encoder - combines multiple modalities"""
    
    def __init__(self):
        self.text_encoder = TextEncoder()
        self.code_encoder = CodeEncoder()
    
    def encode(self, percept: Percept) -> Dict[str, Any]:
        """Encode multimodal percept into features"""
        features = {
            'modality': 'multimodal',
            'embedding': percept.embedding,
            'tokens': percept.tokens,
            'raw_text': percept.raw_text
        }
        
        # Encode based on detected modality
        if percept.modality == ModalityType.CODE:
            code_features = self.code_encoder.encode(percept)
            features.update(code_features)
        else:
            text_features = self.text_encoder.encode(percept)
            features.update(text_features)
        
        # Add cross-modal features
        features.update(self._extract_cross_modal_features(percept))
        
        return features
    
    def _extract_cross_modal_features(self, percept: Percept) -> Dict[str, Any]:
        """Extract features that span multiple modalities"""
        text = percept.raw_text
        
        # Check for mixed content
        has_code = '```' in text or '`' in text
        has_text = len(text.split()) > 10  # Substantial text content
        
        return {
            'cross_modal_features': {
                'has_code': has_code,
                'has_text': has_text,
                'is_mixed_content': has_code and has_text,
                'content_balance': self._calculate_content_balance(text)
            }
        }
    
    def _calculate_content_balance(self, text: str) -> float:
        """Calculate balance between different content types"""
        code_blocks = text.count('```')
        inline_code = text.count('`') - (code_blocks * 2)
        text_content = len(text.split())
        
        if text_content == 0:
            return 0.0
        
        code_ratio = (code_blocks + inline_code) / text_content
        return min(code_ratio, 1.0)


class FeatureEncoderFactory:
    """Factory for creating appropriate feature encoders"""
    
    @staticmethod
    def create_encoder(modality: ModalityType) -> FeatureEncoder:
        """Create appropriate encoder for modality"""
        if modality == ModalityType.TEXT:
            return TextEncoder()
        elif modality == ModalityType.CODE:
            return CodeEncoder()
        elif modality == ModalityType.MULTIMODAL:
            return MultimodalEncoder()
        else:
            # Default to text encoder
            return TextEncoder()
    
    @staticmethod
    def encode_percept(percept: Percept) -> Dict[str, Any]:
        """Convenience method to encode any percept"""
        encoder = FeatureEncoderFactory.create_encoder(percept.modality)
        return encoder.encode(percept)
