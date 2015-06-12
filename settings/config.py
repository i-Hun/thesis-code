# -*- coding: utf-8 -*-
import platform

if platform.system() == "Darwin":
    os_specific_path = "/Users/olegnagornyy"
else:
    os_specific_path = "/home/hun"

def get(key):
    d = {
        "home_path": os_specific_path,
        "tex_image_path": "{0}/Thesis/tex/images/".format(os_specific_path),
        "tex_image_format": ["svg", "eps", "png"],
        "tex_font_size": 16,
        "tex_font_family": "Georgia"
    }
    return d[key]