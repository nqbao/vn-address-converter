"""Utility helper functions for Vietnamese address conversion."""
import unicodedata


def accent_fold(text: str) -> str:
    """Return lowercase accent-folded (diacritic stripped) version of text.
    Performs NFC then NFD normalization and removes all combining marks.
    Also normalizes the Vietnamese letter 'đ'/'Đ' to 'd'.
    Args:
        text: Input string
    Returns:
        Diacritic-free string (or original value if falsy)
    """
    if not text:
        return text
    nfc = unicodedata.normalize("NFC", text)
    nfd = unicodedata.normalize("NFD", nfc)
    folded = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    # Map special Vietnamese letters that are not combining sequences
    folded = folded.replace('đ', 'd').replace('Đ', 'D')
    return folded
