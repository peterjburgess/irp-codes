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

Here, I am heavily using [this](http://www.righto.com/2010/03/understanding-sony-ir-remote-codes-lirc.html) fantastic resource from Ken Shirriff that explains how Sony codes work specifically, and how you can read LIRC files associated with them.

IR remotes communicate using a sequence of on/off signals that can be decoded by the device it controls. The sequence is defined by the length of time the signal is on and off for. A common way to encode these sequences is the following (t is an arbitrary time unit):

- signal on for 2t followed by off for t corresponds to a 1.
- signal on for t followed by off for t corresponds to a 0.

In principle, any number of sequences could be defined in this way (for example, 2t on followed by 2t off could correspond to 2, and so on), but Sony and most other manufacturers stick to the binary format detailed above. I think I've come across talk of at least one protocol that uses a system with more numbers, but it's not relevant for my purposes here.

The standard Sony protocols send their IR signals at a frequency of 40khz. A 1 bit is communicated with a signal of 1200 microseconds on followed by 600 microseconds off, and a 0 bit is communicated with a signal of 600 microsends on followed by 600 microseconds off (in reality, there is a margin of error with these numbers). Before the code itself is transmitted, a header is sent, which in the case of a Sony protocol is an onn signal of 2400 microseconds on followed by 600 microseconds off. At the end of the signal, there is a gap before the signal is repeated - for the Sony protocol here, that gap is 45000 microseconds. The signal repeats for as long as the button is held down, and there is a minimum number of repeats - in this case 3.

The signal can be any number of bits long, and the start and end points are defined by the header and the tail. Common Sony protocol lengths are 12, 15 and 20 bits long.

Just to recap here, we have to know the following information before we can decode an IR signal:

- The carrier frequency (in this case 40khz).
- The length of the signal in bits.
- The signature of the header.
- How a 1 is encoded.
- How a 0 is encoded.
- The length of time between repeats.
- The minimum number of repeats.
- The signature of the signal itself.

The Sony protocols all defined with 7 command bits, which are sent first, followed by either 5 or 8 address bits (to make 12 or 15 bits total). The 20 bit version is similar to the 12 bit version, but with 8 additional bits that follow the address bits. The address bits specify the type of device receiving the code, so I will call them device bits going forward. The command bits are the actual command being sent. These are interpreted with the least significant bit first, so to convert them to decimal, they should be read backwards.

This is the official way to parse these codes, but there are 2 alternatives that are commonly used. The first is to treat the signal as a straight sequence of bits, most-significant first. Ken Shirriff calls this bit decoding The final way is to do the same, but to drop the final bit from the code and treat it as a trail bit instead. This is done because the final bit of the sequence is either 600 or 1200 microseconds on followed by a long off, as opposed to the usual 600 microseconds. Shirriff calls this Bit-1 decoding.

To demonstrate as an example, I will use the lirc file for my remote, the RM-U306A and look at the sleep button. The file tells me that the sequence is 14 bits, and has a ptrail of 667 microseconds. This corresponds to the 15 bit Sony protocol, and uses Bit-1 decoding.

- The code given for this function is 0x0186 in hex. This corresponds to 00 0001 1000 0110 in 14 bit binary, or 390 in decimal.
- As the ptrail value corresponds to a value of 0, in 15 bit binary, (or bit encoding), this is equivalent to 000 0011 0000 1100, or 0x030C in hex, or 780 in decimal.
- And in the official Sony encoding, the device code is 0000 1100 with the least significant digit first, which comes out to a device code of 30 in hex, or 48 in decimal. The command code is then 0000 011 in binary, with the least significant digit first, which corresponds to 0x60 hex, or 96 in decimal. As a sense check, this corresponds with the information on [this page](http://www.hifi-remote.com/sony/Sony_rcvr.htm), which usefully describes common command codes and the device codes that correspond with them.
