About
=====

A graphical front-end for
[anesthetic](https://github.com/williamjameshandley/anesthetic),
designed to allow more efficient observation of what goes on in a
nested sampling run. As this is a thin wrapper around anesthetic, it
supports all of the sampling formats supported by anesthetic, and
*only* those formats. 

The main benefit over using the `anesthetic.gui()` in your scripts is
the improved responsiveness of the graphical user interface, and the
ability to overlay multiple nested sampling plots on top of each
other. There are certain creature comforts included too, like the
ability to alter the colours and display names of the sampling
runs. Additionally, an indexed filter is added to conveniently sort
through the parameters found in the runs. 



Install
=======

Base version
-----------

```{.bash}
python3 -m pip install paranestamol
```

Devel version
------------

``` {.bash}
git clone https://github.com/appetrosyan/paranestamol.git
cd paranestamol
python3 setup.py
```



Usage
=====

`paranestamol` is a graphical application written in QtQuick using
PySide2 (for now). It can be used standalone, or be passed a
command-line (positional) argument containing the file root, or any of
the files belonging to the raw output of your chosen nested sampler,
e.g. [PolyChord](https://github.com/PolyChord/PolyChordLite)


``` {.bash}
python3 -m paranestamol [file_root] 


Planned features
==============

- Integration with [nestcheck](https://github.com/ejhigson/nestcheck) 

- Ability to save the plot(s) to a file

- Ability to save and recall the opened nested sampling runs. 

- Ability to define new parameters, and alter the LaTeX representation
  of the older ones.
  
- Separate log-likelihood sliders for each data-series. 

- Memory-efficient implementation of the alteration-related
  repaints. Right now `paranestamol` caches entire figures.

