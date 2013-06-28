#!/usr/bin/env python
import sys
sys.path.append("../")
import pydoc
import pak
h=pydoc.HTMLDoc()
f=open("./pak.html", "w")
f.write(h.docmodule(pak))
f.close
