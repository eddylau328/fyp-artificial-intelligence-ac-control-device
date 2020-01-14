# Reference

## Machine Learning
### Reinforcement Learning
#### [Monte Carlo Methods](./Monte Carlo Methods.pdf)
It introduces the monte carlo methods. It explains First-visit Monte Carlo Policy Evaluation, on-policy Monte Carlo Control and off-policy Monte Carlo Control. It also provides some explaination about the blackjack example.

#### [Create custom gym environments from scratch — A stock market example](https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e)
It shows how to create an environment in gym, which is a python library.

## Air Conditioner
### Power Consumption
#### [Ideal Air Conditioner temperature for electricity savings](https://www.bijlibachao.com/air-conditioners/ideal-air-conditioner-temperature-for-electricity-saving.html)
This website talks about the working methods of compressor, thermostat, and some basic air conditioner concepts.

## Electronics
### Sensors
#### [HTU21D](./HTU21D_datasheet.pdf)
- VIN max = 3.6V
- SDA, SCL max = 3.6V
- SDA, SCL min = 70% * VIn
- Current consumption
    - Measuring
        - Min 300 μA
        - TYP 450 μA
        - MAX 500 μA

#### [BH1750](./BH1750 datasheet.pdf)
- VIN = 3.3V
- SDA, SCL max = 5V
- Supply Current
    - TYP 120 μA
    - MAX 190 μA
- [schematics](./BH1750 SCH.pdf)

#### [BMP180](./BMP180_datasheet.pdf)
- VIN max = 3.6V
- SDA, SCL max = 3.6V
- Current consumption
    - Peak current
        - TYP 650 μA
        - MAX 1000 μA
    - Standard Mode
        - 5 μA

## Other projects
#### [Smart Sensors Enable Smart Air Conditioning Control](./sensors-14-11179.pdf)
This project aims to use the smart sensors to control the air conditioner. It is very similar to the device my project is doing. However, it does not use a machine learning program to determine the human motion. Also, it only detect the motion and sleeping rate. But my project aims to detect the activity type and classify it into different metabolic rate.

#### [Mobile User Indoor-Outdoor Detection through Physical Daily Activities](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6387420/)
This project aims to use the built-in sensors inside the mobile to detect the user activity whether it is indoor or outdoor activities.

