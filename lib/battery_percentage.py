class BatteryPercent:
    def __init__(self, adc1=3860, U1=8.21, adc2=3480, U2=7.54):
        self.adc1 = adc1
        self.U1 = U1
        self.adc2 = adc2
        self.U2 = U2
        self.a = (self.U1 - self.U2) / (self.adc1 - self.adc2)
        self.b = self.U2 - self.a * self.adc2

    def batt_voltage(self, adc_v):
        u_batt = self.a * adc_v + self.b
        return u_batt

    def batt_percentage(self, u_batt):
        without_offset = (u_batt - 6) 
        normalized = without_offset / (8.4 - 6)
        percent = normalized * 100
        return percent