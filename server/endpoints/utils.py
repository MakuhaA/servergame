import pickle
from logging import INFO, getLogger
from socket import socket
from sqlite3 import Connection, Cursor
from time import sleep

from general.enums import RequestData, ResponseData, ServerEndpoint


logger = getLogger(__name__)
logger.setLevel(INFO)


def pinger(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    return ResponseData(data, key_code=ServerEndpoint.Pong), [sock]


def admin_permission(
    _: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    addr = server.addresses[server.users.index(sock)]
    ip, port = addr[0], addr[1]
    cur.execute(
        'UPDATE users SET name=? WHERE ip=? AND port=?',
        ('admin', ip, port),
    )
    con.commit()
    server.admin_sock.append(sock)
    return ResponseData(), [sock]


def admin_adds_new_team(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    team_name = data[0]
    logger.info(f'Admin try to add new team with name {team_name}')

    if server.teams_count + 1 > 6:
        logger.info('Maximum of teams already reached!')
        return ResponseData(
            data=False,
            key_code=ServerEndpoint.AdminButtonAddNewTeam,
        ), [sock]
    server.teams_count += 1
    cur.execute(
        'INSERT INTO teams VALUES (?, ?, 0, NULL)',
        (server.teams_count, team_name),
    )
    con.commit()

    team_names = cur.execute('SELECT name FROM teams').fetchall()
    key_code = ServerEndpoint.GetTeamsList
    response_data = [str(name[0]) for name in team_names]
    logger.info(f'Teams names: {response_data}')
    response = ResponseData(response_data, key_code=key_code)
    return response, server.users


def get_teams_list(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    logger.info('User try to get teams list')
    team_names = cur.execute('SELECT name FROM teams').fetchall()
    key_code = ServerEndpoint.GetTeamsList
    response_data = [str(name[0]) for name in team_names]
    logger.info(f'Teams names: {response_data}')
    response = ResponseData(response_data, key_code=key_code)
    return response, [sock]


def admin_delete_team(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    row = int(data[0]) + 1
    logger.info(f'Admin try to delete team with id {row}')
    cur.execute('DELETE FROM teams WHERE id=?;', (str(row),))
    con.commit()
    server.teams_count = cur.execute('SELECT COUNT(*) FROM teams').fetchall()[
        0
    ][0]
    for i in range(row, server.teams_count + 1):
        cur.execute('UPDATE teams SET id=? WHERE id=?', (i, i + 1))
        con.commit()

    # Send to client updated version
    team_names = cur.execute('SELECT name FROM teams').fetchall()
    key_code = ServerEndpoint.GetTeamsList
    response_data = [str(name[0]) for name in team_names]
    logger.info(f'Teams names after deleting: {response_data}')
    return ResponseData(response_data, key_code=key_code), server.users


def admin_change_team_capacity(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    capacity_team = data[0]
    cur.execute('UPDATE teams SET capacity=?', (capacity_team,))
    con.commit()
    return ResponseData(), []


def admin_change_timer(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    server.timer_secs = int(data[0])
    key_code = ServerEndpoint.AdminChangeTimer
    response_data = str(server.timer_secs)
    send_to = server.users
    return ResponseData(response_data, key_code=key_code), send_to


def admin_change_current_task(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    server.current_task = data[0]
    key_code = ServerEndpoint.AdminChangeCurrentTask
    return ResponseData(server.current_task, key_code=key_code), server.users


def admin_start_competition(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    response = ResponseData(
        key_code=ServerEndpoint.AdminStartCompetition,
    )
    response = pickle.dumps(response)
    for user in server.users:
        user.send(response)
    sleep(1)
    key_code = ServerEndpoint.YourTurn
    send_to = []
    if len(server.socket_team1) != 0:
        send_to.append(server.socket_team1[server.team1_queue])
    if len(server.socket_team2) != 0:
        send_to.append(server.socket_team2[server.team2_queue])
    if len(server.socket_team3) != 0:
        send_to.append(server.socket_team3[server.team3_queue])
    if len(server.socket_team4) != 0:
        send_to.append(server.socket_team4[server.team4_queue])
    if len(server.socket_team5) != 0:
        send_to.append(server.socket_team5[server.team5_queue])
    if len(server.socket_team6) != 0:
        send_to.append(server.socket_team6[server.team6_queue])
    return (
        ResponseData(
            key_code=key_code,
        ),
        send_to,
    )


def stop_reset_button(
    data: RequestData.data,
    sock: socket,
    con: Connection,
    cur: Cursor,
    server,
) -> tuple[ResponseData, list[socket]]:
    send_to = server.users
    main_key_code = ServerEndpoint.StopResetButton
    response = ResponseData(
        key_code=main_key_code,
    )
    for i in range(1, 7):
        server_team_queue = eval(f'server.team{i}_queue')
        server_current_turn = eval(f'server.team{i}_current_turn')
        server_team_queue, server_current_turn = 0, 0
    return response, send_to
