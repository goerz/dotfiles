#!/usr/bin/env python
color_names = [
    "white", "black", "red", "blue", "orange","green", "purple",
    "brown", "pink", "yellow", "lightred", "lightblue", "lightorange",
    "lightgreen", "lightpurple", "grey"]
rgb_values = {
"white"        : (255, 255, 255),
"black"        : (0, 0, 0),
"red"          : (228, 26, 28),
"blue"         : (55, 126, 184),
"orange"       : (255, 127, 0),
"green"        : (77, 175, 74),
"purple"       : (152, 78, 163),
"brown"        : (166, 86, 40),
"pink"         : (247, 129, 191),
"yellow"       : (210, 210, 21),
"lightred"     : (251, 154, 153),
"lightblue"    : (166, 206, 227),
"lightorange"  : (253, 191, 111),
"lightgreen"   : (178, 223, 138),
"lightpurple"  : (202, 178, 214),
"grey"         : (153, 153, 153),
}

for i, colorname in enumerate(color_names):
    r, g, b = rgb_values[colorname]
    print '@map color %d to (%d, %d, %d), "%s"' % (i, r, g, b, colorname)


