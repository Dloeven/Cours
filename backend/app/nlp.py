"""
NLP processing module for text analysis, summarization, and keyword extraction.
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import Counter
import numpy as np


class NLPProcessor:
    """Handles NLP processing for text analysis."""
    
    def __init__(self):
        # Try to load spaCy model
        try:
            import spacy
            self.nlp = spacy.load("fr_core_news_md")
            self.spacy_available = True
        except:
            try:
                self.nlp = spacy.load("en_core_web_md")
                self.spacy_available = True
            except:
                self.spacy_available = False
                print("spaCy model not available")
        
        # Try to load transformers
        try:
            from transformers import pipeline
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            self.transformers_available = True
        except:
            self.transformers_available = False
            print("Transformers not available")
        
        # Fallback patterns
        self.keyword_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized phrases
            r'\b\w{8,}\b',  # Long words
            r'\b\w+-\w+\b',  # Hyphenated words
        ]
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text."""
        if not text:
            return []
        
        if self.spacy_available:
            doc = self.nlp(text)
            keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
            keywords = [kw for kw in keywords if len(kw) > 2]
            
            # Get most common
            counter = Counter(keywords)
            return [kw for kw, _ in counter.most_common(top_n)]
        else:
            # Fallback method
            words = re.findall(r'\b\w{3,}\b', text.lower())
            stop_words = {'le', 'la', 'les', 'de', 'des', 'du', 'un', 'une', 'et', 'ou', 'à', 'au', 
                         'pour', 'par', 'sur', 'dans', 'ce', 'cette', 'ces', 'qui', 'que', 'dont',
                         'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'is', 'are'}
            words = [w for w in words if w not in stop_words]
            counter = Counter(words)
            return [w for w, _ in counter.most_common(top_n)]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],  # Geopolitical entities
            "DATE": [],
            "NUMERIC": [],
        }
        
        if self.spacy_available:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)
                elif ent.label_ == "CARDINAL" or ent.label_ == "QUANTITY":
                    entities["NUMERIC"].append(ent.text)
        
        return entities
    
    def generate_summary(self, text: str, max_length: int = 500, summary_type: str = "general") -> str:
        """Generate a summary of the text."""
        if not text:
            return ""
        
        # If text is short enough, return as is
        if len(text.split()) <= max_length // 10:
            return text
        
        if self.transformers_available:
            try:
                # Truncate if too long for model
                max_input_length = 1024
                if len(text.split()) > max_input_length:
                    sentences = re.split(r'(?<=[.!?])\s+', text)
                    chunks = []
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk.split()) + len(sentence.split()) < max_input_length:
                            current_chunk += sentence + " "
                        else:
                            chunks.append(current_chunk)
                            current_chunk = sentence + " "
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    summaries = []
                    for chunk in chunks:
                        summary = self.summarizer(chunk, max_length=max_length // len(chunks), min_length=50)[0]['summary_text']
                        summaries.append(summary)
                    return " ".join(summaries)
                else:
                    summary = self.summarizer(text, max_length=max_length, min_length=50)[0]['summary_text']
                    return summary
            except Exception as e:
                print(f"Error with transformers summarization: {e}")
        
        # Fallback: Extractive summarization
        return self.extractive_summarize(text, max_length)
    
    def extractive_summarize(self, text: str, max_length: int = 500) -> str:
        """Create extractive summary by selecting important sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if not sentences:
            return text[:max_length]
        
        # Score sentences based on keywords
        keywords = self.extract_keywords(text, top_n=20)
        
        scored_sentences = []
        for sentence in sentences:
            score = 0
            for keyword in keywords:
                if keyword.lower() in sentence.lower():
                    score += 1
            
            # Bonus for longer sentences
            score += len(sentence.split()) * 0.1
            
            # Bonus for position (first and last sentences are important)
            if len(scored_sentences) == 0 or len(scored_sentences) == len(sentences) - 1:
                score += 5
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Select sentences until we reach max_length
        selected_sentences = []
        current_length = 0
        
        for sentence, _ in scored_sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length <= max_length // 10:
                selected_sentences.append(sentence)
                current_length += sentence_length
            else:
                break
        
        # If we didn't select enough, add more from the beginning
        if len(selected_sentences) < 3 and len(sentences) > 0:
            for i, sentence in enumerate(sentences):
                if sentence not in selected_sentences:
                    selected_sentences.insert(i, sentence)
                    if len(selected_sentences) >= 3:
                        break
        
        # Sort by original order
        original_order = {sentence: i for i, sentence in enumerate(sentences)}
        selected_sentences.sort(key=lambda x: original_order.get(x, 0))
        
        return " ".join(selected_sentences)
    
    def extract_definitions(self, text: str) -> List[Dict[str, str]]:
        """Extract potential definitions from text."""
        definitions = []
        
        # Pattern: Term followed by colon or dash and explanation
        pattern = r'([A-Z][a-zA-Z\s-]+):\s+([^\n]+)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            term = match.group(1).strip()
            definition = match.group(2).strip()
            
            # Clean up
            term = re.sub(r'\s+', ' ', term)
            definition = re.sub(r'\s+', ' ', definition)
            
            if len(term) > 2 and len(definition) > 10:
                definitions.append({
                    "term": term,
                    "definition": definition
                })
        
        # Also look for "est un/une" patterns (French)
        pattern_fr = r'([A-Z][a-zA-Z\s-]+)\s+(est|sont|représente|désigne)\s+(un|une|le|la|les|des)?\s+([^\n.]+[.!?])'
        matches = re.finditer(pattern_fr, text)
        
        for match in matches:
            term = match.group(1).strip()
            definition = match.group(4).strip()
            
            term = re.sub(r'\s+', ' ', term)
            definition = re.sub(r'\s+', ' ', definition)
            
            if len(term) > 2 and len(definition) > 10:
                definitions.append({
                    "term": term,
                    "definition": definition
                })
        
        return definitions
    
    def extract_questions(self, text: str) -> List[str]:
        """Extract questions from text."""
        questions = []
        
        # Find sentences ending with question marks
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence.endswith('?'):
                # Clean up
                sentence = re.sub(r'\s+', ' ', sentence)
                if len(sentence) > 10:
                    questions.append(sentence)
        
        return questions
    
    def analyze_text(self, text: str) -> Dict:
        """Perform comprehensive text analysis."""
        analysis = {
            "word_count": len(text.split()),
            "char_count": len(text),
            "sentence_count": len(re.split(r'[.!?]', text)),
            "paragraph_count": len(text.split('\n\n')),
            "keywords": self.extract_keywords(text, top_n=15),
            "entities": self.extract_entities(text),
            "language": self.detect_language(text),
        }
        
        return analysis
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        # Simple heuristic
        words = text.lower().split()
        
        french_words = {'le', 'la', 'les', 'de', 'des', 'du', 'un', 'une', 'et', 'ou', 'à', 'au', 'pour', 'par'}
        english_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'is', 'are'}
        
        french_count = sum(1 for word in words if word in french_words)
        english_count = sum(1 for word in words if word in english_words)
        
        if french_count > english_count:
            return "fr"
        elif english_count > french_count:
            return "en"
        else:
            return "unknown"
    
    def find_similar_texts(self, text: str, texts: List[str], top_n: int = 3) -> List[Tuple[str, float]]:
        """Find similar texts using simple TF-IDF."""
        if not texts:
            return []
        
        # Simple word overlap similarity
        text_words = set(text.lower().split())
        
        similarities = []
        for other_text in texts:
            other_words = set(other_text.lower().split())
            if len(text_words) == 0 or len(other_words) == 0:
                similarity = 0.0
            else:
                intersection = len(text_words & other_words)
                union = len(text_words | other_words)
                similarity = intersection / union
            
            similarities.append((other_text, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_n]


# Singleton instance
nlp_processor = NLPProcessor()


# Convenience functions
def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract keywords from text."""
    return nlp_processor.extract_keywords(text, top_n)


def generate_summary(text: str, max_length: int = 500, summary_type: str = "general") -> str:
    """Generate a summary of the text."""
    return nlp_processor.generate_summary(text, max_length, summary_type)


def extract_definitions(text: str) -> List[Dict[str, str]]:
    """Extract definitions from text."""
    return nlp_processor.extract_definitions(text)


def extract_questions(text: str) -> List[str]:
    """Extract questions from text."""
    return nlp_processor.extract_questions(text)


def analyze_text(text: str) -> Dict:
    """Analyze text comprehensively."""
    return nlp_processor.analyze_text(text)
