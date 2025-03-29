from enum import Enum


class UserState(Enum):
    CHOOSING_TOPIC = "choosing_topic"
    TASK_IN_PROGRESS = "task_in_progress"
    COMPLETED = "completed"
