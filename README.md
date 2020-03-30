# PalsePoint

PalsePoint is a simple program designed to automatically control a Wi-Fi smart switch based on the user's heart rate. Once the user's heart rate hits the tipping point (switchpoint), the switch turns on. The idea is that this would allow you to connect any fan you have to this switch and effectively now have a simple smart fan similar to the Wahoo Kickr Headwind. This program will allow you to finish your workout completely hands free. Need to take a break, but don't want to get off the trainer to turn off the fan? Or must head to the bathroom quickly? No problem, your fan will only turn on when it is needed.

## Installation

Note that this project only works on Windows and with an EdiMax smart switch. To install simply clone/download this repo and make sure you have Python3 installed. However, if you do not have an EdiMax switch, do not be discouraged. Provided your smart plug has an open API, you should be able to write a module like lean_smartplug.py.

## Usage
```bash
python PalsePoint.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
