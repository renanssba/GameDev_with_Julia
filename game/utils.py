def color_to_hex(color):
    """Converte (r, g, b) ou (r, g, b, a) para '#rrggbb'."""
    if hasattr(color, '__len__') and len(color) >= 3:
        return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
    return "#fff"
