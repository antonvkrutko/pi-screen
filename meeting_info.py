class MeetingInfo:
    def __init__(self, title: str, time_info: str, time_token: int, is_free: bool):
        self.title = title
        self.time_info = time_info
        self.time_token = time_token
        self.is_free = is_free

    def __str__(self):
        return self.title + ", time_info: " + self.time_info + ", time_token: " + str(
            self.time_token) + ", is_free: " + str(self.is_free)
