from dataclasses import dataclass


@dataclass
class Answer:
    content: str
    correct: bool
    weight: int = 1

    def to_dict(self):
        return {
            "Content": self.content,
            "Correct": self.correct,
            "Weight": self.weight,
        }

    # def __init__(self, content: str, is_correct: bool, weight: int = 1):
    #     self.content = content
    #     self.is_correct = is_correct
    #     self.weight = weight
