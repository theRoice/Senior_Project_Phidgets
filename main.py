import traceback
import requests
from time import sleep

from Phidget22.Devices.HumiditySensor import HumiditySensor
from Phidget22.Devices.LightSensor import LightSensor
from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
from Phidget22.Devices.TemperatureSensor import *

sleep_time = 10 # adjust for testing/prod purposes
api_id = "29k3zp3n5l"
aws_region = "us-east-2"
api_gateway_url = f"https://{api_id}.execute-api.{aws_region}.amazonaws.com/test/sensors"

# Declare event handlers
# -----------------------------------------------------------------------------
def on_temperature_change(self, temperature):
    print("Temperature is: " + str(convert_celsius_to_fahrenheit(temperature)) + " degrees Fahrenheit.")
    sleep(sleep_time)

def on_illuminance_change(self, illuminance):
    # Illuminance is returned as lux
    print("Illuminance is: " + str(illuminance) + " lux.")
    sleep(sleep_time)

def humidity_sensor_change(self, humidity):
    # Humidity is returned as a percentage
    print("Humidity is: " + str(humidity) + "%.")
    sleep(sleep_time)

def on_voltage_ratio_change(self, voltage):
    # 0.0-0.2 = dry soil
    # 0.2-0.5 = moist soil
    # 0.5-1.0 = flooded soil
    soil_moisture_level = "unmeasured"
    if 0.0 < voltage <= 0.2:
        soil_moisture_level = "dry soil"
    elif 0.2 < voltage <= 0.5:
        soil_moisture_level = "moist soil"
    elif 0.5 < voltage <= 1.0:
        soil_moisture_level = "flooded soil"
    else:
        print(
            "Voltage of soil is currently at: " + str(voltage) + " which is out of bounds. Please check sensor connection."
        )
    print(f"Voltage of soil is: {str(voltage)} - indicating {soil_moisture_level}")
    sleep(sleep_time)
# -----------------------------------------------------------------------------


# Helper Methods
# -----------------------------------------------------------------------------
def check_if_measurement_changed(measurement_1, measurement_2):
    return abs(measurement_1 - measurement_2) > 0.001

# Define general methods
def convert_celsius_to_fahrenheit(temperature):
    return temperature * 9 / 5 + 32

def build_payload(measurement, user_id, user_plant_id, sensor_type, sensor_id):
    return {
        "measurement": measurement,
        "user_id": user_id,
        "user_plant_id": user_plant_id,
        "sensor_type": sensor_type,
        "sensor_id": sensor_id
    }

# -----------------------------------------------------------------------------


# API Calls
# -----------------------------------------------------------------------------
def send_temp_to_api(temperature, user_id, user_plant_id, sensor_id):
    print("Sending temperature to API")
    json_payload = build_payload(convert_celsius_to_fahrenheit(temperature), user_id, user_plant_id, "temperature", sensor_id)
    response = requests.post(api_gateway_url, json=json_payload)
    print(f"Sent: {json_payload}, Status: {response.status_code}")

def send_lux_to_api(lux, user_id, user_plant_id, sensor_id):
    print("Sending lux to API")
    json_payload = build_payload(lux, user_id, user_plant_id, "lux", sensor_id)
    response = requests.post(api_gateway_url, json=json_payload)
    print(f"Sent: {json_payload}, Status: {response.status_code}")

def send_humidity_to_api(humidity, user_id, user_plant_id, sensor_id):
    print("Sending humidity to API")
    json_payload = build_payload(humidity, user_id, user_plant_id, "humidity", sensor_id)
    response = requests.post(api_gateway_url, json=json_payload)
    print(f"Sent: {json_payload}, Status: {response.status_code}")

def send_voltage_to_api(voltage, user_id, user_plant_id, sensor_id):
    print("Sending voltage to API")
    json_payload = build_payload(voltage, user_id, user_plant_id, "voltage", sensor_id)
    response = requests.post(api_gateway_url, json=json_payload)
    print(f"Sent: {json_payload}, Status: {response.status_code}")
# -----------------------------------------------------------------------------


def main():
    user_id = "EricSensorTest"
    user_plant_id = "1"
    temperature_sensor_id = "0"
    light_sensor_id = "1"
    humidity_sensor_id = "2"
    voltage_sensor_id = "3"

    current_temperature = 0
    current_illuminance = 0
    current_humidity = 0
    current_voltage = 0

    try:

        # Phidget Initialization Start
        # -----------------------------------------------------------------------------
        # Create Phidget channels (name them in accordance with the port you tie them too)
        temperature_sensor_0 = TemperatureSensor()
        light_sensor_1 = LightSensor()
        humidity_sensor_2 = HumiditySensor()
        voltage_ratio_input_3 = VoltageRatioInput()

        # Set addressing parameters to specify which channel opens to sensor
        temperature_sensor_0.setHubPort(0)
        light_sensor_1.setHubPort(1)
        humidity_sensor_2.setHubPort(2)
        voltage_ratio_input_3.setHubPort(3)

        # Assign event handlers you need before calling open so that no events are missed
        temperature_sensor_0.setOnTemperatureChangeHandler(on_temperature_change)
        light_sensor_1.setOnIlluminanceChangeHandler(on_illuminance_change)
        humidity_sensor_2.setOnHumidityChangeHandler(humidity_sensor_change)
        voltage_ratio_input_3.setOnVoltageRatioChangeHandler(on_voltage_ratio_change)

        # Open Phidgets, wait for attachment, give a timeout time
        temperature_sensor_0.openWaitForAttachment(5000)
        light_sensor_1.openWaitForAttachment(5000)
        humidity_sensor_2.openWaitForAttachment(5000)
        voltage_ratio_input_3.openWaitForAttachment(5000)
        # -----------------------------------------------------------------------------
        # Phidget Initialization end


        # Logic Start
        # -----------------------------------------------------------------------------
        try:
            print("Polling sensors, press Ctrl-C to exit...")
            prev_temperature = current_temperature
            prev_illuminance = current_illuminance
            prev_humidity = current_humidity
            prev_voltage = current_voltage
            while True:
                current_temperature = temperature_sensor_0.getTemperature()
                current_illuminance = light_sensor_1.getIlluminance()
                current_humidity = humidity_sensor_2.getHumidity()
                current_voltage = voltage_ratio_input_3.getVoltageRatio()

                if check_if_measurement_changed(current_temperature, prev_temperature):
                    send_temp_to_api(current_temperature, user_id, user_plant_id, temperature_sensor_id)
                    prev_temperature = current_temperature
                if check_if_measurement_changed(current_illuminance, prev_illuminance):
                    send_lux_to_api(current_illuminance, user_id, user_plant_id, light_sensor_id)
                    prev_illuminance = current_illuminance
                if check_if_measurement_changed(current_humidity, prev_humidity):
                    send_humidity_to_api(current_humidity, user_id, user_plant_id, humidity_sensor_id)
                    prev_humidity = current_humidity
                if check_if_measurement_changed(current_voltage, prev_voltage):
                    send_voltage_to_api(current_voltage, user_id, user_plant_id, voltage_sensor_id)
                    prev_voltage = current_voltage
        except KeyboardInterrupt:
            print("Keyboard Interrupt. Exiting.\n")
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            pass
        # -----------------------------------------------------------------------------
        # Logic End


        # Close Phidgets connections cleanly
        # -----------------------------------------------------------------------------
        finally:
            temperature_sensor_0.close()
            light_sensor_1.close()
            humidity_sensor_2.close()
            voltage_ratio_input_3.close()
            print("Closed Phidgets\n")
        # -----------------------------------------------------------------------------


    except PhidgetException as ex:
        # Catch Phidget Exceptions here and print the error information.
        traceback.print_exc()
        print("")
        print("PhidgetException " + str(ex.code) + " (" + ex.description + "): " + ex.details)

main()