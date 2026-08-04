import { spawnSync } from 'node:child_process'
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync
} from 'node:fs'
import { arch, platform as hostPlatform } from 'node:process'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { fileURLToPath } from 'node:url'

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const osDirectory = join(repositoryRoot, 'Uni-Lab-OS')
const frontendDirectory = join(repositoryRoot, 'uni-lab-fe')
const artifactsDirectory = resolve(
  process.env.UNILAB_ARTIFACTS_DIRECTORY ?? join(repositoryRoot, 'artifacts')
)

const PLATFORM_ALIASES = new Map([
  ['linux', 'linux-64'],
  ['linux-64', 'linux-64'],
  ['osx', 'osx-64'],
  ['osx-64', 'osx-64'],
  ['osx-arm64', 'osx-arm64'],
  ['win-64', 'win-64']
])

const DESKTOP_SCRIPTS = {
  'linux-64': 'package:linux',
  'osx-64': 'package:mac',
  'osx-arm64': 'package:mac',
  'win-64': 'package:win'
}

function main() {
  const options = parseArguments(process.argv.slice(2))
  const targetPlatform = normalizePlatform(
    options.platform ?? currentConstructorPlatform()
  )
  const runtimeVersion = options.runtimeVersion ?? sourceRuntimeVersion()
  let runtimeInstaller = options.runtimeInstaller
    ? resolve(options.runtimeInstaller)
    : null
  if (runtimeInstaller && !existsSync(runtimeInstaller)) {
    throw new Error(`Runtime 安装器不存在：${runtimeInstaller}`)
  }
  const plan = {
    platform: targetPlatform,
    runtimeInstaller,
    runtimeVersion,
    constructorRequired: runtimeInstaller === null,
    desktopScript: DESKTOP_SCRIPTS[targetPlatform]
  }
  if (options.dryRun) {
    process.stdout.write(`${JSON.stringify(plan)}\n`)
    return
  }

  requireNativeHost(targetPlatform)
  if (!runtimeInstaller) {
    const condaExecutable = process.env.UNILAB_CONDA_EXE
      ? resolve(process.env.UNILAB_CONDA_EXE)
      : null
    if (!condaExecutable || !existsSync(condaExecutable)) {
      throw new Error(
        '缺少 UNILAB_CONDA_EXE：Unix 请指向 micromamba，Windows 请指向兼容的 conda-standalone'
      )
    }
    const localChannelDirectory = join(artifactsDirectory, 'runtime-conda')
    mkdirSync(localChannelDirectory, { recursive: true })
    run(
      process.env.UNILAB_RATTLER_BUILD_COMMAND ?? 'rattler-build',
      [
        'build',
        '-r',
        join(osDirectory, '.conda', 'vendor', 'rfc8785', 'recipe.yaml'),
        '--target-platform',
        targetPlatform,
        '-c',
        'conda-forge',
        '--output-dir',
        localChannelDirectory,
        '--test',
        'native'
      ],
      osDirectory,
      process.env
    )
    run(
      process.env.UNILAB_RATTLER_BUILD_COMMAND ?? 'rattler-build',
      [
        'build',
        '-r',
        join(osDirectory, '.conda', 'vendor', 'msgcenterpy', 'recipe.yaml'),
        '--target-platform',
        targetPlatform,
        '-c',
        'conda-forge',
        '--channel',
        localChannelDirectory,
        '--output-dir',
        localChannelDirectory,
        '--test',
        'native'
      ],
      osDirectory,
      process.env
    )
    run(
      process.env.UNILAB_RATTLER_BUILD_COMMAND ?? 'rattler-build',
      [
        'build',
        '-r',
        join(osDirectory, '.conda', 'vendor', 'pylabrobot', 'recipe.yaml'),
        '--target-platform',
        targetPlatform,
        '-c',
        'conda-forge',
        '--channel',
        localChannelDirectory,
        '--output-dir',
        localChannelDirectory,
        '--test',
        'native'
      ],
      osDirectory,
      process.env
    )
    run(
      process.env.UNILAB_RATTLER_BUILD_COMMAND ?? 'rattler-build',
      [
        'build',
        '-r',
        join(osDirectory, '.conda', 'base', 'recipe.yaml'),
        '--target-platform',
        targetPlatform,
        '-c',
        'uni-lab',
        '-c',
        'robostack-staging',
        '-c',
        'conda-forge',
        '--channel',
        localChannelDirectory,
        '--output-dir',
        localChannelDirectory,
        '--test',
        'native'
      ],
      osDirectory,
      process.env
    )
    const outputDirectory = join(
      artifactsDirectory,
      'runtime-installer',
      targetPlatform
    )
    mkdirSync(outputDirectory, { recursive: true })
    run(
      process.env.UNILAB_CONSTRUCTOR_COMMAND ?? 'constructor',
      [
        join(osDirectory, '.conda', 'constructor'),
        '--platform',
        targetPlatform,
        '--conda-exe',
        condaExecutable,
        '--output-dir',
        outputDirectory
      ],
      osDirectory,
      {
        ...process.env,
        UNILABOS_INSTALLER_VERSION: runtimeVersion,
        UNILABOS_INSTALLER_PACKAGE:
          process.env.UNILABOS_INSTALLER_PACKAGE ?? 'unilabos',
        UNILABOS_INSTALLER_CHANNEL:
          pathToFileURL(localChannelDirectory).href
      }
    )
    runtimeInstaller = findConstructorInstaller(
      outputDirectory,
      targetPlatform
    )
  }

  run(
    process.env.UNILAB_PNPM_COMMAND
      ?? (process.platform === 'win32' ? 'pnpm.cmd' : 'pnpm'),
    [
      '--dir',
      frontendDirectory,
      '--filter',
      '@unilab/desktop',
      DESKTOP_SCRIPTS[targetPlatform]
    ],
    frontendDirectory,
    {
      ...process.env,
      UNILAB_RUNTIME_INSTALLER: runtimeInstaller,
      UNILAB_RUNTIME_VERSION: runtimeVersion,
      UNILAB_RUNTIME_PLATFORM: targetPlatform
    }
  )
  process.stdout.write(`${JSON.stringify({
    ...plan,
    runtimeInstaller,
    releaseDirectory: join(frontendDirectory, 'apps', 'desktop', 'release')
  })}\n`)
}

function parseArguments(argumentsList) {
  const options = {
    platform: null,
    runtimeInstaller: null,
    runtimeVersion: null,
    dryRun: false
  }
  for (let index = 0; index < argumentsList.length; index += 1) {
    const argument = argumentsList[index]
    if (argument === '--dry-run') {
      options.dryRun = true
      continue
    }
    if (
      argument === '--platform'
      || argument === '--runtime-installer'
      || argument === '--runtime-version'
    ) {
      const value = argumentsList[index + 1]
      if (!value || value.startsWith('--')) {
        throw new Error(`${argument} 缺少值`)
      }
      index += 1
      if (argument === '--platform') options.platform = value
      if (argument === '--runtime-installer') options.runtimeInstaller = value
      if (argument === '--runtime-version') options.runtimeVersion = value
      continue
    }
    throw new Error(`未知参数：${argument}`)
  }
  return options
}

function normalizePlatform(value) {
  const normalized = PLATFORM_ALIASES.get(value)
  if (!normalized) throw new Error(`不支持的平台：${value}`)
  return normalized
}

function currentConstructorPlatform() {
  if (hostPlatform === 'linux' && arch === 'x64') return 'linux-64'
  if (hostPlatform === 'darwin' && arch === 'x64') return 'osx-64'
  if (hostPlatform === 'darwin' && arch === 'arm64') return 'osx-arm64'
  if (hostPlatform === 'win32' && arch === 'x64') return 'win-64'
  throw new Error(`当前主机不受支持：${hostPlatform}/${arch}`)
}

function requireNativeHost(targetPlatform) {
  const current = currentConstructorPlatform()
  if (current !== targetPlatform) {
    throw new Error(
      `可发布安装包必须原生构建：当前 ${current}，目标 ${targetPlatform}`
    )
  }
}

function sourceRuntimeVersion() {
  const source = readFileSync(
    join(osDirectory, 'unilabos', '__init__.py'),
    'utf8'
  )
  const match = source.match(/^__version__\s*=\s*["']([^"']+)["']/m)
  if (!match) throw new Error('无法读取 Uni-Lab-OS 版本')
  return match[1]
}

function findConstructorInstaller(outputDirectory, targetPlatform) {
  const extension = targetPlatform === 'win-64' ? '.exe' : '.sh'
  const candidates = readdirSync(outputDirectory)
    .filter((name) => name.toLowerCase().endsWith(extension))
    .map((name) => join(outputDirectory, name))
  if (candidates.length !== 1) {
    throw new Error(
      `Constructor 产物数量异常：预期 1 个，实际 ${candidates.length}`
    )
  }
  return candidates[0]
}

function run(command, args, cwd, environment) {
  const result = spawnSync(command, args, {
    cwd,
    env: environment,
    stdio: 'inherit',
    shell: false
  })
  if (result.error) throw result.error
  if (result.status !== 0) {
    throw new Error(`${command} 执行失败，退出码 ${String(result.status)}`)
  }
}

try {
  main()
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : error}\n`)
  process.exitCode = 1
}
