# CSCI 6554
 This is Lab work in Python of CSCI 6554 Computer Graphics II in George Washington University.
 
Perspective Vector Display System
------------------------------------------


********************************
### Description:
A system to read in a geometric data of a polygonal object
and to display the object using perspective transformation. 


### Features
 * Real-time rendering
 * support back-face culling
 * Illumination model
 * Texture mapping
 * Easy to setup
 * to be continued...



### How does it work?


* The script first read in .d data and clean it, by removing tab and extra spaces.
* After that, the data will be load as raw data, including vertices and polygons.
* Several parameters were provided to specify viewing angle and other critical conditions in calculation.
* Vector U, V, N were calculated afterwards and matrices followed by that.
* Perspective matrix and viewing matrix were multiplied by raw vertices, to provide screen view of vertices.
* back-face culling function were excuted to remove invisible polygon.
* finally, using Pyglet to draw entire model


##### Detailed code comments were embedded into code


### Deploying & Enviorment Setting
1. install Python     
    * [Python 3.7+](https://www.python.org/downloads/release/python-372/)

2. Install dependencies manually:

    * [Pip](https://pip.pypa.io/en/stable/installing/)
    * [Pyglet](https://bitbucket.org/pyglet/pyglet/downloads/)
    * [numpy](https://www.scipy.org/scipylib/download.html)
    * [PIL/Pillow](https://pillow.readthedocs.io/en/stable/installation.html)

    * ##### Or using following script (recommended, sudo needed)
        <pre>
        python get-pip.py
        pip install Pyglet
        pip install numpy
        pip install Pillow
        </pre>
3. running .py script


#### Thank you!

* Powered by ZDF
* Email: zdf@gwu.edu 

latest update: 2019-05-08
