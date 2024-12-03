from time import sleep
appliances = {
    'heater':
       {'watt': 100}
       ,
    'aircon':
        {'watt': 500}
        ,
    'electric fan':
        {'watt': 150}
        ,
    'television':
    {'watt': 1500}
}
totalwatt:int = 0
perhourwatt:int = 0
panels = {
    1: {'mono':
        {'watt':400}
    },
    2:{'polo':
       {'watt':300}
    },
    3:{'thin-film'}

}

selected_appliances = ['heater', 'electric fan','television']

for appliance in selected_appliances:
    totalwatt += appliances[appliance]['watt']
n=0
for i in range(10,14):
    n+=1
    perhourwatt = totalwatt * n 
    print(f"Wattage Consumed at {i}:00 : -> {perhourwatt}")
    sleep(3)

kwh = perhourwatt/1000
print(f'Total kWH: {kwh}')