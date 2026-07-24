class SentenceBuilder:
    """
    Stateful builder for maintaining a sentence from individual signed letters.
    One instance should be created per active connection.
    """
    def __init__(self, max_length: int = 200):
        self.sentence = ""
        self.max_length = max_length

    def add_letter(self, letter: str) -> None:
        """Appends a confirmed letter to the sentence."""
        if len(self.sentence) < self.max_length:
            self.sentence += letter

    def add_space(self) -> None:
        """Appends a space, preventing multiple consecutive spaces."""
        if not self.sentence.endswith(" ") and len(self.sentence) < self.max_length:
            # Also prevent starting the sentence with a space
            if len(self.sentence) > 0:
                self.sentence += " "

    def delete_last(self) -> None:
        """Removes the last character (letter or space)."""
        if len(self.sentence) > 0:
            self.sentence = self.sentence[:-1]

    def clear(self) -> None:
        """Resets the sentence to an empty string."""
        self.sentence = ""

    def get_sentence(self) -> str:
        """Returns the current sentence."""
        return self.sentence
