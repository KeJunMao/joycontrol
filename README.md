# joycontrol

Emulate Nintendo Switch Controllers over Bluetooth.

Tested on Ubuntu 19.10 and with Raspberry Pi 4B Raspbian GNU/Linux 10 (buster)

## Note

Fork from https://github.com/mart1nro/joycontrol.

I'm just added `douyu.py`.

Run `joycontrol` and enter `douyu` start.

enjoy :)

## Installation

- Install the dbus-python and libhidapi-hidraw0 packages

```bash
sudo apt install python3-dbus libhidapi-hidraw0
```

- Clone the repository and install the joycontrol package to get missing dependencies (Note: Controller script needs super user rights, so python packages must be installed as root). In the joycontrol folder run:

```bash
sudo pip3 install .
```

- Disable the bluez "input" plugin, see [#8](https://github.com/mart1nro/joycontrol/issues/8)

## Command line interface example

- Run the script

```bash
sudo python3 run_controller_cli.py PRO_CONTROLLER
```

This will create a PRO_CONTROLLER instance waiting for the Switch to connect.

- Open the "Change Grip/Order" menu of the Switch

The Switch only pairs with new controllers in the "Change Grip/Order" menu.

Note: If you already connected an emulated controller once, you can use the reconnect option of the script (-r "\<Switch Bluetooth Mac address>").
This does not require the "Change Grip/Order" menu to be opened. You can find out a paired mac address using the "bluetoothctl" system command.

- After connecting, a command line interface is opened. Note: Press \<enter> if you don't see a prompt.

Call "help" to see a list of available commands.

- If you call "test_buttons", the emulated controller automatically navigates to the "Test Controller Buttons" menu.

## Issues

- When using a Raspberry Pi 4B the connection drops after some time. Might be a hardware issue, since it works fine on my laptop. Using a different bluetooth adapter may help, but haven't tested it yet.
- Incompatibility with Bluetooth "input" plugin requires a bluetooth restart, see [#8](https://github.com/mart1nro/joycontrol/issues/8)
- It seems like the Switch is slower processing incoming messages while in the "Change Grip/Order" menu.
  This causes flooding of packets and makes pairing somewhat inconsistent.
  Not sure yet what exactly a real controller does to prevent that.
  A workaround is to use the reconnect option after a controller was paired once, so that
  opening of the "Change Grip/Order" menu is not required.
- ...

## Resources

[Nintendo_Switch_Reverse_Engineering](https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering)

[console_pairing_session](https://github.com/timmeh87/switchnotes/blob/master/console_pairing_session)
