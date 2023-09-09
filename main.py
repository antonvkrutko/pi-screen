import sys

from meeting_info import MeetingInfo
from output import Output, ScreenOutput
# from piscreen import PiScreen
from screen import DummyScreen
from server import Callbacks
from server import CommandServer


class OutputInteractor(Callbacks):

    def __init__(self, output: Output):
        self.output = output

    def meeting(self, info: MeetingInfo):
        self.output.set_meeting_info(info=info)

    def free(self, message: str):
        self.output.set_meeting_free(message=message)


def main():
    args = sys.argv[1:]
    ip = None
    if args[0] == "--ip":
        ip = args[1]

    if ip is None:
        raise Exception("--ip arg is missing!")

    print("Starting server at:", ip)
    serv = CommandServer(
        address=(ip, 8080),
        callbacks=OutputInteractor(
            output=ScreenOutput(
                screen=DummyScreen(refresh_time=1, size=(240, 135))
            )
        )
    )
    serv.start()


if __name__ == '__main__':
    sys.exit(main())
