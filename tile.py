class Tile:
    def __init__(self, crop_type, planted_on: int):
        self.crop_type = crop_type
        self.planted_on = planted_on
    
    def get_days_since_planting(self, today: int) -> int:
        return today - self.planted_on
    
    def has_matured(self, today: int) -> bool:
        return self.get_days_since_planting(today) >= self.crop_type['daysToMature']


    def harvest_today(self, today: int) -> bool:
        if not self.has_matured(today):
            return False

        age = self.get_days_since_planting(today)
        return (age - self.crop_type['daysToMature']) % self.crop_type['regrowth'] == 0