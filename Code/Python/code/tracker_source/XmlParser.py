#
# found this on the following site:
# http://geekyprojects.blogspot.com/2006/10/rants-of-snake-charmer-iii.html
#
# Author:
#    NIKHIL VAJRAMUSHTI

import re
import os

class XMLNode:
    def __init__(self, tag = None, content = None):
        self.tag = tag
        self.properties = {}
        self.childnodes = {}
        self.content = content

    def addProperty(self, property, value):
        self.properties[property] = value

    def addChildNode(self, tag, node):
        if not self.childnodes.has_key(tag):
            self.childnodes[tag] = [node]
        else:
            self.childnodes[tag].append(node)

    def setContent(self, content):
        if self.content is None:
            self.content = content
        else:
            self.content += ' ' + content

class XMLStack:
    def __init__(self):
        self.stack = []

    def pushNode(self, node):
        self.stack.append(node)

    def popNode(self):
        if len(self.stack) == 0:
            raise "Error", "stack is empty"
        node = self.stack[-1]
        del self.stack[-1]
        return node

    def isEmpty(self):
        if len(self.stack) == 0:
            return 1
        return 0

    def length(self):
        return len(self.stack)

# REX/For Python
# Robert D. Cameron "REX: XML Shallow Parsing with Regular Expressions",
# Technical Report TR 1998-17, School of Computing Science, Simon Fraser
# University, November, 1998.
# Copyright (c) 1998, Robert D. Cameron.
# The following code may be freely used and distributed provided that
# this copyright and citation notice remains intact and that modifications
# or additions are clearly identified.
TextSE = "[^<]+"
UntilHyphen = "[^-]*-"
Until2Hyphens = UntilHyphen + "([^-]" + UntilHyphen + ")*-"
CommentCE = Until2Hyphens + ">?"
UntilRSBs = "[^]]*]([^]]+])*]+"
CDATA_CE = UntilRSBs + "([^]>]" + UntilRSBs + ")*>"
S = "[ \\n\\t\\r]+"
NameStrt = "[A-Za-z_:]|[^\\x00-\\x7F]"
NameChar = "[A-Za-z0-9_:.-]|[^\\x00-\\x7F]"
Name = "(" + NameStrt + ")(" + NameChar + ")*"
QuoteSE = '"[^"]' + "*" + '"' + "|'[^']*'"
DT_IdentSE = S + Name + "(" + S + "(" + Name + "|" + QuoteSE + "))*"
MarkupDeclCE = "([^]\"'><]+|" + QuoteSE + ")*>"
S1 = "[\\n\\r\\t ]"
UntilQMs = "[^?]*\\?+"
PI_Tail = "\\?>|" + S1 + UntilQMs + "([^>?]" + UntilQMs + ")*>"
DT_ItemSE = "<(!(--" + Until2Hyphens + ">|[^-]" + MarkupDeclCE + ")|\\?" + Name + "(" + PI_Tail + "))|%" + Name + ";|" + S
DocTypeCE = DT_IdentSE + "(" + S + ")?(\\[(" + DT_ItemSE + ")*](" + S + ")?)?>?"
DeclCE = "--(" + CommentCE + ")?|\\[CDATA\\[(" + CDATA_CE + ")?|DOCTYPE(" + DocTypeCE + ")?"
PI_CE = Name + "(" + PI_Tail + ")?"
EndTagCE = Name + "(" + S + ")?>?"
AttValSE = '"[^<"]' + "*" + '"' + "|'[^<']*'"
ElemTagCE = Name + "(" + S + Name + "(" + S + ")?=(" + S + ")?(" + AttValSE + "))*(" + S + ")?/?>?"
MarkupSPE = "<(!(" + DeclCE + ")?|\\?(" + PI_CE + ")?|/(" + EndTagCE + ")?|(" + ElemTagCE + ")?)"
XML_SPE = TextSE + "|" + MarkupSPE

# Tag Type Constants
OPEN = 1
OPENCLOSE = 2
CLOSE = 3
UNRECOGNISED = 4

# Unsupported tags (HTML formatting tags for displaying info)
unSupportedTags = ['b', 'i', 'u']

def unquote(quotedString):
    if quotedString[0] <> '"' or quotedString[-1] <> '"':
        return quotedString
    return quotedString[1:len(quotedString)-1]

class XMLParser:
    def __init__(self):
        self.nodeStack = XMLStack()
        self.root = None

    def getXMLBuffer(self, fileName):
        if not os.path.exists(fileName):
            return
        f = file(fileName, 'r')
        xmlBuffer = f.read()
        f.close()
        return xmlBuffer

    def parseXMLFile(self, fileName):
        xmlBuffer = self.getXMLBuffer(fileName)
        self.parseXML(xmlBuffer)

    def parseXML(self, xmlBuffer):
        if xmlBuffer is None or xmlBuffer == '':
            return
        buff = xmlBuffer
        currentNode = None
        while 1:
            m = re.search(XML_SPE, buff)
            if m is None:
                break
            g = m.group(0)
            tag = None
            tagType = None
            if g.startswith('<?'):
                buff = m.string[m.end(0):]
                continue
            if g.startswith('<!'):
                buff = m.string[m.end(0):]
                continue
            if g[0] == '<' and g[1] <> '/':
                if g[len(g)-2] <> '/':
                    tag = g[1:len(g)-1].strip()
                    tagType = OPEN
                else:
                    tag = g[1:len(g)-2].strip()
                    tagType = OPENCLOSE
                if tag in unSupportedTags:
                    tagType = UNRECOGNISED
                    buff = m.string[m.end(0):]
                    continue
                else:
                    tagParts = tag.split(' ', 1)
                    newNode = XMLNode(tag = tagParts[0])
                    if len(tagParts) > 1:
                        props = tagParts[1].split('" ')
                        for i in range(len(props)):
                            [attr, val] = props[i].split('="', 1)
                            if val[-1] == '"': val = val[0:len(val)-1]
                            newNode.addProperty(attr, val)
                    if self.root is None:
                        self.root = newNode
                        self.nodeStack.pushNode(self.root)
                        currentNode = self.root
                    else:
                        if currentNode is not None:
                            currentNode.addChildNode(tagParts[0], newNode)
                            if tagType == OPEN:
                                self.nodeStack.pushNode(currentNode)
                                currentNode = newNode
            if g[0] == '<' and g[1] == '/':
                tag = g[2:len(g)-1].strip()
                if tag in unSupportedTags:
                    tagType = UNRECOGNISED
                    buff = m.string[m.end(0):]
                    continue
                else:
                    tagType = CLOSE
                    currentNode = self.nodeStack.popNode()
            if tag is None:
                # This is content for the current tag
                if currentNode is not None:
                    currentNode.setContent(g.strip())
            buff = m.string[m.end(0):]
        # Done parsing

    def getElementsByTagName(self, tag):
        if self.root is None:
            return None
        retnode = self.traverseElements(self.root, tag)
        return retnode

    def traverseElements(self, node, tag):
        if node.tag == tag:
            return node
        for key in node.childnodes.keys():
            nodeArray = node.childnodes[key]
            for childNode in nodeArray:
                retNode = self.traverseElements(childNode, tag)
                if retNode is not None:
                    return retNode
        return None

