This is a proxy for [slobby](https://github.com/itkach/slobby); it extracts the math definitions from the "alt" field of non-inline math images, and uses Mathjax to render them.

Before, with just slobby:

![Before, with just slobby](images/before.png "Before, with just slobby")

After, over this mathjax_proxy.py:

![After, over this mathjax_proxy.py](images/after.png "After, over this mathjax_proxy.py")

# Installation

First make sure you've downloaded a .slob file with the data you want.
I use the Wikipedia one, from here:

[https://ftp.halifax.rwth-aachen.de/aarddict/enwiki/enwiki20260401-slob/](https://ftp.halifax.rwth-aachen.de/aarddict/enwiki/enwiki20260401-slob/)

There's a release per month, so choose what you want. There's also many other datasets you can choose from - see 
[https://ftp.halifax.rwth-aachen.de/aarddict/](https://ftp.halifax.rwth-aachen.de/aarddict/)

The enwiki ones contain the textual entirety of Wikipedia. Put the file in the same 
place as I did (`/opt/aard.wikipedia/enwiki-20260401.slob`) or update the `SLOBBY_FILE` in the 
Makefile.

Usage can't get any simpler:

    make

This will build a Docker container with both `slobby` and my Mathjax proxy filter; and then launch them both.

You can then visit [http://localhost:8014](http://localhost:8014) to access the end result.

Note that the docker image is "only" 247MB, which I suppose is an achievement these days :-)

Hope this helps someone!
