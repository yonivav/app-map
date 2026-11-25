"""TypeScript and JavaScript (React and React Native): components, hooks, stores and contexts,
classes, interfaces, types and enums, with their members. Function components and hooks are the
React equivalent of widgets and view-models, so they get their own kinds; JSX gives what a
component renders (`refs.builds`), calls give the hooks and functions it uses."""
import re

from .base import Language, add_member, declaration, end_line, first, line, text

LEADING = {'comment'}
FUNCTION_VALUES = {'arrow_function', 'function_expression', 'function'}
# Wrappers whose first argument is the component: `memo(X)`, `React.forwardRef((p, ref) => …)`.
COMPONENT_WRAPPERS = {'memo', 'forwardRef', 'observer', 'React.memo', 'React.forwardRef'}
STORE_FACTORIES = {'create', 'createStore', 'createSlice', 'configureStore', 'makeAutoObservable'}
CONTEXT_FACTORIES = {'createContext', 'React.createContext'}
HOOK = re.compile(r'^use[A-Z0-9]')
COMPONENT = re.compile(r'^[A-Z]')
HOST_COMPONENT = re.compile(r'^[a-z]')  # <div>, <svg>: never a project component


def _callee(source, call):
    function = call.child_by_field_name('function')
    return text(source, function) if function is not None else ''


def _unwrap_call(source, node):
    """`memo(forwardRef((props) => …))` → the innermost function value, with the wrappers seen."""
    wrappers = []
    while node is not None and node.type == 'call_expression':
        name = _callee(source, node)
        wrappers.append(name)
        args = node.child_by_field_name('arguments')
        node = args.named_children[0] if args is not None and args.named_children else None
    return node, wrappers


def _returns_jsx(node):
    stack = [node]
    while stack:
        current = stack.pop()
        if current.type in ('jsx_element', 'jsx_self_closing_element', 'jsx_fragment'):
            return True
        # Nested function bodies belong to callbacks, not to this function's own return.
        if current is not node and current.type in FUNCTION_VALUES | {'function_declaration'}:
            continue
        stack.extend(current.named_children)
    return False


def _refs(source, node):
    """What a declaration renders (JSX), calls and mentions (types)."""
    builds, calls, types = set(), set(), set()
    stack = [node]
    while stack:
        current = stack.pop()
        kind = current.type
        if kind in ('jsx_opening_element', 'jsx_self_closing_element'):
            name = current.child_by_field_name('name')
            if name is not None:
                label = text(source, name)
                if not HOST_COMPONENT.match(label):
                    builds.add(label)
                    builds.add(label.split('.')[-1])
        elif kind == 'call_expression':
            label = _callee(source, current)
            if label:
                calls.add(label.split('.')[-1])
                if '.' in label:
                    calls.add(label.split('.')[0])
        elif kind == 'new_expression':
            constructor = current.child_by_field_name('constructor')
            if constructor is not None:
                calls.add(text(source, constructor).split('.')[-1])
        elif kind == 'type_identifier':
            types.add(text(source, current))
        elif kind == 'identifier' and COMPONENT.match(text(source, current)):
            # `component={ProfileScreen}`, `useContext(ThemeContext)`: a mention, not a call.
            types.add(text(source, current))
        stack.extend(current.named_children)
    return {'builds': sorted(builds), 'calls': sorted(calls), 'types': sorted(types)}


def _pattern_names(source, pattern):
    """Names bound by a parameter or `const` pattern: `{ title, onPress }`, `[count, setCount]`."""
    if pattern is None:
        return []
    if pattern.type in ('identifier', 'shorthand_property_identifier_pattern'):
        return [text(source, pattern)]
    names = []
    for child in pattern.named_children:
        if child.type == 'pair_pattern':
            value = child.child_by_field_name('value')
            names += _pattern_names(source, value) if value is not None else []
        elif child.type in ('object_assignment_pattern', 'assignment_pattern'):
            names += _pattern_names(source, child.named_children[0] if child.named_children else None)
        elif child.type in ('identifier', 'shorthand_property_identifier_pattern'):
            names.append(text(source, child))
        elif child.type in ('object_pattern', 'array_pattern', 'rest_pattern'):
            names += _pattern_names(source, child)
    return names


def _props(source, function, decl):
    params = function.child_by_field_name('parameters')
    if params is None and function.child_by_field_name('parameter') is not None:
        params = function  # `x => …`: a single bare parameter
    if params is None:
        return
    for param in params.named_children[:1]:  # a component's props are its first parameter
        pattern = param.child_by_field_name('pattern') if param.type in (
            'required_parameter', 'optional_parameter') else param
        if pattern is not None and pattern.type == 'object_pattern':
            for name in _pattern_names(source, pattern):
                add_member(decl, name, line(param), end_line(param))


def _body_members(source, function, decl, hook=False):
    """State (`const [x, setX] = useState`), handlers and inner helpers; for a hook, what it returns."""
    body = function.child_by_field_name('body')
    if body is None or body.type != 'statement_block':
        return
    for statement in body.named_children:
        if statement.type == 'lexical_declaration' or statement.type == 'variable_declaration':
            for declarator in statement.named_children:
                if declarator.type != 'variable_declarator':
                    continue
                name = declarator.child_by_field_name('name')
                value = declarator.child_by_field_name('value')
                if name is None:
                    continue
                if name.type == 'array_pattern':
                    # `const [count, setCount] = useState(0)`: the state is `count`.
                    names = _pattern_names(source, name)
                    if names:
                        add_member(decl, names[0], line(statement), end_line(statement))
                elif name.type == 'identifier' and value is not None:
                    inner, _ = _unwrap_call(source, value) if value.type == 'call_expression' else (value, [])
                    is_function = inner is not None and inner.type in FUNCTION_VALUES
                    callee = _callee(source, value) if value.type == 'call_expression' else ''
                    if is_function or HOOK.match(callee.split('.')[-1] or ''):
                        add_member(decl, text(source, name), line(statement), end_line(statement))
        elif statement.type == 'function_declaration':
            name = statement.child_by_field_name('name')
            if name is not None:
                add_member(decl, text(source, name), line(statement), end_line(statement))
        elif hook and statement.type == 'return_statement':
            for value in statement.named_children:
                if value.type == 'object':
                    for entry in value.named_children:
                        key = entry.child_by_field_name('key') if entry.type in ('pair', 'method_definition') else entry
                        if key is not None and entry.type in ('pair', 'shorthand_property_identifier', 'method_definition'):
                            add_member(decl, text(source, key), line(entry), end_line(entry))


def _object_keys(source, obj, decl):
    for entry in obj.named_children:
        key = None
        if entry.type in ('pair', 'method_definition'):
            key = entry.child_by_field_name('key') or entry.child_by_field_name('name')
        elif entry.type == 'shorthand_property_identifier':
            key = entry
        if key is not None:
            add_member(decl, text(source, key).strip('\'"'), line(entry), end_line(entry))


def _store_members(source, call, decl):
    """`createSlice({ name, reducers: {…} })`, zustand `create((set) => ({…}))`: its fields and actions."""
    stack = [call]
    while stack:
        current = stack.pop()
        if current.type == 'object':
            for entry in current.named_children:
                key = entry.child_by_field_name('key') if entry.type == 'pair' else None
                value = entry.child_by_field_name('value') if entry.type == 'pair' else None
                if key is not None and text(source, key) in ('reducers', 'extraReducers', 'selectors') \
                        and value is not None and value.type == 'object':
                    _object_keys(source, value, decl)
                    continue
            if not decl['members'] or any(text(source, e).startswith(('name', 'initialState'))
                                          for e in current.named_children if e.type == 'pair'):
                _object_keys(source, current, decl)
            return
        stack.extend(reversed(current.named_children))


def _class_members(source, body, decl):
    start = None
    for child in body.named_children:
        if child.type in LEADING:
            start = start or line(child)
            continue
        name = None
        if child.type in ('method_definition', 'abstract_method_signature', 'method_signature'):
            name = child.child_by_field_name('name')
        elif child.type in ('public_field_definition', 'field_definition'):
            name = child.child_by_field_name('name') or child.child_by_field_name('property')
        if name is not None:
            add_member(decl, text(source, name), start or line(child), end_line(child))
        start = None


def _type_members(source, body, decl):
    for child in body.named_children:
        if child.type in ('property_signature', 'method_signature'):
            name = child.child_by_field_name('name')
            if name is not None:
                add_member(decl, text(source, name), line(child), end_line(child))


def _supers(source, node):
    supers = []
    heritage = first(node, 'class_heritage')
    for clause in (heritage.named_children if heritage is not None else []):
        for value in clause.named_children:
            if value.type not in ('type_arguments',):
                supers.append(text(source, value).split('<')[0])
    extends = first(node, 'extends_type_clause')
    for value in (extends.named_children if extends is not None else []):
        supers.append(text(source, value).split('<')[0])
    return supers


def _function_decl(rel, source, name, function, begin, end):
    hook = bool(HOOK.match(name))
    component = bool(COMPONENT.match(name)) and _returns_jsx(function)
    kind = 'hook' if hook else 'component' if component else 'function'
    decl = declaration(rel, name, kind, begin, end)
    if component:
        _props(source, function, decl)
    if component or hook:
        _body_members(source, function, decl, hook=hook)
    return decl


def _variable_decl(rel, source, declarator, begin, end):
    name = declarator.child_by_field_name('name')
    value = declarator.child_by_field_name('value')
    if name is None or name.type != 'identifier':
        return None
    label = text(source, name)
    if value is None:
        return declaration(rel, label, 'top-level variable', begin, end)
    if value.type in FUNCTION_VALUES:
        return _function_decl(rel, source, label, value, begin, end)
    if value.type == 'call_expression':
        inner, wrappers = _unwrap_call(source, value)
        names = {wrapper.split('<')[0] for wrapper in wrappers}
        if names & CONTEXT_FACTORIES:
            return declaration(rel, label, 'context', begin, end)
        if names & STORE_FACTORIES or any(n.endswith('.create') for n in names):
            decl = declaration(rel, label, 'store', begin, end)
            _store_members(source, value, decl)
            return decl
        if names & COMPONENT_WRAPPERS and inner is not None and inner.type in FUNCTION_VALUES:
            return _function_decl(rel, source, label, inner, begin, end)
        if inner is not None and inner.type in FUNCTION_VALUES and HOOK.match(label):
            return _function_decl(rel, source, label, inner, begin, end)
    if value.type == 'class':
        decl = declaration(rel, label, 'class', begin, end, _supers(source, value))
        body = value.child_by_field_name('body')
        if body is not None:
            _class_members(source, body, decl)
        return decl
    return declaration(rel, label, 'top-level variable', begin, end)


def _declaration(rel, source, node, begin):
    """Declarations in one top-level statement (an `export` wraps one)."""
    end = end_line(node)
    kind = node.type
    if kind == 'export_statement':
        inner = node.child_by_field_name('declaration')
        if inner is None:
            value = node.child_by_field_name('value')
            # `export default function () {}` has no name; `export default memo(Foo)` adds nothing.
            return [] if value is None else []
        return _declaration(rel, source, inner, begin)
    if kind == 'function_declaration' or kind == 'generator_function_declaration':
        name = node.child_by_field_name('name')
        return [_function_decl(rel, source, text(source, name), node, begin, end)] if name is not None else []
    if kind in ('lexical_declaration', 'variable_declaration'):
        found = []
        for declarator in node.named_children:
            if declarator.type == 'variable_declarator':
                decl = _variable_decl(rel, source, declarator, begin, end)
                if decl is not None:
                    found.append(decl)
        return found
    if kind in ('class_declaration', 'abstract_class_declaration'):
        name = node.child_by_field_name('name')
        if name is None:
            return []
        decl = declaration(rel, text(source, name), 'class', begin, end, _supers(source, node))
        body = node.child_by_field_name('body')
        if body is not None:
            _class_members(source, body, decl)
        if any(parent.endswith(('Component', 'PureComponent')) for parent in decl['supers']):
            decl['kind'] = 'component'
        return [decl]
    if kind == 'interface_declaration':
        name = node.child_by_field_name('name')
        decl = declaration(rel, text(source, name), 'interface', begin, end, _supers(source, node))
        body = node.child_by_field_name('body')
        if body is not None:
            _type_members(source, body, decl)
        return [decl]
    if kind == 'type_alias_declaration':
        name = node.child_by_field_name('name')
        decl = declaration(rel, text(source, name), 'type', begin, end)
        value = node.child_by_field_name('value')
        if value is not None and value.type == 'object_type':
            _type_members(source, value, decl)
        return [decl]
    if kind == 'enum_declaration':
        name = node.child_by_field_name('name')
        decl = declaration(rel, text(source, name), 'enum', begin, end)
        body = node.child_by_field_name('body')
        for entry in (body.named_children if body is not None else []):
            label = entry.child_by_field_name('name') if entry.type == 'enum_assignment' else entry
            if label is not None and entry.type in ('property_identifier', 'enum_assignment'):
                add_member(decl, text(source, label), line(entry), end_line(entry))
        return [decl]
    return []


def extract(rel, source, root):
    decls = []
    start = None
    for node in root.named_children:
        if node.type in LEADING:
            start = start or line(node)
            continue
        for decl in _declaration(rel, source, node, start or line(node)):
            decl['refs'] = _refs(source, node)
            decls.append(decl)
        start = None
    return decls


class TypeScript(Language):
    """`.ts` with the TypeScript grammar; `.tsx`, `.jsx` and `.js` with TSX, since JSX in `.js`
    files is common in React Native and TSX parses plain JavaScript too."""

    def __init__(self):
        super().__init__('tsx', ('.ts', '.tsx', '.js', '.jsx', '.mts', '.cts'),
                         ('.d.ts', '.gen.ts', '.generated.ts', '.min.js', '.bundle.js'), extract)
        self._ts_parser = None

    def declarations(self, rel, source):
        if rel.endswith(('.ts', '.mts', '.cts')):
            if self._ts_parser is None:
                from tree_sitter_language_pack import get_parser
                self._ts_parser = get_parser('typescript')
            return self._extract(rel, source, self._ts_parser.parse(source).root_node)
        return super().declarations(rel, source)


LANGUAGE = TypeScript()
