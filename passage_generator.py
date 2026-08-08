import json
import random
import re
import urllib.request

SUBJECTS = ["the cat", "a young boy", "our teacher", "the old man", "a gentle breeze",
            "the football team", "my best friend", "a curious student", "the bright sun"]
VERBS = ["ran across", "quietly watched", "quickly found", "carefully studied",
         "slowly walked through", "happily jumped over", "gently touched"]
OBJECTS = ["the empty field", "a strange noise", "the old library", "the busy market",
           "a broken window", "the tall mountain", "the local park"]
CONNECTORS = ["and then", "but suddenly", "while", "because", "so that", "before"]


def capitalize_sentences(text):
    """Capitalizes the first character of text and any letter following a full stop."""
    if not text:
        return ""

    # Capitalize start of text and any character following a period and spaces
    def replace_cap(match):
        return match.group(1) + match.group(2).upper()

    text = text[0].upper() + text[1:]
    return re.sub(r'(\.\s+)([a-z])', replace_cap, text)


def generate_local_passage(word_target=220):
    sentences = []
    total_words = 0

    while total_words < word_target:
        clause1 = f"{random.choice(SUBJECTS)} {random.choice(VERBS)} {random.choice(OBJECTS)}"
        if random.random() < 0.5:
            clause2 = f"{random.choice(CONNECTORS)} {random.choice(VERBS)} {random.choice(OBJECTS)}"
            full_clause = f"{clause1} {clause2}."
        else:
            full_clause = f"{clause1}."

        sentences.append(full_clause)
        total_words += len(full_clause.split())

    raw_text = " ".join(sentences)
    return capitalize_sentences(raw_text)


def fetch_scraped_passage(word_target=220):
    try:
        url = "https://dummyjson.com/quotes?limit=30"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            quotes = [item['quote'] for item in data.get('quotes', [])]
            random.shuffle(quotes)
            text = " ".join(quotes)
            words = text.split()

            if len(words) >= word_target:
                text = " ".join(words[:word_target])
            return capitalize_sentences(text)
    except Exception:
        return generate_local_passage(word_target)