# Hacman door tap in/tap out
---
* Lets people tap in and out of the space
* Uses standard parts so easily replacable
* Reports status to the membership system
* Reports tap in to the membership system
* Error logging and alerting (coming soon)

---
## Setup

### Parts required
* Pi
* (for entry)
  * Arduino nano 
  * Fob reader 
* (for exit)
  * Arduino nano 
  * Fob reader 
* Relay board

### Programming the Arduinos
The Arduinos act as a middleperson between the fob readers and the Pi. They handle the fob reader, and present a serial interface, via the USB port. Handy.

Program the nano using [the sketch](Arduino/rfid2serial.ino)

### Programming the Pi
* Install blank raspbian
* Clone this repo
* Edit the config file
  * Copy `config.example.yaml`
  * Rename it `config.yaml`
  * Edit as needed (see below)
* Set up WiFi if needed
* Automation
  * access.py to be run on startup ideally monitored so if it crashes out it's restarted
  * get-members.py to be run periodically. Updates the member list locally (so if there's a powercut or internet outage, there's still a local list of permitted users)


### Config
This project has space for two fob readers, an in and an out.
If there's no out (or somehow, no in), just remove that section of config. If a fob reader is specified but not available, you'll get errors logged out.

### Connections
* Connect the two nanos to the Pi.
* Plug in the Pi.
* Conenct the Pi GPIO to the relay board to activate the door lock release