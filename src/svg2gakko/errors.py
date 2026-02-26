class Svg2GakkoError(Exception):
    """Base exception for svg2gakko package."""

    pass


class InputDirectoryDoesntExistError(Svg2GakkoError):
    """Raised when passed input directory to the CLI doesn't exist or None"""

    pass


class InputDirectoryIsNotDirectoryError(Svg2GakkoError):
    """Raised when passed input directory to the CLI is not directory"""

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


class NotAtLeastThreeNumberOfOptions(Svg2GakkoError):
    """Raised when number_of_options in Question is less than 3."""

    pass
