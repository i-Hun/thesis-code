# -*- coding: utf-8 -*-

def get(key):
    d = {
        "tex_image_path": "/home/hun/Thesis/tex/images/",
        "tex_image_format": ["svg", "eps", "png"],
        "tex_font_size": 16,
        "tex_font_family": "Georgia"
    }
    return d[key]