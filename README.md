# irp-codes

A Python 3 project to create Broadlink base 64 ir codes when given a lirc.conf file, via Pronto hex.

## Motivation

This section is to document, in one place, everything I've learned about IR codes. This is purely for my own benefit, but if anyone else does find it useful, or notices a glaring error, please let me know.

After getting hold of an old Sony receiever for free (the [STR-DE595](https://www.sony.ca/en/electronics/support/audio-components-receivers-amplifiers/str-de595)), I wanted to be able to control it using Home Assistant. With this in mind, I bought a [Broadlink RM4 mini](https://www.ibroadlink.com/productinfo/762674.html). However, the receiever came without a remote, and so I began looking online for the codes I would need to manually program the rm4. Unfortunately, this was much less straightforward than I had hoped.

There are public databases for remote specs, but these aren't easy to understand for a complete beginner. For my purposes in particular, there is no public database that maps particular functions on specific remotes to the associated Broadlink code. Luckily, I'm not the first person to want to do this sort of thing, and so I was able to find inspiration in particular from [this](https://github.com/molexx/irdb2broadlinkha/) Github project. This project leverages 2 ir code databases - the [irdb](https://github.com/probonopd/irdb/tree/master/codes) and [lirc](https://sourceforge.net/p/lirc-remotes/code/ci/master/tree/remotes/) - as well as the [pronto2broadlink.py](https://gist.githubusercontent.com/appden/42d5272bf128125b019c45bc2ed3311f/raw/bdede927b231933df0c1d6d47dcd140d466d9484/pronto2broadlink.py) and [IrpTransmogrifier](https://github.com/bengtmartensson/IrpTransmogrifier) projects. For my purposes, this project helped me get a foot in the door when looking to understand how I might go about this, but it doesn't actually work for me. Also, it's written as a bash script, which I find difficult to follow, IrpTransmogrifier is in Java, which I know even less, and pronto2broadlink is Python 2. In contrast, this project is pure Python 3.

### A bit about IR databases

I've found the documentation on how to parse these databases to be extremely confusing and/or lacking. Of the two potential code sources I had, I found the irdb to be worse. You can navigate through the codes section on the repository, but I'm expected to know the protocol of the various functions on my remote. There is nowhere I can find either the name of my receiver or the remote (the RM-U306A) so I have no way of knowing which files I'm supposed to be using. Even if I could figure that out, I'm unclear how to actually use the files to create the codes I need. If anyone is coming after me and would like to attempt this route, [this](http://www.hifi-remote.com/sony/Sony_rcvr.htm) source might come in handy.

In contrast, the lirc database [has the specs for my remote](https://sourceforge.net/p/lirc-remotes/code/ci/master/tree/remotes/sony/RM-U306A.lircd.conf). This is why, for this project, the lirc database is used.

Parsing these files still takes quite a bit of background understanding, which is the purpose of the next section.

## How IR codes work

Pass.
