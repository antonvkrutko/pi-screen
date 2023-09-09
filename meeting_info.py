class MeetingInfo:
    def __init__(self, title: str, time_info: str, is_free: bool):
        self.title = title
        self.time_info = time_info
        self.is_free: bool = is_free

    def __str__(self):
        return self.title + ", time_info: " + self.time_info + ", is_free: " + str(self.is_free)
