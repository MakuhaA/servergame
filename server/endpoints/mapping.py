import typing as tp

from general.enums import ServerEndpoint

from .utils import (
    admin_adds_new_team,
    admin_change_current_task,
    admin_change_team_capacity,
    admin_change_timer,
    admin_delete_team,
    admin_permission,
    admin_start_competition,
    get_teams_list,
    pinger,
    stop_reset_button,
)


# map endpoint to function
EndpointMapper: dict[ServerEndpoint, tp.Callable] = {
    ServerEndpoint.Ping: pinger,  #
    ServerEndpoint.AdminPermission: admin_permission,  #
    ServerEndpoint.AdminButtonAddNewTeam: admin_adds_new_team,  #
    ServerEndpoint.GetTeamsList: get_teams_list,  #
    ServerEndpoint.AdminDeleteTeam: admin_delete_team,  #
    ServerEndpoint.AdminChangeTeamCapacity: admin_change_team_capacity,  #
    ServerEndpoint.AdminChangeTimer: admin_change_timer,  #
    ServerEndpoint.AdminChangeCurrentTask: admin_change_current_task,  #
    ServerEndpoint.AdminStartCompetition: admin_start_competition,  #
    ServerEndpoint.StopResetButton: stop_reset_button,  #
}
