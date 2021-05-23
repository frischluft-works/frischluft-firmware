# frischluft.works - Source

This repository contains the sourcecode for the frischluft.works project.
It is written in micropython and in a modular fashion that allows the components to be reused in other projects.



--- 


Prebuilt firmware releases live in /releases folder

latest release is always found at /releases/latest.bin

---

`src/` contains all the micropython code to run the frischluft.works project

`src-dist/` contains the compiled .mpy files that are used on the actual device


---

# Webserver & Built-in Website

You can run the webserver locally:

```shell
$ cd src
$ micropython webserver
```
You need to install micropython for that, its easy to compile from source (micropython.org)

Keyboard shortcuts:

* `p`: add datapoint with random value to the chart
* `i`: toggle devtools (stats about ram and fs)

Lint the code: `npm run lint`



---

# Known Problems

## Memory Issues

We are running into out of memory situations, even though `gc.mem_free()` says we have 39k free.

That's why there's a 300 datapoint limit in `databuffer.py`, and why DNS is currently disabled.

Possible ways include frozen bytecode or [mpy-cross](https://github.com/micropython/micropython/tree/master/mpy-cross) (build .mpy files and upload them - delete .py files!) (see [here](https://github.com/micropython/micropython/issues/2530), [here](https://forum.micropython.org/viewtopic.php?t=4306) and [here](micropython "MemoryError: memory allocation failed, allocating 3035 bytes"))


use the build-release.sh to generate .mpfiles from the .py files and use these on the actual microcontroller to safe precious memory

## Charts License Problem

We used highcharts but the license is not compatible with our open source aproaich, so we will switch to another visualisation javascript framework.
we are currently looking at Charts.js and once integrated, you will be able to download it here.
As we can not include highcharts here, the firmware will work, but the webinterface wont show statistics.

