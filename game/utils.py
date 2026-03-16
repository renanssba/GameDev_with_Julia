import os
import types
import renpy


def color_to_hex(color):
    """Converte (r, g, b) ou (r, g, b, a) para '#rrggbb'."""
    if hasattr(color, '__len__') and len(color) >= 3:
        return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
    return "#fff"


def _document_all_methods_impl(obj, prefix, visited, depth, max_depth, out):
    """
    Lógica compartilhada: percorre atributos/métodos e envia cada linha via out(line).
    out pode ser list.append (modo arquivo) ou print (modo terminal).
    """
    obj_id = id(obj)
    if obj_id in visited or depth > max_depth:
        return
    visited.add(obj_id)
    indent = "  " * depth
    if depth == 0:
        out("")
        out("=" * 60)
        out(f"{prefix} - ATTRIBUTES AND METHODS")
        out("=" * 60)
    try:
        for name in sorted(n for n in dir(obj) if not n.startswith("_")):
            try:
                attr = getattr(obj, name)
                full_name = f"{prefix}.{name}"
                out(f"{indent}{full_name} : {type(attr).__name__}")
                root_name = prefix.split(".")[0]
                try:
                    is_module = type(attr) == types.ModuleType
                    is_submodule = is_module or getattr(attr, "__path__", None) is not None or (getattr(attr, "__module__", None) and root_name in str(getattr(attr, "__module__", "")))
                except Exception:
                    is_module = False
                    is_submodule = False
                if depth < max_depth and is_submodule:
                    try:
                        attr_count = len([x for x in dir(attr) if not x.startswith("_")])
                        if is_module or attr_count <= 50:
                            _document_all_methods_impl(attr, full_name, visited, depth + 1, max_depth, out)
                    except (TypeError, AttributeError):
                        pass
            except (AttributeError, TypeError) as e:
                out(f"{indent}{prefix}.{name} : <error: {e}>")
    finally:
        visited.discard(obj_id)
    if depth == 0:
        out("=" * 60)


def document_all_methods(obj=None, filename="renpy_doc.txt", prefix=None, visited=None, depth=0, max_depth=2, lines=None):
    """Imprime atributos e métodos do objeto, recursivamente. Salva no arquivo especificado (pasta do projeto)."""
    if visited is None:
        visited = set()
        lines = []
    if lines is None:
        lines = []
    if obj is None:
        obj = renpy
    if prefix is None:
        prefix = getattr(obj, "__name__", type(obj).__name__)
    out = lines.append
    _document_all_methods_impl(obj, prefix, visited, depth, max_depth, out)
    if depth == 0:
        project_dir = os.path.dirname(renpy.config.gamedir)
        out_path = os.path.join(project_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[document_all_methods] {filename} salvo em: {out_path}")


def document_all_methods_print(obj=None, prefix=None, visited=None, depth=0, max_depth=2):
    """Lista atributos e métodos do objeto no terminal (sem salvar em arquivo)."""
    if visited is None:
        visited = set()
    if obj is None:
        obj = renpy
    if prefix is None:
        prefix = getattr(obj, "__name__", type(obj).__name__)
    _document_all_methods_impl(obj, prefix, visited, depth, max_depth, print)
