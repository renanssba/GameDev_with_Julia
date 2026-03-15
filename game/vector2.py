"""
Vector2 - Implementação compatível com pygame.math.Vector2
Referência: https://www.pygame.org/docs/ref/math.html#pygame.math.Vector2
"""
import math


class Vector2:
    """Vetor 2D compatível com pygame.math.Vector2."""
    epsilon = 1e-6

    def __init__(self, x=0, y=None):
        """Vector2() -> (0,0); Vector2(s) -> (s,s); Vector2(x,y) ou Vector2((x,y)) ou Vector2(Vector2)."""
        if y is None:
            if isinstance(x, (int, float)):
                self.x = float(x)
                self.y = float(x)
            elif isinstance(x, Vector2):
                self.x = x.x
                self.y = x.y
            elif isinstance(x, (list, tuple)) and len(x) >= 2:
                self.x = float(x[0])
                self.y = float(x[1])
            else:
                self.x = 0.0
                self.y = 0.0
        else:
            self.x = float(x)
            self.y = float(y)

    # --- Operadores numéricos ---
    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        return Vector2(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        return Vector2(self.x - other, self.y - other)

    def __mul__(self, other):
        if isinstance(other, Vector2):
            return self.dot(other)  # produto escalar (dot product)
        return Vector2(self.x * other, self.y * other)

    def __rmul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        return Vector2(self.x / other, self.y / other)

    def __floordiv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x // other.x, self.y // other.y)
        return Vector2(self.x // other, self.y // other)

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other
            self.y += other
        return self

    def __isub__(self, other):
        if isinstance(other, Vector2):
            self.x -= other.x
            self.y -= other.y
        else:
            self.x -= other
            self.y -= other
        return self

    def __imul__(self, other):
        if isinstance(other, Vector2):
            raise TypeError("dot product result is scalar, use elementwise() for element-wise *")
        self.x *= other
        self.y *= other
        return self

    def __itruediv__(self, other):
        if isinstance(other, Vector2):
            self.x /= other.x
            self.y /= other.y
        else:
            self.x /= other
            self.y /= other
        return self

    def __ifloordiv__(self, other):
        if isinstance(other, Vector2):
            self.x //= other.x
            self.y //= other.y
        else:
            self.x //= other
            self.y //= other
        return self

    def __eq__(self, other):
        if not isinstance(other, Vector2):
            return False
        return abs(self.x - other.x) < self.epsilon and abs(self.y - other.y) < self.epsilon

    def __ne__(self, other):
        return not self.__eq__(other)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"

    def __getitem__(self, key):
        if key == 0 or key == 'x':
            return self.x
        if key == 1 or key == 'y':
            return self.y
        if isinstance(key, slice):
            return (self.x, self.y)[key]
        raise IndexError("Vector2 index out of range")

    def __setitem__(self, key, value):
        if key == 0 or key == 'x':
            self.x = float(value)
        elif key == 1 or key == 'y':
            self.y = float(value)
        elif isinstance(key, slice):
            vals = (self.x, self.y)
            new = list(vals)
            new[key] = value
            if len(new) >= 2:
                self.x, self.y = float(new[0]), float(new[1])
        else:
            raise IndexError("Vector2 index out of range")

    def __iter__(self):
        yield self.x
        yield self.y

    def __round__(self, ndigits=0):
        return Vector2(round(self.x, ndigits), round(self.y, ndigits))

    # --- Atributos swizzle (xy) ---
    @property
    def xy(self):
        return (self.x, self.y)

    @xy.setter
    def xy(self, value):
        self.x, self.y = float(value[0]), float(value[1])

    # --- Produto escalar e vetorial ---
    def dot(self, other):
        """Produto escalar (dot product)."""
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        """Produto vetorial 2D: retorna componente z (escalar)."""
        return self.x * other.y - self.y * other.x

    # --- Magnitude e comprimento ---
    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_squared(self):
        return self.x * self.x + self.y * self.y

    def length(self):
        return self.magnitude()

    def length_squared(self):
        return self.magnitude_squared()

    # --- Normalização ---
    def normalize(self):
        """Retorna vetor normalizado (comprimento 1)."""
        mag = self.length()
        if mag < self.epsilon:
            raise ValueError("Cannot normalize zero vector")
        return Vector2(self.x / mag, self.y / mag)

    def normalize_ip(self):
        """Normaliza o vetor in-place."""
        mag = self.length()
        if mag < self.epsilon:
            raise ValueError("Cannot normalize zero vector")
        self.x /= mag
        self.y /= mag

    def is_normalized(self):
        return abs(self.length_squared() - 1.0) < self.epsilon

    def scale_to_length(self, length):
        """Escala o vetor para o comprimento dado (in-place)."""
        mag = self.length()
        if mag < self.epsilon:
            raise ValueError("Cannot scale zero vector")
        factor = length / mag
        self.x *= factor
        self.y *= factor

    # --- Reflexão ---
    def reflect(self, normal):
        """Reflete o vetor sobre a normal dada."""
        n = Vector2(normal.x, normal.y)
        if n.length_squared() < self.epsilon:
            raise ValueError("Cannot reflect over zero vector")
        n = n.normalize()
        return self - 2 * self.dot(n) * n

    def reflect_ip(self, normal):
        """Reflete o vetor sobre a normal in-place."""
        r = self.reflect(normal)
        self.x, self.y = r.x, r.y

    # --- Distância ---
    def distance_to(self, other):
        return (self - other).length()

    def distance_squared_to(self, other):
        return (self - other).length_squared()

    # --- Move towards ---
    def move_towards(self, target, distance):
        """Move em direção ao target por distance, sem ultrapassar."""
        diff = Vector2(target) - self
        dist = diff.length()
        if dist <= distance or dist < self.epsilon:
            return Vector2(target)
        return self + diff * (distance / dist)

    def move_towards_ip(self, target, distance):
        """Move em direção ao target in-place."""
        r = self.move_towards(target, distance)
        self.x, self.y = r.x, r.y

    # --- Interpolação ---
    def lerp(self, other, weight):
        """Interpolação linear. weight em [0, 1]."""
        if not 0 <= weight <= 1:
            raise ValueError("weight must be between 0 and 1")
        return Vector2(
            self.x + (other.x - self.x) * weight,
            self.y + (other.y - self.y) * weight
        )

    def slerp(self, other, weight):
        """Interpolação esférica. weight em [-1, 1]."""
        if not -1 <= weight <= 1:
            raise ValueError("weight must be between -1 and 1")
        a_len = self.length()
        b_len = other.length()
        if a_len < self.epsilon or b_len < self.epsilon:
            raise ValueError("Cannot slerp with zero vector")
        dot = self.dot(other) / (a_len * b_len)
        dot = max(-1, min(1, dot))
        omega = math.acos(dot)
        if abs(omega) < self.epsilon:
            return self.lerp(other, weight)
        sin_omega = math.sin(omega)
        a = math.sin((1 - weight) * omega) / sin_omega
        b = math.sin(weight * omega) / sin_omega
        return Vector2(a * self.x + b * other.x, a * self.y + b * other.y)

    # --- Elementwise ---
    def elementwise(self):
        """Próxima operação será element-wise."""
        return VectorElementwiseProxy(self)

    # --- Rotação ---
    def rotate(self, angle):
        """Rotação por ângulo em graus (anti-horário)."""
        rad = math.radians(angle)
        c, s = math.cos(rad), math.sin(rad)
        return Vector2(self.x * c - self.y * s, self.x * s + self.y * c)

    def rotate_rad(self, angle):
        """Rotação por ângulo em radianos."""
        c, s = math.cos(angle), math.sin(angle)
        return Vector2(self.x * c - self.y * s, self.x * s + self.y * c)

    def rotate_ip(self, angle):
        """Rotação in-place (graus)."""
        r = self.rotate(angle)
        self.x, self.y = r.x, r.y

    def rotate_rad_ip(self, angle):
        """Rotação in-place (radianos)."""
        r = self.rotate_rad(angle)
        self.x, self.y = r.x, r.y

    def rotate_ip_rad(self, angle):
        """Alias para rotate_rad_ip (deprecated no pygame)."""
        self.rotate_rad_ip(angle)

    # --- Ângulo ---
    def angle_to(self, other):
        """Ângulo em graus que rotaciona self até alinhar com other."""
        cross = self.x * other.y - self.y * other.x
        dot = self.x * other.x + self.y * other.y
        return math.degrees(math.atan2(cross, dot))

    def as_polar(self):
        """Retorna (r, phi) em coordenadas polares."""
        r = self.length()
        phi = math.atan2(self.y, self.x)
        return (r, math.degrees(phi))

    @classmethod
    def from_polar(cls, polar):
        """Cria Vector2 a partir de (r, phi) onde phi em graus."""
        r, phi = polar[0], math.radians(polar[1])
        return cls(r * math.cos(phi), r * math.sin(phi))

    # --- Projeção ---
    def project(self, other):
        """Projeta este vetor sobre other."""
        len_sq = other.length_squared()
        if len_sq < self.epsilon:
            raise ValueError("Cannot project onto zero vector")
        return other * (self.dot(other) / len_sq)

    # --- Copy e clamp ---
    def copy(self):
        return Vector2(self.x, self.y)

    def clamp_magnitude(self, max_length, min_length=None):
        """Retorna cópia com magnitude limitada."""
        if min_length is None:
            min_length = 0
        if min_length > max_length or min_length < 0 or max_length < 0:
            raise ValueError("Invalid clamp bounds")
        mag = self.length()
        if mag < self.epsilon:
            return self.copy()
        if mag < min_length:
            return self * (min_length / mag)
        if mag > max_length:
            return self * (max_length / mag)
        return self.copy()

    def clamp_magnitude_ip(self, max_length, min_length=None):
        """Clamp magnitude in-place."""
        if min_length is None:
            min_length = 0
        if min_length > max_length or min_length < 0 or max_length < 0:
            raise ValueError("Invalid clamp bounds")
        mag = self.length()
        if mag < self.epsilon:
            return
        if mag < min_length:
            f = min_length / mag
        elif mag > max_length:
            f = max_length / mag
        else:
            return
        self.x *= f
        self.y *= f

    # --- Update (atribui coordenadas) ---
    def update(self, *args):
        """Atribui x,y: update(), update(s), update(x,y), update((x,y)), update(Vector2)."""
        if len(args) == 0:
            self.x, self.y = 0, 0
        elif len(args) == 1:
            a = args[0]
            if isinstance(a, (int, float)):
                self.x = self.y = float(a)
            elif isinstance(a, Vector2):
                self.x, self.y = a.x, a.y
            elif isinstance(a, (list, tuple)) and len(a) >= 2:
                self.x, self.y = float(a[0]), float(a[1])
        elif len(args) == 2:
            self.x, self.y = float(args[0]), float(args[1])

    # --- Compatibilidade com código existente ---
    def make_int_tuple(self):
        return int(self.x), int(self.y)

    def set(self, vec):
        self.x = vec.x
        self.y = vec.y
