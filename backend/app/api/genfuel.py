import json
from ..db.db_manager import DatabaseManager
from ..config.generator_list import generator_fuel_capacity


class GeneratorFuelEstimate:
    def __init__(self, generator_name, fuel_percentage, run_hours):
        self.generator_name = generator_name
        self.fuel_capacity = generator_fuel_capacity

        self.current_fuel_volume = round(
            fuel_percentage/100 * self.fuel_capacity)

        self.fuel_delta = self.fuel_capacity - self.current_fuel_volume

        self.run_hours = run_hours

    def __str__(self):
        return f"{self.generator_name}: {self.current_fuel_volume} gallons (needs {self.fuel_delta} gallons to be full)"

    def __repr__(self):
        return f"GeneratorFuelEstimate({self.generator_name}, {self.current_fuel_volume} gal)"

    def to_dict(self):
        return {
            "generator_name": self.generator_name,
            "fuel_capacity": self.fuel_capacity,
            "current_fuel_volume": self.current_fuel_volume,
            "fuel_delta": self.fuel_delta,
            "run_hours": self.run_hours
        }


class FuelEstimator:
    def __init__(self, month: str):
        self.db = DatabaseManager()
        self.post_data = self.db.all_gen_data(month, completed_only=True)
        self.generator_estimates = self._create_estimates()

    def _create_estimates(self):
        estimates = {}
        for gen, data in self.post_data.items():
            fuel_percentage = data['post'][0]
            run_hours = data['post'][2]
            estimates[gen] = GeneratorFuelEstimate(gen, fuel_percentage, run_hours)
        return estimates

    def total_fuel_needed(self):
        return sum(est.fuel_delta for est in self.generator_estimates.values())

    def estimate_fuel_cost(self, cost_per_gallon: float):
        return self.total_fuel_needed() * cost_per_gallon


    def get_estimates(self):
        return {gen: est.to_dict() for gen, est in self.generator_estimates.items()}

    def __str__(self):
        return f"FuelEstimator(generators={len(self.generator_estimates)}, total_needed={self.total_fuel_needed()})"

    def to_json(self):
        return json.dumps({"get_estimates": self.get_estimates(),
                           "total_fuel_needed": self.total_fuel_needed(),
                           "estimate_fuel_cost": self.estimate_fuel_cost(1.5),
                           })
