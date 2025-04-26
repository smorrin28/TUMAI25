import numpy as np
from decimal import Decimal, getcontext
from simplekml import Kml

def create_kml(positions: list[tuple[float, float, float]]):
    kml = Kml()
    track = kml.newgxtrack(name="Drone flight Path")
    
    for position in positions:
        track.newgxcoord([position])
        
    kml.save("drone_flight_track.kml")