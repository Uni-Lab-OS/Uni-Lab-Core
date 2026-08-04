import assert from 'node:assert/strict'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import { afterEach, describe, it } from 'node:test'

const temporaryDirectories = []
const scriptPath = new URL('./package-unified.mjs', import.meta.url)

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true })
  }
})

describe('unified package command', () => {
  it('maps a platform alias to one native Constructor and Electron plan', () => {
    const root = mkdtempSync(join(tmpdir(), 'unilab-unified-plan-'))
    temporaryDirectories.push(root)
    const installer = join(root, 'Uni-Lab-OS-0.11.3-linux-64.sh')
    writeFileSync(installer, 'fixture')

    const result = spawnSync(process.execPath, [
      scriptPath.pathname,
      '--platform',
      'linux',
      '--runtime-installer',
      installer,
      '--runtime-version',
      '0.11.3',
      '--dry-run'
    ], { encoding: 'utf8' })

    assert.equal(result.status, 0, result.stderr)
    assert.deepEqual(JSON.parse(result.stdout), {
      platform: 'linux-64',
      runtimeInstaller: installer,
      runtimeVersion: '0.11.3',
      constructorRequired: false,
      desktopScript: 'package:linux'
    })
  })
})
