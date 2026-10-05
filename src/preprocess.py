import re
from bs4 import BeautifulSoup
from typing import List


def clean_text(text: str) -> str:
    """
    Clean raw text by removing HTML tags, URLs, and normalizing whitespace.
    """
    # Remove HTML tags
    if '<' in text and '>' in text:
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Normalize whitespace: replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def split_into_clauses(text: str, min_words: int = 5) -> List[str]:
    """
    Split text into sentence-level clauses.
    A clause is a sentence or sentence fragment with at least min_words words.
    """
    # Split by common sentence delimiters (. ! ? ; :)
    # We'll use regex to split while keeping the delimiter
    clauses = re.split(r'[.!?;:]\s+', text)
    
    # Filter out short clauses and empty strings
    clauses = [c.strip() for c in clauses if c.strip()]
    clauses = [c for c in clauses if len(c.split()) >= min_words]
    
    return clauses


if __name__ == "__main__":
    # Test the functions
    sample = "This is a test. With multiple sentences! And some URLs http://example.com"
    cleaned = clean_text(sample)
    print(f"Cleaned: {cleaned}")
    clauses = split_into_clauses(cleaned)
    print(f"Clauses: {clauses}")
