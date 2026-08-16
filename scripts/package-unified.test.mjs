import assert from 'node:assert/strict'
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync
} from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import { afterEach, describe, it } from 'node:test'
import { pathToFileURL } from 'node:url'

const temporaryDirectories = []
const scriptPath = new URL('./package-unified.mjs', import.meta.url)
const nativePlatform = process.platform === 'darwin'
  ? process.arch === 'arm64' ? 'osx-arm64' : 'osx-64'
  : process.platform === 'win32'
    ? 'win-64'
    : 'linux-64'

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true })
  }
})

describe('unified package command', () => {
  it('exposes memorable native packaging aliases', () => {
    const packageConfig = JSON.parse(
      readFileSync(new URL('../package.json', import.meta.url), 'utf8')
    )

    assert.deepEqual({
      linux: packageConfig.scripts['build:linux'],
      mac: packageConfig.scripts['build:mac'],
      macIntel: packageConfig.scripts['build:mac-intel'],
      windows: packageConfig.scripts['build:win']
    }, {
      linux: 'node scripts/package-unified.mjs --platform linux-64',
      mac: 'node scripts/package-unified.mjs --platform osx-arm64',
      macIntel: 'node scripts/package-unified.mjs --platform osx-64',
      windows: 'node scripts/package-unified.mjs --platform win-64'
    })
  })

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
      desktopScript: 'package:linux',
      releaseMode: 'development'
    })
  })

  it('publishes packages at one channel root for platform and noarch solving', () => {
    const root = mkdtempSync(join(tmpdir(), 'unilab-unified-channel-'))
    temporaryDirectories.push(root)
    const binDirectory = join(root, 'bin')
    const artifactsDirectory = join(root, 'artifacts')
    const channelDirectory = join(artifactsDirectory, 'runtime-conda')
    const commandLog = join(root, 'commands.jsonl')
    mkdirSync(binDirectory)

    const fakeCommand = `#!/usr/bin/env node
const { appendFileSync, mkdirSync, writeFileSync } = require('node:fs')
const { basename, join } = require('node:path')
const command = basename(process.argv[1])
appendFileSync(process.env.UNILAB_TEST_COMMAND_LOG, JSON.stringify({
  command,
  args: process.argv.slice(2),
  channel: process.env.UNILABOS_INSTALLER_CHANNEL ?? null,
  runtimeInstaller: process.env.UNILAB_RUNTIME_INSTALLER ?? null
}) + '\\n')
if (command === 'constructor') {
  const outputDirectory = process.argv[process.argv.indexOf('--output-dir') + 1]
  mkdirSync(outputDirectory, { recursive: true })
  const extension = process.env.UNILAB_TEST_TARGET_PLATFORM === 'win-64' ? '.exe' : '.sh'
  writeFileSync(join(
    outputDirectory,
    'Uni-Lab-OS-0.11.3-' + process.env.UNILAB_TEST_TARGET_PLATFORM + extension
  ), 'fixture')
}
`
    for (const command of ['rattler-build', 'constructor', 'micromamba', 'pnpm']) {
      writeFileSync(join(binDirectory, command), fakeCommand, { mode: 0o755 })
    }

    const result = spawnSync(process.execPath, [
      scriptPath.pathname,
      '--platform',
      nativePlatform,
      '--runtime-version',
      '0.11.3'
    ], {
      encoding: 'utf8',
      env: {
        ...process.env,
        UNILAB_ARTIFACTS_DIRECTORY: artifactsDirectory,
        UNILAB_RATTLER_BUILD_COMMAND: join(binDirectory, 'rattler-build'),
        UNILAB_CONSTRUCTOR_COMMAND: join(binDirectory, 'constructor'),
        UNILAB_CONDA_EXE: join(binDirectory, 'micromamba'),
        UNILAB_PNPM_COMMAND: join(binDirectory, 'pnpm'),
        UNILAB_TEST_TARGET_PLATFORM: nativePlatform,
        UNILAB_TEST_COMMAND_LOG: commandLog
      }
    })

    assert.equal(result.status, 0, result.stderr)
    const commands = readFileSync(commandLog, 'utf8')
      .trim()
      .split('\n')
      .map((line) => JSON.parse(line))
    const builds = commands.filter(({ command }) => command === 'rattler-build')
    assert.equal(builds.length, 4)
    for (const build of builds) {
      const outputIndex = build.args.indexOf('--output-dir')
      assert.equal(build.args[outputIndex + 1], channelDirectory)
    }
    const constructor = commands.find(({ command }) => command === 'constructor')
    const condaExeIndex = constructor.args.indexOf('--conda-exe')
    assert.equal(
      constructor.args[condaExeIndex + 1],
      join(binDirectory, 'micromamba')
    )
    assert.equal(
      constructor.channel,
      pathToFileURL(channelDirectory).href
    )
    const pnpm = commands.find(({ command }) => command === 'pnpm')
    assert.deepEqual(pnpm.args.slice(0, 4), [
      '--dir',
      join(new URL('../uni-lab-fe', import.meta.url).pathname),
      '--filter',
      '@unilab/workbench'
    ])
  })

  it('selects the formal signed or ad-hoc Workbench package explicitly', () => {
    const production = spawnSync(process.execPath, [
      scriptPath.pathname,
      '--platform',
      'osx-arm64',
      '--runtime-installer',
      '/tmp/runtime.sh',
      '--runtime-version',
      '0.11.3',
      '--release-mode',
      'production',
      '--dry-run'
    ], { encoding: 'utf8' })
    assert.equal(production.status, 1)
    assert.match(production.stderr, /Runtime 安装器不存在/u)

    const root = mkdtempSync(join(tmpdir(), 'unilab-unified-mac-plan-'))
    temporaryDirectories.push(root)
    const installer = join(root, 'runtime.sh')
    writeFileSync(installer, 'fixture')
    const development = spawnSync(process.execPath, [
      scriptPath.pathname,
      '--platform',
      'osx-arm64',
      '--runtime-installer',
      installer,
      '--runtime-version',
      '0.11.3',
      '--release-mode',
      'development',
      '--dry-run'
    ], { encoding: 'utf8' })
    assert.equal(development.status, 0, development.stderr)
    assert.equal(
      JSON.parse(development.stdout).desktopScript,
      'package:mac:adhoc'
    )
  })
})
