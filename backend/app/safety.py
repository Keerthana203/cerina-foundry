def evaluate_safety(text: str) -> float:
    banned = ["self-harm", "suicide"]
    for word in banned:
        if word in text.lower():
            return 0.5
    return 0.95
