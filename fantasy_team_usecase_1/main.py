import logging
import sys

from fantasy_team_usecase_1.factories import PlayerFactory
from fantasy_team_usecase_1.team import CurrentTeam
from fantasy_team_usecase_1.observers import RealTimeUIUpdater
from fantasy_team_usecase_1.strategies import BudgetValidation, SquadSizeValidation, PositionValidation
from fantasy_team_usecase_1.singletons import DatabaseManager, APIService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Fantasy Team Builder application.")

    try:
        api_service = APIService()
        raw_players = api_service.fetch_player_data()
        
        available_players = []
        for data in raw_players:
            player = PlayerFactory.create_player(data)
            available_players.append(player)
            
        logger.info(f"Successfully loaded {len(available_players)} players from dataset.")

        my_team = CurrentTeam("Bil482 All Stars")
        ui_component = RealTimeUIUpdater()
        my_team.attach(ui_component) 

        for i, player in enumerate(available_players):
            if i >= 15: # Full FPL squad
                break
            my_team.add_player(player)
            
        my_team.add_validation_strategy(BudgetValidation(max_budget=150.0))
        my_team.add_validation_strategy(SquadSizeValidation(target_size=15))
        
        from fantasy_team_usecase_1.strategies import TeamLimitValidation
        my_team.add_validation_strategy(TeamLimitValidation(max_players_per_team=3))
        
        my_team.add_validation_strategy(PositionValidation({
            "Goalkeeper": 2,
            "Defender": 5,
            "Midfielder": 5,
            "Forward": 3
        }))
        
        logger.info("Validating current team configuration...")
        if my_team.save_team():
            db_manager = DatabaseManager()
            db_manager.connect()
            db_manager.save_team(my_team)
            logger.info("Application executed successfully.")
        else:
            logger.warning("Initial squad validation failed.")
            
    except Exception as e:
        logger.error(f"Application encountered an error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
