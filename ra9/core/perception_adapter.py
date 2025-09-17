"""
Perception Adapter - Sensory receptors & thalamic relay analogue
Handles multimodal input processing and feature extraction
"""

import re
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .schemas import Percept, ModalityType, ContextBundle
from ..tools.tool_api import ask_gemini


class PerceptionAdapter:
    """
    Processes raw input and creates structured Percept objects
    Analogous to sensory receptors + thalamic relay in the brain
    """
    
    def __init__(self):
        self.modality_detectors = {
            'code': self._detect_code,
            'image': self._detect_image,
            'audio': self._detect_audio,
            'text': self._detect_text
        }
    
    def process(self, raw_input: str, metadata: Dict[str, Any] = None) -> Percept:
        """
        Main entry point - processes raw input into structured Percept
        
        Args:
            raw_input: Raw text/input from user
            metadata: Additional context (session_id, user_id, etc.)
            
        Returns:
            Percept object with modality, embedding, tokens, and metadata
        """
        if metadata is None:
            metadata = {}
            
        # Detect modality
        modality = self._detect_modality(raw_input)
        
        # Extract features based on modality
        tokens = self._tokenize(raw_input, modality)
        embedding = self._generate_embedding(raw_input, modality)
        
        # Create Percept object
        percept = Percept(
            modality=modality,
            embedding=embedding,
            tokens=tokens,
            raw_text=raw_input,
            meta=metadata,
            timestamp=datetime.now(),
            session_id=metadata.get('session_id', ''),
            user_id=metadata.get('user_id', ''),
            privacy_flags=metadata.get('privacy_flags', {})
        )
        
        return percept
    
    def _detect_modality(self, raw_input: str) -> ModalityType:
        """Detect the primary modality of the input"""
        # Check for code patterns
        if self._detect_code(raw_input):
            return ModalityType.CODE
        
        # Check for image references
        if self._detect_image(raw_input):
            return ModalityType.IMAGE
            
        # Check for audio references
        if self._detect_audio(raw_input):
            return ModalityType.AUDIO
        
        # Default to text
        return ModalityType.TEXT
    
    def _detect_code(self, text: str) -> bool:
        """Detect if input contains code"""
        code_patterns = [
            r'```[\s\S]*?```',  # Code blocks
            r'`[^`]+`',         # Inline code
            r'def\s+\w+',       # Python functions
            r'function\s+\w+',  # JavaScript functions
            r'class\s+\w+',     # Classes
            r'import\s+\w+',    # Imports
            r'#include\s*<',    # C++ includes
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _detect_image(self, text: str) -> bool:
        """Detect if input references images"""
        image_patterns = [
            r'\.(jpg|jpeg|png|gif|bmp|svg|webp)',
            r'image|picture|photo|screenshot',
            r'\[.*?\]\(.*?\.(jpg|jpeg|png|gif|bmp|svg|webp)\)',
            r'<img\s+src=',
        ]
        
        for pattern in image_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _detect_audio(self, text: str) -> bool:
        """Detect if input references audio"""
        audio_patterns = [
            r'\.(mp3|wav|flac|aac|ogg|m4a)',
            r'audio|sound|music|voice|speech',
            r'record|recording|listen',
        ]
        
        for pattern in audio_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _detect_text(self, text: str) -> bool:
        """Default text detection - always true as fallback"""
        return True
    
    def _tokenize(self, text: str, modality: ModalityType) -> List[str]:
        """Tokenize input based on modality"""
        if modality == ModalityType.CODE:
            return self._tokenize_code(text)
        else:
            return self._tokenize_text(text)
    
    def _tokenize_code(self, text: str) -> List[str]:
        """Tokenize code with language awareness"""
        # Simple word-based tokenization for now
        # In production, use proper code tokenizers (Tree-sitter, etc.)
        tokens = re.findall(r'\w+|[^\w\s]', text)
        return tokens
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize natural language text"""
        # Simple word-based tokenization
        # In production, use proper NLP tokenizers (spaCy, NLTK, etc.)
        tokens = re.findall(r'\w+|[^\w\s]', text.lower())
        return tokens
    
    def _generate_embedding(self, text: str, modality: ModalityType) -> List[float]:
        """
        Generate embedding for the input text
        In production, use proper embedding models (sentence-transformers, etc.)
        """
        # For now, create a simple hash-based embedding
        # In production, use actual embedding models
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to pseudo-embedding (768 dimensions like BERT)
        embedding = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            val = int(hex_pair, 16) / 255.0  # Normalize to 0-1
            embedding.append(val)
        
        # Pad or truncate to 768 dimensions
        while len(embedding) < 768:
            embedding.append(0.0)
        embedding = embedding[:768]
        
        return embedding
    
    def extract_intent_features(self, percept: Percept) -> Dict[str, Any]:
        """
        Extract additional features for intent classification
        """
        features = {
            'length': len(percept.raw_text),
            'token_count': len(percept.tokens),
            'modality': percept.modality.value,
            'has_question': '?' in percept.raw_text,
            'has_imperative': any(word in percept.raw_text.lower() 
                                for word in ['please', 'can you', 'help', 'do', 'make']),
            'has_technical_terms': any(word in percept.raw_text.lower() 
                                    for word in ['algorithm', 'function', 'code', 'data', 'model']),
            'sentiment_indicators': self._extract_sentiment_indicators(percept.raw_text),
            'complexity_score': self._calculate_complexity_score(percept.raw_text)
        }
        
        return features
    
    def _extract_sentiment_indicators(self, text: str) -> Dict[str, int]:
        """Extract basic sentiment indicators"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'wrong', 'error']
        urgent_words = ['urgent', 'asap', 'immediately', 'critical', 'important']
        
        text_lower = text.lower()
        
        return {
            'positive': sum(1 for word in positive_words if word in text_lower),
            'negative': sum(1 for word in negative_words if word in text_lower),
            'urgent': sum(1 for word in urgent_words if word in text_lower)
        }
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate a simple complexity score"""
        # Simple heuristics for complexity
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        
        # Count complex words (3+ syllables approximation)
        words = text.split()
        complex_words = sum(1 for word in words if len(word) > 6)
        complexity_ratio = complex_words / max(1, len(words))
        
        # Combine metrics
        complexity_score = (avg_sentence_length / 20.0) + complexity_ratio
        return min(complexity_score, 1.0)  # Cap at 1.0


def create_percept_from_request(request_data: Dict[str, Any]) -> Percept:
    """Convenience function to create Percept from request data"""
    adapter = PerceptionAdapter()
    
    metadata = {
        'session_id': request_data.get('sessionId', ''),
        'user_id': request_data.get('userId', ''),
        'privacy_flags': request_data.get('privacyFlags', {}),
        'mode': request_data.get('mode', 'concise'),
        'loop_depth': request_data.get('loopDepth', 2),
        'allow_memory_write': request_data.get('allowMemoryWrite', False)
    }
    
    return adapter.process(request_data.get('text', ''), metadata)
