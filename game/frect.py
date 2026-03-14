"""
Implementação de FRect (retângulo com coordenadas float), compatível com pygame.FRect.
Usar no lugar de pygame.FRect quando o Ren'Py não expõe essa classe.
"""


class FRect:
    """Retângulo com x, y, width, height em float."""

    def __init__(self, x, y, width, height):
        self._x = float(x)
        self._y = float(y)
        self._w = float(width)
        self._h = float(height)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, v):
        self._x = float(v)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, v):
        self._y = float(v)

    @property
    def width(self):
        return self._w

    @width.setter
    def width(self, v):
        self._w = float(v)

    @property
    def height(self):
        return self._h

    @height.setter
    def height(self, v):
        self._h = float(v)

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, v):
        self._w = float(v)

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, v):
        self._h = float(v)

    @property
    def left(self):
        return self._x

    @left.setter
    def left(self, v):
        self._x = float(v)

    @property
    def top(self):
        return self._y

    @top.setter
    def top(self, v):
        self._y = float(v)

    @property
    def right(self):
        return self._x + self._w

    @right.setter
    def right(self, v):
        self._x = float(v) - self._w

    @property
    def bottom(self):
        return self._y + self._h

    @bottom.setter
    def bottom(self, v):
        self._y = float(v) - self._h

    @property
    def centerx(self):
        return self._x + self._w / 2

    @centerx.setter
    def centerx(self, v):
        self._x = float(v) - self._w / 2

    @property
    def centery(self):
        return self._y + self._h / 2

    @centery.setter
    def centery(self, v):
        self._y = float(v) - self._h / 2

    @property
    def center(self):
        return (self.centerx, self.centery)

    @center.setter
    def center(self, v):
        self.centerx, self.centery = v

    @property
    def topleft(self):
        return (self._x, self._y)

    @topleft.setter
    def topleft(self, v):
        self._x, self._y = float(v[0]), float(v[1])

    @property
    def topright(self):
        return (self._x + self._w, self._y)

    @topright.setter
    def topright(self, v):
        self._x = float(v[0]) - self._w
        self._y = float(v[1])

    @property
    def bottomleft(self):
        return (self._x, self._y + self._h)

    @bottomleft.setter
    def bottomleft(self, v):
        self._x = float(v[0])
        self._y = float(v[1]) - self._h

    @property
    def bottomright(self):
        return (self._x + self._w, self._y + self._h)

    @bottomright.setter
    def bottomright(self, v):
        self._x = float(v[0]) - self._w
        self._y = float(v[1]) - self._h

    @property
    def size(self):
        return (self._w, self._h)

    @size.setter
    def size(self, v):
        self._w, self._h = float(v[0]), float(v[1])

    def copy(self):
        return FRect(self._x, self._y, self._w, self._h)

    def move(self, x, y):
        return FRect(self._x + x, self._y + y, self._w, self._h)

    def move_ip(self, x, y):
        self._x += x
        self._y += y

    def colliderect(self, other):
        """Retorna True se este retângulo colide com other (FRect ou objeto com x, y, width, height)."""
        try:
            ox = other.x if hasattr(other, 'x') else other[0]
            oy = other.y if hasattr(other, 'y') else other[1]
            ow = other.width if hasattr(other, 'width') else other[2]
            oh = other.height if hasattr(other, 'height') else other[3]
        except (IndexError, TypeError):
            return False
        return not (self._x + self._w <= ox or ox + ow <= self._x or
                    self._y + self._h <= oy or oy + oh <= self._y)

    def collidepoint(self, x, y=None):
        """Retorna True se o ponto (x, y) está dentro do retângulo."""
        if y is None:
            x, y = x[0], x[1]
        return (self._x <= x < self._x + self._w and
                self._y <= y < self._y + self._h)

    def __iter__(self):
        yield self._x
        yield self._y
        yield self._w
        yield self._h

    def __repr__(self):
        return f"FRect({self._x}, {self._y}, {self._w}, {self._h})"
