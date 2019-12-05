# Retrieved from https://github.com/ArsThaumaturgis/TabbedFrame

#######################################################################
##                                                                   ##
## A DirectGUI-based frame that can show multiple "pages",           ##
## selected via tab-buttons at the frame's top                       ##
##                                                                   ##
##                                                                   ##
#######################################################################
##                                                                   ##
## Written by                                                        ##
## Ian Eborn (Thaumaturge) in 2019                                   ##
## (Portions may be earlier)                                         ##
##                                                                   ##
#######################################################################
##                                                                   ##
## This code is licensed under the MIT license. See the              ##
## license file (LICENSE.md) for details.                            ##
## Link, if available:                                               ##
##  https://github.com/ArsThaumaturgis/KeyMapper/blob/master/LICENSE ##
##                                                                   ##
#######################################################################

import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectGui import DirectFrame, DirectScrolledFrame, DirectButton
from panda3d.core import NodePath, PandaNode, TextNode, Vec4, TextureStage, Texture

import types, collections

class TabbedFrame(DirectFrame):
    def __init__(self, parent = None, **kwargs):
        optiondefs = (
            ('frameSize',      (-0.8, 0.8, -0.9, 0.8), None),
            ('tabClickOffsetColor',      Vec4(0.1, 0.1, 0.1, 0), None),
            ('tabRolloverOffsetColor',       Vec4(0.1, 0.1, 0.1, 0), None),
            ('tabInactiveColor',      Vec4(0.2, 0.2, 0.2, 1), None),
            ('tabUnselectedColor',      Vec4(0.7, 0.7, 0.7, 1), None),
            ('tabSelectedColor',      Vec4(0.4, 0.7, 1.0, 1), None),
            ('tab_scale',     0.05, None),
            ('tab_frameSize',      (0, 5, 0, 2), None),
            ('tab_geom_scale',      1, None),
            ('tabHighlightFrameTexture',      None, None),
            ('tabFrameTexture',      None, None),
            ('tabHighlightGeom',      None, None),
            ('tabGeom',      None, None),
            )

        # Button colours: Selected, unselected, rollover-offset, clicked-offset, inactive
        if "scrollFrameConstructor" in kwargs:
            self.scrollFrameConstructor = kwargs["scrollFrameConstructor"]
            del kwargs["scrollFrameConstructor"]
        else:
            self.scrollFrameConstructor = None #type(DirectScrolledFrame)
        if "pageChangeCallback" in kwargs:
            self.pageChangeCallback = kwargs["pageChangeCallback"]
            del kwargs["pageChangeCallback"]
        else:
            self.pageChangeCallback = None #type(DirectScrolledFrame)

        viewingArgs = {}
        for key, arg in list(kwargs.items()):
            if key.startswith("scroll_"):
                key = key[7:]
                viewingArgs[key] = arg
        for key in viewingArgs:
            del kwargs["scroll_"+key]

        if not "canvasSize" in viewingArgs:
            viewingArgs["canvasSize"] = (0, 0, 0, 0)

        self.defineoptions(kwargs, optiondefs)
        
        DirectFrame.__init__(self, parent)

        if self.scrollFrameConstructor is not None:
            self.viewingArea = self.scrollFrameConstructor(parent = self, **viewingArgs)
        else:
            self.viewingArea = DirectScrolledFrame(parent = self, **viewingArgs)

        self.pages = []
        self.pageButtons = []
        
        self.currentPageIndex = -1

        self.tabArgs = {}
        for key, arg in self._constructorKeywords.items():
            if key.startswith("tab_") and \
                        not key.endswith("highlightGeom") and \
                        not key.endswith("unselectedColor") and \
                        not key.endswith("selectedColor") and \
                        not key.endswith("highlightFrameTexture") and \
                        not key.endswith("highlightGeom"):
                self.tabArgs[key[4:]] = arg[0]

        self.addPage(DirectFrame(), "<stand-in>")
        
        self.initialiseoptions(TabbedFrame)

    def __setitem__(self, key, value):
        DirectFrame.__setitem__(self, key, value)
        if key.startswith("tab_"):
            self.tabArgs[key[4:]] = value
    
    def addPage(self, page, pageName, selectedCallback = None, deselectedCallback = None, callbackArg = None):
        if len(self.pages) > 0 and self.pageButtons[0]["text"] == "<stand-in>":
            self.pageButtons[0].destroy()
            self.pageButtons = []
            self.pages[0][0].destroy()
            self.pages = []

        btn = self.makeButton(pageName, len(self.pages))
        
        self.pageButtons.append(btn)
        
        self.dehighlightButton(-1)
        
        self.pages.append((page, selectedCallback, deselectedCallback, callbackArg))

        page.hide()
        page.detachNode()

        self.layoutButtons()
        
        if len(self.pages) == 1:
            self.currentPageIndex = -1
            self.setPage(0)
    
    def makeButton(self, pageName, pageIndex):
        btn = self.createcomponent("tab%d" % len(self.pageButtons), (), "tab",
                                   DirectButton,
                                   command = self.setPage, text = pageName, extraArgs = [pageIndex],
                                   **self.tabArgs)
        #print (self["tab_scale"], btn["scale"])

        return btn
    
    def highlightButton(self, index):
        if index >= -len(self.pageButtons) and index < len(self.pageButtons):
            btn = self.pageButtons[index]

            if self["tabHighlightGeom"] is not None:
                btn["geom"] = self["tabHighlightGeom"]

            if self["tabHighlightFrameTexture"] is not None:
                btn["frameTexture"] = self["tabHighlightFrameTexture"]

            btn["frameColor"] = (self["tabSelectedColor"],
                                 self["tabSelectedColor"],
                                 self["tabSelectedColor"],
                                 self["tabInactiveColor"])
    
    def dehighlightButton(self, index):
        if index >= -len(self.pageButtons) and index < len(self.pageButtons):
            btn = self.pageButtons[index]

            if self["tabGeom"] is not None:
                btn["geom"] = self["tabGeom"]

            if self["tabFrameTexture"] is not None:
                btn["frameTexture"] = self["tabFrameTexture"]

            btn["frameColor"] = (self["tabUnselectedColor"],
                                 self["tabUnselectedColor"] + self["tabClickOffsetColor"],
                                 self["tabUnselectedColor"] + self["tabRolloverOffsetColor"],
                                 self["tabInactiveColor"])
    
    def setPage(self, index):
        if index == self.currentPageIndex:
            return
        
        if self.currentPageIndex >= 0:
            page, selectedCallback, deselectedCallback, callbackArg = self.pages[self.currentPageIndex]
            page.hide()
            page.detachNode()
            self.dehighlightButton(self.currentPageIndex)
            if deselectedCallback is not None:
                deselectedCallback(callbackArg)
        
        if index >= 0 and index < len(self.pages):
            newPage, selectedCallback, deselectedCallback, callbackArg = self.pages[index]
            newPage.show()
            newPage.reparentTo(self.viewingArea.getCanvas())
            if selectedCallback is not None:
                selectedCallback(callbackArg)
            
            self.layoutPage(newPage)
            
            self.highlightButton(index)
            
        self.currentPageIndex = index

        if self.pageChangeCallback is not None:
            self.pageChangeCallback(self)

    def nextPage(self):
        if self.currentPageIndex < len(self.pages) - 1:
            self.setPage(self.currentPageIndex + 1)

    def previousPage(self):
        if self.currentPageIndex > 0:
            self.setPage(self.currentPageIndex - 1)
    
    def layoutPage(self, page):
        pageBounds = page["frameSize"]
        if pageBounds is None:
            pageBounds = tuple(self.viewingArea["frameSize"])
        mainBounds = self.viewingArea["frameSize"]

        tall = False
        if pageBounds[2] < mainBounds[2]:
            tall = True
            b = pageBounds[2] - 0.15
        else:
            b = mainBounds[2]
        if pageBounds[3] > mainBounds[3]:
            tall = True
            t = pageBounds[3]
        else:
            t = mainBounds[3]
        if pageBounds[0] < mainBounds[0]:
            l = pageBounds[0]
        else:
            l = mainBounds[0]
        if tall or pageBounds[1] > mainBounds[1]:
            r = pageBounds[1]
        else:
            r = mainBounds[1]

        self.viewingArea["canvasSize"] = (l, r, b, t)

    def layoutButtons(self):
        width = self["tab_frameSize"][1] - self["tab_frameSize"][0]
        buttonScale = self["tab_scale"]

        for pageIndex, button in enumerate(self.pageButtons):
            bounds = self["frameSize"]
            pos = (bounds[0] + pageIndex*width*buttonScale, 0, bounds[3])
            button.setPos(*pos)

    def setFrameSize(self, fClearFrame = 0):
        self.layoutButtons()

        DirectFrame.setFrameSize(self, fClearFrame)
        self.viewingArea["frameSize"] = self["frameSize"]

        self.layoutPage(self.pages[self.currentPageIndex][0])

    def clearPages(self):
        for btn in self.pageButtons:
            btn.destroy()
        for page, callback1, callback2, arg in self.pages:
            page.destroy()

        self.currentdeselectedCallback = None

        self.pageButtons = []
        self.pages = []

        self.currentPageIndex = -1

    def destroy(self):
        self.clearPages()
        
        DirectFrame.destroy(self)
