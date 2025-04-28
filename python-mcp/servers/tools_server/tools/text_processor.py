class TextProcessor:
    """Text processor tool for MCP."""

    def word_count(self, text):
        """Count words in text."""
        return len([word for word in text.split() if word.strip()])

    def character_count(self, text):
        """Count characters in text."""
        return len(text)

    def sentence_count(self, text):
        """Count sentences in text."""
        return len([s for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()])

    def to_upper_case(self, text):
        """Convert text to uppercase."""
        return text.upper()

    def to_lower_case(self, text):
        """Convert text to lowercase."""
        return text.lower()
