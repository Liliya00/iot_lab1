
from csv import reader
from datetime import datetime

from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
from domain.parking import Parking


class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
        parking_filename: str = None
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename

        self.acc_file = None
        self.gps_file = None
        self.parking_file = None

        self.acc_reader = None
        self.gps_reader = None
        self.parking_reader = None

    def startReading(self, *args, **kwargs):
        self.acc_file = open(self.accelerometer_filename, "r")
        self.gps_file = open(self.gps_filename, "r")

        self.acc_reader = reader(self.acc_file)
        self.gps_reader = reader(self.gps_file)

        next(self.acc_reader, None)
        next(self.gps_reader, None)

        if self.parking_filename:
            self.parking_file = open(self.parking_filename, "r")
            self.parking_reader = reader(self.parking_file)
            next(self.parking_reader, None)

    def read(self) -> AggregatedData:
        try:
            acc_row = next(self.acc_reader)
            gps_row = next(self.gps_reader)
        except StopIteration:
            self.stopReading()
            self.startReading()

            acc_row = next(self.acc_reader)
            gps_row = next(self.gps_reader)

        accelerometer = Accelerometer(
            x=int(float(acc_row[0])),
            y=int(float(acc_row[1])),
            z=int(float(acc_row[2]))
        )

        gps = Gps(
            longitude=float(gps_row[0]),
            latitude=float(gps_row[1])
        )

        return AggregatedData(
            accelerometer=accelerometer,
            gps=gps,
            timestamp=datetime.now(),
            user_id=1
        )

    def readParking(self) -> Parking:
        if not self.parking_reader:
            return None

        try:
            parking_row = next(self.parking_reader)
        except StopIteration:
            self.parking_file.close()
            self.parking_file = open(self.parking_filename, "r")
            self.parking_reader = reader(self.parking_file)
            next(self.parking_reader, None)
            parking_row = next(self.parking_reader)

        gps = Gps(
            longitude=float(parking_row[1]),
            latitude=float(parking_row[2])
        )

        return Parking(
            empty_count=int(float(parking_row[0])),
            gps=gps
        )

    def stopReading(self, *args, **kwargs):
        if self.acc_file:
            self.acc_file.close()

        if self.gps_file:
            self.gps_file.close()

        if self.parking_file:
            self.parking_file.close()
