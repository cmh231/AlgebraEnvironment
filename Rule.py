from Pattern import Pattern

class Rule:
    def __init__(self, name: str, inputPattern: Pattern, outputPattern: Pattern):
        self._name = name
        self._inputPattern = inputPattern
        self._outputPattern = outputPattern
        if ~self.checkValidRule():
            raise ValueError("Arguments of the output pattern specified by the input did not inherit the properties " +
                             "required by the output pattern.")

    def getName(self) -> str:
        return self._name

    def getInputPattern(self) -> Pattern:
        return self._inputPattern

    def getOutputPattern(self) -> Pattern:
        return self._outputPattern

    def checkValidRule(self) -> bool:

        inputPatternsStruct: tuple[list[Pattern], bool] = self._inputPattern.getPatternsOfIndices()
        outputPatternsStruct: tuple[list[Pattern], bool] = self._inputPattern.getPatternsOfIndices()

        if ~inputPatternsStruct[1] | ~outputPatternsStruct[1]:
            return False

        inputPatterns: list[Pattern] = inputPatternsStruct[0]
        outputPatterns: list[Pattern] = outputPatternsStruct[0]

        if len(outputPatterns) > len(inputPatterns):
            return False

        for index in range(len(outputPatterns)):
            inputPattern = inputPatterns[index]
            if inputPattern is None:
                return False
            outputPattern = outputPatterns[index]
            if ~inputPattern.getPropertyInheritance().inheritsProperties(
                    [outputPattern.getPropertyInheritance()],
                    False
            ):
                return False

        return True