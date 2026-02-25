class Svg2GakkoError(Exception):
    """Base exception for svg2gakko package."""

    pass


class NotAtLeastTwoAnswersError(Svg2GakkoError):
    """Raised when MULTIPLE/SINGLE_CHOISE_QUESTION has less than 2 answers."""

    pass


class NotAtLeastOneCorrectAnswersError(Svg2GakkoError):
    """Raised when MULTIPLE/SINGLE_CHOISE_QUESTION hasn't at least 1 correct answers."""

    pass


class NotAllAnswerCorrectError(Svg2GakkoError):
    """Raised when TEXT_QUESTION' all answers are correct."""

    pass
