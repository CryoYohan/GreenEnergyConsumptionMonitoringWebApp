from dbhelper import Databasehelper
from random import uniform
class Simulator:
    def __init__(self):
        self.temperatures:list = [31,34,36,35,32]
        self.db = Databasehelper()

    def getTotalConsumption(self, appliances:list):
        totalConsumption = 0
        self.db_appliances = self.db.getall_users('appliance')
        for appliance_record in self.db_appliances:
            for appliance in appliances:
                if appliance == appliance_record['appliancename']:
                    print(f'{appliance} found!\nWattage: {appliance_record['watt']}\nHours of Use: {appliance_record['hours_use']}')
                    totalConsumption+=appliance_record['watt'] * appliance_record['hours_use']
        
        print(f'DAILY\nTotal Consumption: {int(totalConsumption)} Watt\nTotal Consumption in KWH: {totalConsumption/1000:.2f} KWH')
        print(f'WEEKLY\nTotal Consumption: {int(totalConsumption)*7} Watt\nTotal Consumption in KWH: {totalConsumption*7/1000:.2f} KWH')
        print(f'MONTHLY\nTotal Consumption: {int(totalConsumption)*30} Watt\nTotal Consumption in KWH: {totalConsumption*30/1000:.2f} KWH')
        print(f'DAILY SOLAR PANEL GENERATION: {((400*5)*.20)*5} Watts | Kilowats: {(((400*5)*.20)*5)/1000} \nWEEKLY {((400*5)*.20)*(5*7)} Watts | KWH {((400*5)*.20)*(5*7) /1000}')
        

    def getTotalSolarKWH_Production(self,type,quantity):
        days_list = []
        watts: int = 0
        efficiency: float = 0.0
        optimal_temp: float = 0.0
        temp_coefficient: float = 0.0
        hours_of_use: float = 0.0
        totalKWH: float = 0.0
        solarpanels = self.db.getall_users(table='solarpanel')
        
        # Get solar panel specs from the database
        for panel in solarpanels:
            if panel['panelname'] == type:
                watts = panel['wattcapacity']
                efficiency = panel['efficiency']
                optimal_temp = panel['optimal_temp']
                temp_coefficient = panel['temp_coef']
                hours_of_use = panel['hours_use']
        
        # Simulate energy production over 7 days
        for _ in range(7):
            totalwattcapacity = watts * int(quantity)
            wattefficiency = totalwattcapacity * efficiency

            # Generate a random temperature within a realistic range
            random_temp = uniform(30, 40)  # e.g., temperatures between 20°C and 40°C
            temp_effect = 1 + (float(temp_coefficient)) * (random_temp - float(optimal_temp))
            adjusted_output = (float(wattefficiency) * temp_effect) * float(hours_of_use)
            days_list.append(round(adjusted_output / 1000,2))  # Convert to kWh

        # Print energy production for each day
        # days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        # for day, kwh in enumerate(days_list):
        #     print(f'{days[day]} - {kwh:.2f} KWH Produced')
        return days_list

    def getTotalCarbonEmissions(self,tariff_company,totalConsumption):
        pass

    def getTotalCosts(self, totalConsumption, tariffRate, tariffType):
        pass

if __name__ == "__main__":
    from simulator import Simulator
    sim = Simulator()
    appliances = ['Heater','PS5']
    sim.getTotalSolarKWH_Production('monocrystalline',20)
