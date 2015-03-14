# Introduction #

Myro requires packages like old Python and threaded Tcl/Tk.


# Details #

The development setup includes:
  * custom Python and Tcl/Tk builds
  * old modules
  * wrapper script for Python

For development, the simulator will be launched. Beeps will be printed to the server console.

You will need:
  * make, gcc, etc.
  * numpy, etc.
  * 250 MB free space
  * network

Instructions:
  1. In `lib/`, type `make`. After everything installs, you should get a Python prompt.
  1. Run `simulator()` to see if the simulator starts.
  1. Run `forward(1)`.
  1. In the project root, type `make` to start the server. The simulator should automatically open. The default recipe should kill any existing simulators.
  1. Edit interface.py and the server will automatically reload the code. Depending on your editor, the automatic reloading may occasionally fail due to a race condition, but this only happens during development.