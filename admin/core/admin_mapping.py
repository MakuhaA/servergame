import typing as tp

from general.enums import ServerEndpoint

from .admin_core import (
    add_new_team,
    change_current_task,
    change_timer,
    get_teams_list,
    ponger,
    pushed_button_3,
    result_final,
    stop_reset,
)


EndpointMapper: dict[ServerEndpoint, tp.Callable] = {
    ServerEndpoint.Pong: ponger,
    ServerEndpoint.GetTeamsList: get_teams_list,
    ServerEndpoint.AdminButtonAddNewTeam: add_new_team,
    ServerEndpoint.AdminChangeTimer: change_timer,
    ServerEndpoint.AdminChangeCurrentTask: change_current_task,
    ServerEndpoint.ResultFinal: result_final,
    ServerEndpoint.PushButton3: pushed_button_3,
    ServerEndpoint.StopResetButton: stop_reset,
}
