"""Simple list-based profanity filter for MVP."""

PROFANITY_LIST = {
    "fuck", "shit", "ass", "bitch", "bastard", "damn", "crap",
    "dick", "piss", "whore", "slut", "cunt", "asshole", "motherfucker",
    "bullshit", "dumbass", "jackass", "idiot", "moron", "retard",
}


def check_profanity(text: str) -> bool:
    """Returns True if the text contains profanity."""
    words = text.lower().split()
    return any(word.strip(".,!?;:'\"") in PROFANITY_LIST for word in words)


def censor_profanity(text: str) -> str:
    """Replace profane words with asterisks."""
    words = text.split()
    result = []
    for word in words:
        stripped = word.lower().strip(".,!?;:'\"")
        if stripped in PROFANITY_LIST:
            result.append("*" * len(word))
        else:
            result.append(word)
    return " ".join(result)
