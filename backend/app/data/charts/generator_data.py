from app.db.db_manager import DatabaseManager
from app.config.generator_list import generators

FUEL_CAPACITY = 8983

class Generator:
    def __init__(self, name, fuelInput):
        self.name = name
        self.fuelInput = fuelInput
        self.capacity = FUEL_CAPACITY
        self.estimatedFill = round(self.fuelInput / 100 * self.capacity)
        self.fuel_color = self.get_fuel_color()

    def get_fuel_color(self):
        if self.fuelInput <= 25:
            return 'rgb(255,0,0)'  # Red
        elif 25 < self.fuelInput <= 75:
            return 'rgb(255,255,0)'  # Yellow
        else:
            return 'rgb(0,128,0)'  # Green

def get_generator_data(month="december"):
    db_manager = DatabaseManager()
    raw_gen_data = {gen: db_manager.get_gen_data(month=month, generator=gen)['post'] for gen in generators}
    
    gen_data = []
    for gen in raw_gen_data.keys():
        if raw_gen_data[gen]['fuel_level'] != 0:
            gen_data.append(Generator(gen, raw_gen_data[gen]['fuel_level']))
    
    return gen_data

def calculate_fuel_metrics(gen_data):
    total_capacity = sum(FUEL_CAPACITY for gen in gen_data)
    total_current_fuel = sum((gen.fuelInput / 100) * FUEL_CAPACITY for gen in gen_data)
    total_fuel_delta = total_capacity - total_current_fuel
    estimated_cost_to_fill = total_fuel_delta * 4.25
    
    return {
        'total_capacity': total_capacity,
        'total_current_fuel': total_current_fuel,
        'total_fuel_delta': total_fuel_delta,
        'estimated_cost_to_fill': estimated_cost_to_fill
    }