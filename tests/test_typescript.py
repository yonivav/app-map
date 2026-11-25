"""The TypeScript/JavaScript indexer on a small React Native file. Run: python3 tests/test_typescript.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skills', 'app-map', 'scripts'))
from languages import language_for  # noqa: E402

SOURCE = b'''
import React, { createContext, memo, useContext, useState } from "react"
import { create } from "zustand"

export interface ProfileProps { userId: string; onClose(): void }

export enum Status { Idle, Loading = "loading" }

/** The profile screen. */
export function ProfileScreen({ userId, onClose }: ProfileProps) {
  const [tab, setTab] = useState(0)
  const { profile, refresh } = useProfile(userId)
  const onPressFollow = () => refresh()
  return <Screen><ProfileHeader profile={profile} /><Tabs.Bar value={tab} /></Screen>
}

export const ProfileHeader = memo(function ProfileHeader({ profile }: { profile: Profile }) {
  return <View><Avatar uri={profile.avatar} /></View>
})

export function useProfile(userId: string) {
  const store = useProfileStore()
  const seconds = 3
  const refresh = () => store.load(userId)
  return { profile: store.profile, refresh }
}

export const useProfileStore = create<State>()((set) => ({
  profile: null,
  load: async (id: string) => set({ profile: await fetchProfile(id) }),
}))

export const ThemeContext = createContext({ dark: false })

export class Avatar extends React.Component<{ uri: string }> {
  size = 40
  render() { return <Image source={{ uri: this.props.uri }} /> }
}

const styles = { root: { flex: 1 } }
'''


def main():
    language = language_for('app/ProfileScreen.tsx')
    assert language is not None and language.name == 'tsx', language
    found = {decl['name']: decl for decl in language.declarations('app/ProfileScreen.tsx', SOURCE)}
    expect = {
        'ProfileProps': ('interface', {'userId', 'onClose'}),
        'Status': ('enum', {'Idle', 'Loading'}),
        'ProfileScreen': ('component', {'userId', 'onClose', 'tab', 'onPressFollow'}),
        'ProfileHeader': ('component', {'profile'}),
        'useProfile': ('hook', {'profile', 'refresh', 'store'}),
        'useProfileStore': ('store', {'profile', 'load'}),
        'ThemeContext': ('context', set()),
        'Avatar': ('component', {'size', 'render'}),
        'styles': ('top-level variable', set()),
    }
    for name, (kind, members) in expect.items():
        assert name in found, f'missing {name}: {sorted(found)}'
        assert found[name]['kind'] == kind, (name, found[name]['kind'])
        assert members <= set(found[name]['members']), (name, sorted(found[name]['members']))
    assert 'seconds' not in found['useProfile']['members'], 'a hook lists what it returns, not every local'
    assert found['ProfileScreen']['from'] == 9, found['ProfileScreen']['from']  # includes its doc comment
    refs = found['ProfileScreen']['refs']
    assert {'Screen', 'ProfileHeader', 'Bar'} <= set(refs['builds']), refs['builds']
    assert 'useProfile' in refs['calls'], refs['calls']
    print('typescript: OK')


if __name__ == '__main__':
    main()
