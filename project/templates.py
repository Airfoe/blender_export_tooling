


# /!\ ALERT: Claude Opus 5 /!\


import re

TOKEN_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
MAX_DEPTH = 16


class TemplateError(Exception):
    pass


def resolve(template, ctx, _depth=0, _seen=()):
    """'{ROOT}/Chars/{FILENAME}' -> 'X:/MyProject/Chars/hero'"""
    if _depth > MAX_DEPTH:
        raise TemplateError(f"Token nesting too deep in {template!r}")

    def sub(m):
        key = m.group(1).upper()
        if key in _seen:
            raise TemplateError(f"Circular reference: {' -> '.join((*_seen, key))}")
        if key not in ctx:
            raise TemplateError(f"Unknown token {{{key}}}")
        return resolve(str(ctx[key]), ctx, _depth + 1, (*_seen, key))


    return TOKEN_RE.sub(sub, template)



def to_regex(template):
    """'{ROOT}/Chars/{FILENAME}' -> pattern capturing root/filename from a real path"""
    out, idx = [], 0
    for m in TOKEN_RE.finditer(template):
        out.append(re.escape(template[idx:m.start()]))
        out.append(f"(?P<{m.group(1).lower()}>[^/\\\\]+)")
        idx = m.end()
    out.append(re.escape(template[idx:]))
    return re.compile("".join(out), re.IGNORECASE)