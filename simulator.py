from dbhelper import Databasehelper
from random import uniform
from collections import defaultdict
class Simulator:
    def __init__(self):
        self.temperatures:list = [31,34,36,35,32]
        self.db = Databasehelper()

    def getTotalConsumption(self, appliances:list) -> list:
        weeklyconsumption = []
        self.db_appliances = self.db.getall_users('appliance')

        for _ in range(7):  # Loop for 7 days
            totalConsumption = 0
            for appliance_record in self.db_appliances:
                for appliance in appliances:
                    if appliance == appliance_record['appliancename']:
                        # Generate a random adjustment for hours of use
                        random_hour = uniform(0, 4)
                        adjusted_hours = float(appliance_record['hours_use']) - random_hour
                        adjusted_hours = max(0, adjusted_hours)  # Ensure no negative hours
                        
                        # Calculate consumption for this appliance
                        print(f'{appliance} found!\nWattage: {appliance_record["watt"]}\nAdjusted Hours of Use: {adjusted_hours}')
                        totalConsumption += appliance_record['watt'] * adjusted_hours / 1000  # Convert to kWh

            weeklyconsumption.append(round(totalConsumption, 2))

        print(f"Total Weekly Consumption{weeklyconsumption}")
        return weeklyconsumption


    def getTotalSolarKWH_Production(self,type,quantity)->list:
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

        return days_list

    def getTotalCarbonEmissions(self, tariff_company, totalConsumption: list) -> list:
        COAL_C02_KWH = 1.1
        NATURALGAS_C02_KWH = 0.5

        # Define tariff company emission percentages
        company_emissions = {
            'MERALCO': {'coal_percentage': 0.5, 'naturalgas_percentage': 0.3},
            'VECO': {'coal_percentage': 0.6, 'naturalgas_percentage': 0.3},
            'TORECO': {'coal_percentage': 0.6, 'naturalgas_percentage': 0.0},
            'CEBECO': {'coal_percentage': 0.7, 'naturalgas_percentage': 0.0},
            'Aboitiz': {'coal_percentage': 0.6, 'naturalgas_percentage': 0.0}
        }

        # Get percentages for the selected company
        if tariff_company not in company_emissions:
            raise ValueError(f"Unsupported tariff company: {tariff_company}")

        coal_percentage = company_emissions[tariff_company]['coal_percentage']
        naturalgas_percentage = company_emissions[tariff_company].get('naturalgas_percentage', 0.0)

        # Calculate carbon emissions for each consumption value
        carbon_emissions = []
        for kwh in totalConsumption:
            carbonemission = (kwh * coal_percentage * COAL_C02_KWH) + \
                            (kwh * naturalgas_percentage * NATURALGAS_C02_KWH)
            carbon_emissions.append(round(carbonemission, 2))

        print(f"Carbon emissions for {tariff_company}: {carbon_emissions}")
        return carbon_emissions

            
    def deductkwhFromGreenEnergy(self, totalConsumption: list, totalGreenEnergy: list) -> list:
        # Ensure both lists have the same length
        if len(totalConsumption) != len(totalGreenEnergy):
            raise ValueError("Total consumption and green energy lists must have the same length!")

        # Subtract green energy from consumption for each day
        weekly_deducted_green = [
            max(0, kwh - green) for kwh, green in zip(totalConsumption, totalGreenEnergy)
        ]

        print('KWH LIST DEDUCTED BY GREEN ENERGY')
        print(weekly_deducted_green)
        return weekly_deducted_green
              

    def getTotalCosts(self, totalConsumption, tariffRate, tariffType):
        print(f"Processing Total Consumption: {totalConsumption}")
        print(f"Length of Total Consumption: {len(totalConsumption)}")

        weekly_cost = []
        for kwh in totalConsumption:
            cost = round(kwh * float(tariffRate), 2)
            weekly_cost.append(cost)
            print(f"KWH: {kwh}, Tariff Rate: {tariffRate}, Cost: {cost}")

        print(f"Weekly Costs: {weekly_cost}")
        return weekly_cost

    def getTotalCostwithGreenEnergy(self, totalConsumption: list, totalGreenEnergy: list, tariffRate: int, tariffType: str) -> list:
        weekly_cost_green = []
        weekly_deducted_green = []

        # Ensure both lists have the same length
        if len(totalConsumption) != len(totalGreenEnergy):
            raise ValueError("Total consumption and green energy lists must have the same length!")

        # Iterate over the values of totalConsumption and totalGreenEnergy
        for kwh, green in zip(totalConsumption, totalGreenEnergy):
            # Deduct green energy from total consumption
            deducted_from_green_energy = max(0, kwh - green)  # Avoid negative values
            weekly_deducted_green.append(deducted_from_green_energy)

        print('KWH LIST DEDUCTED BY GREEN ENERGY')
        print(weekly_deducted_green)

        # Calculate cost for each day
        for greenkwh in weekly_deducted_green:
            cost = greenkwh * float(tariffRate)
            weekly_cost_green.append(round(cost, 2))

        print('KWH LIST DEDUCTED BY GREEN ENERGY CALCULATED ITS EQUIVALENT COST')
        print(weekly_cost_green)
        return weekly_cost_green


    def getTotalConsumption2(self, appliances: list) -> dict:
        # Weekly consumption grouped by appliance type
        weekly_consumption = defaultdict(list)
        
        # Fetch appliance data
        self.db_appliances = self.db.getall_users('appliance')
        
        # Organize appliances by their types
        appliances_by_type = defaultdict(list)
        for appliance_record in self.db_appliances:
            appliance_type = appliance_record['type']  # Assume a 'type' field exists in the database
            appliances_by_type[appliance_type].append(appliance_record)
        
        # Simulate daily consumption for 7 days
        for _ in range(7):
            daily_consumption_by_type = defaultdict(float)
            
            for appliance_type, appliance_records in appliances_by_type.items():
                for appliance_record in appliance_records:
                    if appliance_record['appliancename'] in appliances:
                        # Simulate random hours of use
                        random_hour = uniform(0,4)
                        # Don't deduct hours_use if the hours of use is less than 5 to avoid zero values.
                        if not appliance_record['hours_use'] < 1:
                            adjusted_hours = max(0, float(appliance_record['hours_use']) - random_hour)
                        else:
                            random_hour = uniform(0.01, 0.2)
                            adjusted_hours = float(appliance_record['hours_use']) - random_hour
                        # Calculate kWh consumption
                        kwh_consumption = (appliance_record['watt'] * adjusted_hours) / 1000
                        
                        # Accumulate daily consumption by type
                        daily_consumption_by_type[appliance_type] += float(kwh_consumption)
            
            # Append daily totals to weekly totals
            for appliance_type, daily_total in daily_consumption_by_type.items():
                weekly_consumption[appliance_type].append(round(daily_total, 2))
        
        # Debug output
        print("Weekly Consumption by Type:")
        for appliance_type, daily_totals in weekly_consumption.items():
            print(f"{appliance_type}: {daily_totals}")
        
        return weekly_consumption


if __name__ == "__main__":
    from simulator import Simulator
    sim = Simulator()
    appliances:list = ['Electric Stove', 'Heater', 'Coffee Maker', 'Lamp', 'House Lighting', 
                       'RGB Lighting', 'Christmas Lights', 'Ceiling Fan', 'Electric Fan', 
                       'Washing Machine', 'Clothes Iron', 'Refrigerator', 'Oven', 'Rice Cooker']
    totalConsumption = [7.53,5.66,8.56,5.36,7.15,8.67,8.14]
    totalGreenEnergy = [3.42,4.12,3.46,3.67,4.55,5.61,4.86]
    tariffRate = 12
    tariffType = 'TOU'
    # print(f"TOTAL WITHOUT KWH COST: {totalConsumption}\nWith Cost | Pesos:")
    # print(sim.getTotalCosts(totalConsumption=totalConsumption,tariffRate=tariffRate,tariffType=tariffType))
    # print(f"TOTAL WITHOUT KWH COST (2): {totalConsumption}\nWith Cost deducted from Green Energy | Pesos:")
    # print(sim.getTotalCostwithGreenEnergy(totalConsumption=totalConsumption,totalGreenEnergy=totalGreenEnergy,tariffRate=tariffRate,tariffType=tariffType))
    print(f"WEEKLY CARBON EMISSION FROM MERALCO: {sim.getTotalCarbonEmissions(tariff_company='MERALCO',totalConsumption=totalConsumption)}")
    print(f"Total Carbon Emission MERALCO: {sum(sim.getTotalCarbonEmissions(tariff_company='MERALCO',totalConsumption=totalConsumption)):.2f}kg C02\n\n\n")

    print(f"Weekly KWH Deducted by Green Energy{sim.deductkwhFromGreenEnergy(totalConsumption=totalConsumption,totalGreenEnergy=totalGreenEnergy)}")
    print(f"WEEKLY CARBON EMISSION FROM MERALCO WITH GREEN ENERGY:{sim.getTotalCarbonEmissions(tariff_company='MERALCO',totalConsumption=sim.deductkwhFromGreenEnergy(totalConsumption=totalConsumption,totalGreenEnergy=totalGreenEnergy))}")
    print(f"Total Carbon Emission MERALCO WITH GREEN ENERGY: {sum(sim.getTotalCarbonEmissions(tariff_company='MERALCO',totalConsumption=sim.deductkwhFromGreenEnergy(totalConsumption=totalConsumption,totalGreenEnergy=totalGreenEnergy))):.2f} kg C02")
