# Py IDE

Py IDE is a basic IDE for Linux and Mac (if you use Windows, don't) written in Python3 and using GTK3 libraries as GUI. It is inspired on Visual Studio for Mac (not VS Code) - released yesterday (November 16th 2016).

It will feature live Web Development preview, preset compiling options for C/C++ (screw Java) plus customizable compiling options for C/C++ and pretty much any other language since you can write your own compiling code, and any other nice feature that I can copy from some other decent IDE.

Right now it looks something like this:

![](ide-preview.png)

## How to use

As I said on the description, it only supports Linux and Mac, but as I don't have a Mac I'll only provide support for Linux.


```bash
  # To run it simply
  ./main.py

  # You can also provide a path like so
  ./main.py /path/to/FOLDER
```

## Known Issues

* Create a project doesn't work (I haven't created a function for it yet)
* Buttons over Tree View don't work (I haven't created a function for it yet)
* Doesn't alert you if you close the editor without saving a file
* Tree View doesn't work properly with folders
* Dark theme sucks

## Features

Sort of works.

* Basic syntax highlighting
* Opening and saving files
* Retarded code completion (based on what you've already typed)
* Crappy "Compile and Run" (you'll see why)
* Basic configuration (still doesn't have a configuration window, but you can still edit the settings from the file ```pyide-settings.json```)

## To-do

Literally everything.

Being developed right now:

* Menu button featuring settings menu, new file and folder creation, manual syntax highlighting language setting, and more.
* Real time external files/folders creation detection (update and add them to the Tree View)
* Tree View support for folders
* Improve dark theme

## FAQ*

\*Actually never asked questions that you might be asking yourself right now

__What theme is that?__

That is Arc Flatabulous, best theme ever (yes it has a dark version).
