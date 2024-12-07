from dbhelper import Databasehelper
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
        pass

    def getTotalCarbonEmissions(self,tariff_company,totalConsumption):
        pass

    def getTotalCosts(self, totalConsumption, tariffRate, tariffType):
        pass

if __name__ == "__main__":
    from simulator import Simulator
    sim = Simulator()
    appliances = ['Heater','PS5']
    sim.getTotalConsumption(appliances)
