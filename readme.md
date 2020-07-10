About
=====

This is a GUI for anesthetic.

Install
=======

Base version
------------

``` {.bash}
git clone https://github.com/appetrosyan/paranestamol.git
cd paranestamol
python3 setup.py
```

Async updating version
----------------------

Careful, here be dragons. This version is much faster, and more
responsive, but it also crashes occasionally. Until I track down the
segfault, use at own risk.

``` {.bash}
git clone https://github.com/appetrosyan/paranestamol.git
cd paranestamol
git checkout async-plotting
python3 setup.py
```

Usage
=====

``` {.bash}
python3 -m paranestamol
```

Should give you a gui.

On the first window, you can browse for a chains file, or you can just
drag and drop (whichever you find easier). Loading takes a minute. After
that you\'ll see a list of the loaded chain roots.

Here you can click on the checkbox to turn off rendering of a chain. You
can see the Bayesian model dimensionality, and the Kullback-Leibler
Divergence, along with the evidence.

To change the legend appearance. Just click in the list, either on the
legend rectangle, or the text. Make your changes, including changing the
opacity of the chain you selected. On hitting enter, the view gets
updated.

The plots are presented on the right. As of now `nestcheck` integration
is underway, but not usable. This means that the usual Higson plot that
is in `anesthetic.gui()` is not yet production ready.

Missing features.
=================

-   File hot-reload.
-   `nestcheck` integration
-   Memory-efficient caching.
-   Efficient plot updates
-   A better canvas than matplotlib.
