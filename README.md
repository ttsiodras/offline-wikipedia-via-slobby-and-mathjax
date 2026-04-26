# What is this?

Without any internet access, you get to have this:

![Offline wikipedia, with math](images/after.png "Offline wikipedia, with math")

# Installation

Make sure you also got the submodules checked out:

    git submodule init
    git submodule update

Then download a .slob file with the data you want. I use the Wikipedia one, from here:

[https://ftp.halifax.rwth-aachen.de/aarddict/enwiki/enwiki20260401-slob/](https://ftp.halifax.rwth-aachen.de/aarddict/enwiki/enwiki20260401-slob/)

There's a release per month, so choose what you want. There's also many other datasets you can choose from - see 
[https://ftp.halifax.rwth-aachen.de/aarddict/](https://ftp.halifax.rwth-aachen.de/aarddict/)

The enwiki ones contain the entirety of the text content in the English Wikipedia. Due to my 
Mathjax filter, it also auto-renders all mathematical notation. Put the file in the same 
place as I did (`/opt/aard.wikipedia/enwiki-20260401.slob`) or update the `SLOBBY_FILE` in the 
Makefile.

Usage can't get any simpler:

    make

This will build a Docker container with both `slobby` and my Mathjax proxy filter; and then launch them both.

You can then visit [http://localhost:8014](http://localhost:8014) to access the end result.

Note that the docker image is "only" 247MB, which I suppose is an achievement these days; keep in mind
that the `enwiki-20260401.slob` file is 24GB, so we're only adding 1% extra :-)

# Notes

Hope this helps someone! It's a Wikipedia that will still function, even when you don't have any
Internet connectivity - giving you what matters the most: the text, and the math.

The bulk of the work was done by the slob/slobby guys. All I did was add a proxy in front,
that extracts the math definitions from the "alt" field of non-inline math images,
and uses Mathjax to render them.

Before, with just slobby:

![Before, with just slobby](images/before.png "Before, with just slobby")

After, over this mathjax_proxy.py:

![After, over this mathjax_proxy.py](images/after.png "After, over this mathjax_proxy.py")

