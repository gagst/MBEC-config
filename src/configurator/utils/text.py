class TextDescription:
    _text = ""

    def add_sentence(self, sentence: str):
        sentence = sentence.strip()
        sentence = capitalize_first(sentence)
        if sentence[-1] != ".":
            raise ValueError("Sentence must end with '.'")
        if len(self._text) > 1:
            self._text += " " + sentence
        else:
            self._text = sentence

    def add_sentences(self, sentences: list[str]):
        for sentence in sentences:
            self.add_sentence(sentence)

    def get_text(self):
        return self._text


def capitalize_first(string: str) -> str:
    if string:
        return string[0].upper() + string[1:]
    return string


def enumeration(strings: list[str]) -> str:
    if len(strings) == 2:
        return strings[0] + " and " + strings[1]
    elif len(strings) > 2:
        return ", ".join(strings[:-1]) + ", and " + strings[-1]
    else:
        raise ValueError("Enumeration requires one or more strings.")
