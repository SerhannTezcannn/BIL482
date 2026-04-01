from abc import ABC, abstractmethod

class ScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, stats: dict) -> int:
        pass

    def _calculate_common_points(self, stats: dict) -> int:
        minutes = stats.get('minutes', 0)
        if minutes == 0:
            return 0
            
        score = 2 if minutes >= 60 else 1
        
        score -= stats.get('yellow_cards', 0) * 1
        score -= stats.get('red_cards', 0) * 3
        score += stats.get('bonus', 0)
        
        return score

class GoalkeeperScoringStrategy(ScoringStrategy):
    def calculate_score(self, stats: dict) -> int:
        if stats.get('minutes', 0) == 0:
            return 0
            
        score = self._calculate_common_points(stats)
        
        score += stats.get('clean_sheets', 0) * 4
        score += stats.get('saves', 0) // 3
        score -= stats.get('goals_conceded', 0) // 2
        
        score += stats.get('goals', 0) * 6
        score += stats.get('assists', 0) * 3
        
        if stats.get('saves', 0) >= 5:
            score += 2
            
        if stats.get('venue') == 'Away' and stats.get('clean_sheets', 0) > 0:
            score += 2
            
        return score

class DefenderScoringStrategy(ScoringStrategy):
    def calculate_score(self, stats: dict) -> int:
        if stats.get('minutes', 0) == 0:
            return 0
            
        score = self._calculate_common_points(stats)
        
        score += stats.get('clean_sheets', 0) * 4
        score -= stats.get('goals_conceded', 0) // 2
        score += stats.get('goals', 0) * 6
        score += stats.get('assists', 0) * 3
        
        result = str(stats.get('result', '')).lower()
        if 'win' in result and stats.get('goals_conceded', 0) == 0:
            score += 2
            
        return score

class MidfielderScoringStrategy(ScoringStrategy):
    def calculate_score(self, stats: dict) -> int:
        if stats.get('minutes', 0) == 0:
            return 0
            
        score = self._calculate_common_points(stats)
        
        score += stats.get('clean_sheets', 0) * 1
        score += stats.get('goals', 0) * 5
        score += stats.get('assists', 0) * 3
        
        minutes = stats.get('minutes', 0)
        try:
            ict = float(stats.get('ict_index', 0.0) or 0.0)
        except ValueError:
            ict = 0.0
            
        if minutes == 90 and ict >= 8.0:
            score += 2
            
        return score

class ForwardScoringStrategy(ScoringStrategy):
    def calculate_score(self, stats: dict) -> int:
        if stats.get('minutes', 0) == 0:
            return 0
            
        score = self._calculate_common_points(stats)
        
        score += stats.get('goals', 0) * 4
        score += stats.get('assists', 0) * 3
        
        try:
            ict = float(stats.get('ict_index', 0.0) or 0.0)
        except ValueError:
            ict = 0.0
            
        if stats.get('goals', 0) == 0 and stats.get('assists', 0) == 0 and ict >= 10.0:
            score += 3
            
        return score

class ModifierStrategy(ScoringStrategy):
    def __init__(self, base_strategy: ScoringStrategy, multiplier: int):
        self.base_strategy = base_strategy
        self.multiplier = multiplier
        
    def calculate_score(self, stats: dict) -> int:
        base_score = self.base_strategy.calculate_score(stats)
        return base_score * self.multiplier
