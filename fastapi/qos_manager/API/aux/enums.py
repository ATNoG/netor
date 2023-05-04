from enum import Enum, unique
@unique
class ActionStatus(Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    def __str__(self):
        return str(self.value)