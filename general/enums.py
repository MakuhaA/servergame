from enum import Enum, unique


@unique
class ServerEndpoint(str, Enum):
    Pong = "PONG"
    Ping = "ping"
    ButtonGetInTeam = "button4"
    AdminPermission = "admin_rights_permission_3223"
    AdminButtonAddNewTeam = "admin_b4"
    GetTeamsList = "b29"
    AdminDeleteTeam = "admin_b13"
    UpdatePlayersList = "b4con"
    LeaveTeam = "button5c"
    AdminChangeTeamCapacity = "admin_b5"
    AdminChangeTimer = "admin_b6"
    AdminChangeCurrentTask = "admin_b7"
    AdminStartCompetition = "admin_starts"
    PushButton1 = "push_button_1"
    PushButton2 = "push_button_2"
    PushButton3 = "push_button_3"
    StopResetButton = "STOP_RESET"
    ResultFinal = "result_final"
    YourTurn = "your_turn"


class RequestData:
    endpoint = None
    data = None

    def __init__(self, endpoint=None, data=None):
        self.endpoint = endpoint
        self.data = data

    def __str__(self):
        return f"RequestData({self.endpoint=}, {self.data=})"


class ResponseData:
    data: list[str] | None = None
    key_code = None

    def __init__(
            self,
            data=None,
            key_code=None
    ):
        self.data = data
        self.key_code = key_code

    def __str__(self):
        return f"ResponseData({self.data=}, {self.key_code=})"
