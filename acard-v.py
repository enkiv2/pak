#!/usr/bin/env python

from pak import *
try:
    from tkinter import *
    from tkinter import filedialog
    tkFileDialog=filedialog
except:
    from Tkinter import *
    import tkFileDialog

try:
    import cpickle
    pickle=cpickle
except:
    import pickle

def font(family="TKTextFont", size="0", weight="normal", slant="roman"):
    return " ".join([family, size, weight, slant])


fname=""
current_card=""
stack={}
history=[]
historyPos=-1

bold=font(weight='bold')
italic=font(slant='italic')

top=Tk()
top.wm_title("ACard-Viewer")
cmdBarFrame=Frame(top)
bodyFrame=Frame(top)
openButton=Button(cmdBarFrame, text="Open")
backButton=Button(cmdBarFrame, text="<-")
forwardButton=Button(cmdBarFrame, text="->")
exitButton=Button(cmdBarFrame, text="Exit")

openButton.pack(side=LEFT)
backButton.pack(side=LEFT)
forwardButton.pack(side=LEFT)
exitButton.pack(side=LEFT)

bodyFrame.config(height=200, width=300)

content=Text(bodyFrame)
content.config(state=DISABLED)
content.pack(side=TOP, fill=BOTH)


cmdBarFrame.pack(side=TOP, fill=X)
bodyFrame.pack(side=BOTTOM, fill=BOTH)

def getIndexCard():
    if '.header' in stack:
        if 'value' in stack['.header']:
            if 'index' in stack['.header']['value']:
                return stack['.header']['value']['index']
    print("Could not find index in header; falling back to default 'index'.")
    if 'index' in stack:
        return 'index'
    print("Stack is missing card 'index'; falling back to first key lexicographically.")
    keys=stack.keys()
    keys.sort()
    if(len(keys)>0):
        return keys[0]
    print("Stack has no keys!")
    return None

def str2offsets(value):
    valueLines=value.split("\n")
    offsets=[]
    ax=0
    for line in valueLines:
        offsets.append(ax)
        ax+=len(line)
    return offsets

def deflattenOffset(idx, offsets):
    i=len(offsets)-1
    while(idx>offsets[i] and i>=0):
        i-=1
    return str(i+1)+"."+str(idx-offsets[i])

def replaceContent(value):
    content.configure(state=NORMAL)
    content.delete("0.0", END)
    content.insert("0.0", value)
    content.configure(state=DISABLED)
def tagIndexPair(tag, start, end):
    content.mark_set("matchStart", start)
    content.mark_set("matchEnd", end)
    content.tag_add(tag, 'matchStart', 'matchEnd')

def displayCardContent(cardName, handler=None):
    if 'handler' in stack[cardName]:
        handler=stack[cardName]['handler']
    value=stack[cardName]['value']
    cardType=stack[cardName]['type']
    if(cardType=='text'):
        offsets=str2offsets(value)
        replaceContent(value)
        target_cards=[]
        if 'links' in stack[cardName]:
            for link in stack[cardName]['links']:
                tagIndexPair(link['card'], deflattenOffset(link['bpos'], offsets), deflattenOffset(link['epos'], offsets))
                target_cards.append(link['card'])
        for card in target_cards:
            content.tag_configure(card, background="#aaffaa")
            content.bind_tag(card, lambda: displayCard(card), '<Button-1>')
    elif(cardType=='code'):
        exec(value, globals(), {})
    elif(cardType=='list'):
        strval=map(str, value)
        content.replaceContent("\n".join(strval))
        target_cards=[]
        if 'links' in stack[cardName]:
            for link in stack[cardName]['links']:
                tagIndexPair(link['card'], str(link['bpos'])+".0", str(link['epos'])+".end")
                target_cards.append(link['card'])
        for card in target_cards:
            content.tag_configure(card, background="#aaffaa")
            content.bind_tag(card, lambda: displayCard(card), '<Button-1>')
    elif(cardType=='dict'):
        keys=value.keys()
        keys.sort()
        strval=[]
        for key in keys:
            strval.append(str(key)+":\t"+str(value[key]))
        content.replaceContent("\n".join(strval))
        target_cards=[]
        if 'links' in stack[cardName]:
            for link in stack[cardName]['links']:
                tagIndexPair(link['card'], str(link['bpos'])+".0", str(link['epos'])+".end")
                target_cards.append(link['card'])
        for card in target_cards:
            content.tag_configure(card, background="#aaffaa")
            content.bind_tag(card, lambda: displayCard(card), '<Button-1>')
    elif(cardType=='html'):
        fmts={}
        newVal=value.split("<")
        newVal2=[""]
        for i in newVal:
            x=i.split(">")
            tagContent=x[0]
            data=""
            if(len(x)>1):
                data=">".join(x[1:])
            tagName=tagContent.split()[0].lower()
            if tagName[0]=='/':
                tagName=tagName[1:]
            if tagName in ['br', 'p']:
                newVal2.append("\n")
            elif tagName in ['b', 'i', 'u', 'sup', 'sub', 'st']:
                if not tagName in fmts:
                    fmts[tagName]=[]
                fmts[tagName].append(str(len(newVal2))+"."+str(len(newVal2[-1])))
            newVal2[-1]+=data
        strippedValue="".join(newVal2)
        replaceContent(strippedValue)
        for fmt in fmts.keys():
            for start, end in fmts[fmt]:
                tagIndexPair(fmt, start, end)
        content.tag_configure('u', underline=1)
        content.tag_configure('b', font=bold)
        content.tag_configure('i', font=italic)
        content.tag_configure('sup', offset=5)
        content.tag_configure('sub', offset=-5)
        content.tag_configure('st', overstrike=1)
        offsets=str2offsets(strippedValue)
        if 'links' in stack[cardName]:
            for link in stack[cardName]['links']:
                tagIndexPair(link['card'], deflattenOffset(link['bpos'], offsets), deflattenOffset(link['epos'], offsets))
                target_cards.append(link['card'])
        for card in target_cards:
            content.tag_configure(card, background="#aaffaa")
            content.bind_tag(card, lambda: displayCard(card), '<Button-1>')
    else:
        if(handler):
            if handler in stack:
                if 'type' in stack[handler] and 'value' in stack[handler] and stack[handler]['type']=='code':
                    exec(stack[handler]['value'], globals(), {'cardData': value})
                    return
        replaceContent("Cannot display data: no handler")




def displayCard(cardName=None):
    global currentCard, history, historyPos
    if(cardName==None):
        cardName=getIndexCard()
    if(cardName!=None):
        top.wm_title("ACard-Viewer - "+fname+" - "+cardName)
        current_card=cardName
        if(historyPos>=0):
            history=history[:historyPos]
            history.append(cardName)
            historyPos=-1
        displayCardContent(cardName)

def openHelper(*args):
    global fname, stack
    name=tkFileDialog.askopenfilename(filetypes=[('Pak archive', '.pak')])
    if(name):
            if(name!=fname):
                    with open(name, 'r') as f:
                            fname=name
                            stack=pickle.load(f)
                            displayCard()

openButton.configure(command=openHelper)
exitButton.configure(command=lambda: os.exit(0))

top.mainloop()

