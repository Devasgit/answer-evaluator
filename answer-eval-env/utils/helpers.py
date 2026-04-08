import re
from difflib import SequenceMatcher

def clean_text(text: str) -> str:
    """Removes punctuation and converts text to lowercase."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def similar(a: str, b: str) -> float:
    """Returns a similarity ratio between 0 and 1 for two strings."""
    return SequenceMatcher(None, a, b).ratio()

def extract_keywords(text: str) -> set:
    """Extracts basic words from text."""
    return set(clean_text(text).split())

def match_concepts(answer: str, concepts: list[str], threshold: float = 0.75):
    """
    Checks which concepts are covered in the answer using exact match and semantic similarity check.
    Returns (covered_concepts, missing_concepts)
    """
    cleaned_answer = clean_text(answer)
    covered = []
    missing = []
    
    for concept in concepts:
        cleaned_concept = clean_text(concept)
        if cleaned_concept in cleaned_answer:
            covered.append(concept)
        else:
            # Try fuzzy matching in case of typos, split answer into chunks of concept length roughly
            words = cleaned_answer.split()
            concept_words = cleaned_concept.split()
            concept_len = len(concept_words)
            
            found = False
            if concept_len > 0:
                # Check sliding window of word combinations
                for i in range(len(words) - concept_len + 1):
                    chunk = " ".join(words[i:i+concept_len])
                    if similar(chunk, cleaned_concept) >= threshold:
                        found = True
                        break
                
                # Check individual words against single-word concepts that might be slightly misspelled
                if not found and concept_len == 1:
                    for word in words:
                        if similar(word, cleaned_concept) >= threshold:
                            found = True
                            break
            
            if found:
                covered.append(concept)
            else:
                missing.append(concept)
                
    return covered, missing
