from difflib import SequenceMatcher
def check(user_diag: str, correct: str) -> bool:
    similarity = SequenceMatcher(None, user_diag.lower(), correct.lower()).ratio()
    return similarity > 0.8
