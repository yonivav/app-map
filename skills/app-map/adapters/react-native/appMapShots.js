/* app-map's React Native helper: reports where each component of the map sits on screen.
 * Copied into the app by run_shots.sh and imported first by the app's entry file, in debug builds
 * only; listed in .git/info/exclude, never committed.
 *
 * React calls the DevTools hook on every commit; this keeps the latest root of each renderer.
 * When the screenshot driver asks the host relay for a snap, this walks that root, measures the
 * first native view of every component whose name the map draws, and posts back
 * `SHOT RECT <id> <Component> <x> <y> <width> <height> <visible>` lines (points / dp). */
/* global __DEV__ */
if (typeof __DEV__ !== 'undefined' && __DEV__) {
  const RELAY = global.__APP_MAP_RELAY__ || 'http://localhost:8765'
  const roots = new Map()

  // Install the hook before React loads, or wrap the one already there (DevTools).
  const existing = global.__REACT_DEVTOOLS_GLOBAL_HOOK__
  if (existing) {
    const commit = existing.onCommitFiberRoot
    existing.onCommitFiberRoot = function (id, root, ...rest) {
      roots.set(id, root)
      return commit ? commit.call(this, id, root, ...rest) : undefined
    }
  } else {
    let nextId = 1
    global.__REACT_DEVTOOLS_GLOBAL_HOOK__ = {
      supportsFiber: true,
      renderers: new Map(),
      inject(renderer) {
        const id = nextId++
        this.renderers.set(id, renderer)
        return id
      },
      onCommitFiberRoot(id, root) {
        roots.set(id, root)
      },
      onCommitFiberUnmount() {},
      onPostCommitFiberRoot() {},
      checkDCE() {},
    }
  }

  const HOST = new Set([5, 6]) // HostComponent, HostText

  function nameOf(fiber) {
    const type = fiber.type
    if (!type || typeof type === 'string') return null
    // memo / forwardRef wrap the function: use the inner name when the wrapper has none.
    const inner = type.type || type.render || type
    return type.displayName || inner.displayName || inner.name || null
  }

  // The first native view down each branch: what a component draws on screen.
  function hostViews(fiber) {
    const found = []
    const visit = (node) => {
      for (; node; node = node.sibling) {
        if (HOST.has(node.tag) && node.stateNode) found.push(node)
        else if (node.child) visit(node.child)
      }
    }
    visit(fiber.child)
    return found
  }

  function measureOne(instance) {
    const target = (instance && instance.canonical && instance.canonical.publicInstance) || instance
    return new Promise((resolve) => {
      if (!target || typeof target.measureInWindow !== 'function') return resolve(null)
      let done = false
      setTimeout(() => !done && resolve(null), 500)
      target.measureInWindow((x, y, width, height) => {
        done = true
        resolve(width > 0 && height > 0 ? { x, y, width, height } : null)
      })
    })
  }

  // A plain wrapper View can be flattened away on the native side (new architecture): it has
  // nothing to measure, so measure its own native children instead, a few levels down.
  async function measure(hostFiber, depth = 0) {
    const box = await measureOne(hostFiber.stateNode)
    if (box || depth >= 4) return box ? [box] : []
    const children = (await Promise.all(hostViews(hostFiber).map((child) => measure(child, depth + 1)))).flat()
    return children
  }

  // Mounted but not showing: inside a hidden Suspense/Offscreen subtree (react-freeze, inactive
  // tabs), or a react-native-screens screen that isn't active (a screen under the top of a stack).
  function isTopOfStack(item) {
    let stack = item.return
    while (stack && nameOf(stack) !== 'ScreenStack') stack = stack.return
    if (!stack) return true
    const items = []
    const visit = (node) => {
      for (; node; node = node.sibling) {
        const name = nameOf(node)
        if (name === 'ScreenStackItem') items.push(node)
        else if (name !== 'ScreenStack' && node.child) visit(node.child)  // not a nested stack's
      }
    }
    visit(stack.child)
    return items.length === 0 || items[items.length - 1] === item ||
      items[items.length - 1] === item.alternate
  }

  function hiddenBy(fiber) {
    for (let node = fiber.return; node; node = node.return) {
      if (node.tag === 22 && node.memoizedState !== null) return 'offscreen'
      // A native stack draws only its last screen on top; the ones before it are covered.
      if (nameOf(node) === 'ScreenStackItem' && !isTopOfStack(node)) return 'under the top of a stack'
      const props = node.memoizedProps
      if (props && typeof props === 'object') {
        if (props.activityState === 0) return 'inactive screen'
        if (props.style && !Array.isArray(props.style) && props.style.display === 'none') return 'display none'
      }
    }
    return null
  }

  async function rects(id, names) {
    const wanted = new Set(names)
    const lines = []
    const seen = new Set()
    const missed = new Set()
    for (const root of roots.values()) {
      const stack = [root.current]
      while (stack.length) {
        const fiber = stack.pop()
        if (!fiber) continue
        const name = nameOf(fiber)
        if (name) seen.add(name)
        if (name && wanted.has(name)) {
          const hosts = hostViews(fiber).filter((host) => host.tag !== 6)  // text nodes can't be measured
          const boxes = (await Promise.all(hosts.map((host) => measure(host)))).flat()
          if (!boxes.length) missed.add(`${name}:${fiber.tag}:${hosts.length}`)
          if (boxes.length) {
            const left = Math.min(...boxes.map((b) => b.x))
            const top = Math.min(...boxes.map((b) => b.y))
            const right = Math.max(...boxes.map((b) => b.x + b.width))
            const bottom = Math.max(...boxes.map((b) => b.y + b.height))
            // On screen or not: a screen kept mounted behind the current one is off to a side.
            const { width, height } = require('react-native').Dimensions.get('window')
            const hidden = hiddenBy(fiber)
            if (hidden) missed.add(`${name}:hidden(${hidden})`)
            const onScreen = !hidden && right > 0 && bottom > 0 && left < width && top < height
            lines.push(`SHOT RECT ${id} ${name} ${left.toFixed(1)} ${top.toFixed(1)} ` +
              `${(right - left).toFixed(1)} ${(bottom - top).toFixed(1)} ${onScreen ? 5 : 0}`)
          }
        }
        if (fiber.sibling) stack.push(fiber.sibling)
        if (fiber.child) stack.push(fiber.child)
      }
    }
    // Every component name on screen, for the relay log: what a scenario or a map can name.
    lines.push(`SHOT SEEN ${id} ${[...seen].sort().join(' ')}`)
    if (missed.size) lines.push(`SHOT SEEN ${id} not measured or hidden: ${[...missed].join(' ')}`)
    return lines
  }

  async function poll() {
    try {
      const response = await fetch(`${RELAY}/poll`)
      if (response.status === 200) {
        const { id, names } = await response.json()
        const lines = await rects(id, names)
        await fetch(`${RELAY}/rects?id=${encodeURIComponent(id)}`, { method: 'POST', body: lines.join('\n') })
      }
    } catch (error) {
      // The relay isn't running (an ordinary debug session): try again later.
    }
    setTimeout(poll, 250)
  }
  setTimeout(poll, 1000)
}
