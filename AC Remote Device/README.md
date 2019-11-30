# AC Remote Device

## About
This is a device used to monitor the temperature, humidity, pressure and light intensity from the daylight inside a indoor environment, and also perform certain action to control the air conditioner. It helps to analyse the indoor environment properties which the target user is staying. The data this device collected will be sent to the online server, and by combining this data and other data collected from other devices, a group of environment properties will be sent to the reinforcement learning agent. The reinforcement learning agent will send a control signal according to the update rate. And this device will receive the control signal and perform the action.

## Electronic Part
### Device Schematics
[Link to diagram, created by Draw.io](https://www.draw.io/#Aeddylau328%2Ffyp-artificial-intelligence-ac-control-device%2Fmaster%2FAC%20Remote%20Device%2FAC_Remote_Device_Electronic_Diagram)

### Development Process
#### Reading Environment Status
In order to collect the temperature, humidity, pressure and light intensity, this device used three integrated modules, which are BMP180, BH1750 and HTU21D. For BMP180, it collects the barometric pressure. For BH1750, it collects the light intensity from the sun. For HTU21D, it collects the indoor temperature and humidity. By using the corresponding arduino libraries, the device can receive the signals generate by differenet sensors and output the correct value.

![Integrated Modules Connection img](../Project Record/AC remote DEV/environment reading/img_environment_reading_connection.jpg "Integrated Modules Connection")
It shows that the connection betweeen the three integrated modules and Arudino Mega 2560.

Here is the test of reading the indoor environment.
![Environment Reading Test img](../Project Record/AC remote DEV/environment reading/img_environment_reading_test.jpg "Environment Reading Test")
![Environment Reading Test vid](../Project Record/AC remote DEV/environment reading/vid_environment_reading_test.mp4 "Environment Reading Test")