from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from core.database import get_db_connection

router = APIRouter(prefix="/team", tags=["Team Builder"])

class TeamCreate(BaseModel):
    name: str
    player_ids: List[int]
    captain_id: int = 0
    bench_ids: List[int] = []

@router.post("")
def create_team(team: TeamCreate):
    from fantasy_team_usecase_1.team import CurrentTeam
    from fantasy_team_usecase_1.strategies import BudgetValidation, SquadSizeValidation, PositionValidation, TeamLimitValidation
    from fantasy_team_usecase_1.factories import PlayerFactory
    from fantasy_team_usecase_1.observers import RealTimeUIUpdater
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        placeholders = ",".join("?" * len(team.player_ids))
        query = f'''
            SELECT id, first_name, second_name, team, position_id, cost 
            FROM players WHERE id IN ({placeholders})
        '''
        c.execute(query, team.player_ids)
        rows = c.fetchall()
        
        db_players = {}
        for row in rows:
            db_players[row['id']] = {
                "id": row['id'], "first_name": row['first_name'], "second_name": row['second_name'],
                "team": row['team'], "position": row['position_id'], "cost": row['cost'],
                "is_captain": row['id'] == team.captain_id, "is_bench": row['id'] in team.bench_ids
            }
            
        if len(db_players) != len(team.player_ids):
            raise HTTPException(status_code=400, detail="One or more players not found in database.")
            
        user_team = CurrentTeam()
        user_team.attach(RealTimeUIUpdater())
        
        user_team.add_validation_strategy(BudgetValidation(150.0))
        user_team.add_validation_strategy(SquadSizeValidation(15))
        user_team.add_validation_strategy(PositionValidation({"Goalkeeper": 2, "Defender": 5, "Midfielder": 5, "Forward": 3}))
        user_team.add_validation_strategy(TeamLimitValidation(3))
        
        for p_id in team.player_ids:
            p_data = db_players[p_id]
            is_cap = p_data["is_captain"]
            is_b = p_data["is_bench"]
            player_obj = PlayerFactory.create_player(p_data)
            user_team.add_player(player_obj)
            
        total_cost = sum([p.cost for p in user_team.players])
        c.execute("INSERT INTO user_teams (name, budget_used) VALUES (?, ?)", (team.name, total_cost))
        team_id = c.lastrowid
        
        team_players_data = [(team_id, p_id, db_players[p_id]["is_captain"], db_players[p_id]["is_bench"]) for p_id in team.player_ids]
        c.executemany("INSERT INTO team_players (team_id, player_id, is_captain, is_bench) VALUES (?, ?, ?, ?)", team_players_data)
        
        conn.commit()
        return {"message": f"Team '{team.name}' created successfully with {len(team.player_ids)} players.", "team_id": team_id}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/{team_id}")
def get_team(team_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT id, name, budget_used FROM user_teams WHERE id = ?", (team_id,))
    team = c.fetchone()
    
    if not team:
        conn.close()
        raise HTTPException(status_code=404, detail="Team not found")
        
    query = '''
        SELECT p.id, p.first_name, p.second_name, p.team, p.position_id, p.cost,
               s.total_points, tp.is_captain, tp.is_bench
        FROM team_players tp
        JOIN players p ON tp.player_id = p.id
        LEFT JOIN stats s ON p.id = s.player_id AND s.gameweek = (SELECT MAX(gameweek) FROM stats)
        WHERE tp.team_id = ?
    '''
    c.execute(query, (team_id,))
    players = [dict(row) for row in c.fetchall()]
    conn.close()
    
    from fantasy_points_usecase_2.calculator import TeamPointCalculator
    calc = TeamPointCalculator()
    gw_score = calc.calculate_team_score(players)
    
    return {
        "team_id": team['id'], "name": team['name'], "budget_used": team['budget_used'],
        "total_score": gw_score, "players": players
    }
