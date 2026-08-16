# Uni-Lab 统一离线打包

## 打包结果

统一打包入口会把当前 checkout 的 Uni-Lab-OS 构建为私有 Conda Runtime，使用
Constructor 生成离线 Runtime 安装器，再把该安装器和 SHA-256 manifest 嵌入 Electron
安装包。最终用户只需安装桌面端，不需要另外拉取 Uni-Lab-OS 源码或预装 Conda。

PLC-Sim 和领域设备包不随桌面端打包。用户在桌面端选择源码目录或可执行文件后分别
启动；未签名或签名无效的设备包会显示警告，在用户确认后仍可启动并写入本机审计记录。

## 可测试的源码组合

一键打包只以 `Uni-Lab-Core` 当前提交记录的两个 submodule 指针为准。正式 0.1.0 组合
保留现有 Workbench workflow/inventory 业务树，只提取 Constructor、managed-runtime
Supervisor、前端安装控制面和统一打包能力。不要把历史 `df829970` 或
`feat/managed-runtime-installer` 的整棵业务树再次合入。

`deepmodeling/Uni-Lab-OS:dev` 的 Jazzy、Python 3.12、NumPy 2 与网络驱动迁移不属于
0.1.0 打包基线；它应在后续独立兼容性工作中合入和验证。

### 推荐：由 Core 自动锁定子模块

```bash
git clone --recurse-submodules git@github.com:Uni-Lab-OS/Uni-Lab-Core.git
cd Uni-Lab-Core
git submodule update --init --recursive
pnpm --dir uni-lab-fe install --frozen-lockfile
```

如果已经克隆了 Core：

```bash
git fetch origin
git switch main
git pull --ff-only
git submodule update --init --recursive
pnpm --dir uni-lab-fe install --frozen-lockfile
```

执行 `git submodule update` 后，子模块通常处于 detached HEAD，这是 Git 按 Core 锁定提交
工作的正常状态，不需要再手工切换 FE 或 OS 分支。可用下面的命令核对：

```bash
git branch --show-current
git submodule status
```

预期值以 `git submodule status` 为准，不再维护第二套手工分支组合。

## 新命令

日常使用直接运行根 `package.json` 中的平台别名：

| 命令 | 目标平台 |
| --- | --- |
| `pnpm build:linux` | Linux x86_64 |
| `pnpm build:mac` | macOS Apple Silicon |
| `pnpm build:mac-intel` | macOS Intel |
| `pnpm build:win` | Windows x86_64 |

例如，在 Apple Silicon Mac 上打包完整的 Runtime 和正式 Workbench（默认开发验收使用
ad-hoc 签名）：

```bash
pnpm build:mac
```

这些短命令默认从当前 OS 源码读取 Runtime 版本，也可以继续附加统一入口参数。例如只重打
Linux Electron 安装包：

```bash
pnpm build:linux \
  --runtime-version 0.11.3 \
  --runtime-installer artifacts/runtime-installer/linux-64/Uni-Lab-OS-0.11.3-linux-64.sh
```

需要显式指定平台、用于 CI 或脚本集成时，仍可使用通用形式。

在包含 `Uni-Lab-OS` 和 `uni-lab-fe` 子模块的 Uni-Lab-Core 根目录执行：

```bash
pnpm package:unified --platform linux-64 --runtime-version 0.11.3
```

`pnpm 10` 不需要在脚本名和参数之间再写一个 `--`。下面的写法会把字面量 `--` 传给
Node 脚本并报 `未知参数：--`，不要使用：

```text
pnpm package:unified -- --platform linux-64
```

省略 `--platform` 时使用当前主机平台，省略 `--runtime-version` 时读取当前
`Uni-Lab-OS/unilabos/__init__.py` 中的版本。

`--release-mode production` 在 macOS 使用 Developer ID 与 notarization；
`development`/`adhoc` 使用清晰标记的临时签名验收包。

## 支持的平台

| 命令输入 | 规范平台 | 必须使用的原生主机 | Runtime 产物 | 桌面产物 |
| --- | --- | --- | --- | --- |
| `linux`、`linux-64` | `linux-64` | Linux x86_64 | `.sh` | `.AppImage` |
| `osx`、`osx-64` | `osx-64` | macOS Intel | `.sh` | `.dmg` |
| `osx-arm64` | `osx-arm64` | macOS Apple Silicon | `.sh` | `.dmg` |
| `win-64` | `win-64` | Windows x86_64 | `.exe` | `*-setup.exe` |

可发布安装包不允许跨平台生成。例如，在 Linux 主机执行 `--platform win-64` 会立即
失败。四种规范平台由 `.github/workflows/unified-desktop-build.yml` 中对应的原生 runner
并行构建。

## 首次准备

1. 拉取子模块并安装前端依赖：

   ```bash
   git submodule update --init --recursive
   pnpm --dir uni-lab-fe install --frozen-lockfile
   ```

2. 使用 Node.js 22、pnpm 10.13.1，并创建固定版本的打包环境。

   Linux 和 macOS：

   ```bash
   conda create -n constructor-build --override-channels -c conda-forge \
     constructor=3.16.1 micromamba=2.8.1 rattler-build=0.72.2 -y
   conda activate constructor-build
   export UNILAB_CONDA_EXE="$(command -v micromamba)"
   ```

   Windows（在 Miniforge Bash 中）：

   ```bash
   conda create -n constructor-build --override-channels -c conda-forge \
     constructor=3.16.1 conda-standalone=26.3.2.post1 rattler-build=0.72.2 -y
   conda activate constructor-build
   export UNILAB_CONDA_EXE="$CONDA_PREFIX/standalone_conda/conda.exe"
   ```

`UNILAB_CONDA_EXE` 是 Constructor 制作离线 Runtime 时使用的执行器。Unix 必须指向
micromamba，Windows 必须指向兼容的 conda-standalone；它不是最终用户需要预装的依赖。

## 两种打包方式

### 从当前源码完整打包

推荐用于发布或验证当前 OS 改动：

```bash
pnpm package:unified --platform linux-64 --runtime-version 0.11.3
```

该命令依次执行：

1. 用 `rattler-build` 构建 RFC 8785、msgcenterpy、pylabrobot 和当前 Uni-Lab-OS；
2. 将包发布到本地 `file://` Conda channel；
3. 用 Constructor 生成私有 Runtime 安装器；
4. 生成 Runtime manifest，记录版本、平台、文件名和 SHA-256；
5. 构建 Electron，并验证 Runtime payload 确实存在于安装包；
6. 将最终桌面安装包复制到统一 release 目录。

本地 channel 始终位于远端 channel 之前，因此打包的是当前 checkout，而不是远端恰好
具有相同版本号的包。

### 复用已经验证的 Runtime 安装器

只修改了前端或 Electron 时，可以跳过 Conda 和 Constructor 阶段：

```bash
pnpm package:unified \
  --platform linux-64 \
  --runtime-version 0.11.3 \
  --runtime-installer artifacts/runtime-installer/linux-64/Uni-Lab-OS-0.11.3-linux-64.sh
```

`--runtime-installer` 可以是相对路径或绝对路径。脚本仍会生成 manifest、校验 payload，
并重新构建桌面安装包。调用方必须保证安装器的平台和版本与参数一致；桌面打包层还会
校验 manifest 中的平台、文件存在性和 SHA-256。

## 参数与环境变量

| 参数 | 作用 |
| --- | --- |
| `--platform <name>` | 目标平台；默认自动识别当前主机 |
| `--runtime-version <version>` | Runtime/manifest 版本；默认读取 OS 源码版本 |
| `--runtime-installer <path>` | 复用已有 Runtime 安装器，跳过 Conda 与 Constructor |
| `--dry-run` | 只输出规范化后的执行计划，不构建任何文件 |

常用 dry-run：

```bash
pnpm package:unified --platform win-64 --runtime-version 0.11.3 --dry-run
```

| 环境变量 | 默认值/作用 |
| --- | --- |
| `UNILAB_CONDA_EXE` | 完整打包必填；micromamba 或 Windows conda-standalone 的绝对路径 |
| `UNILAB_ARTIFACTS_DIRECTORY` | 默认 `<Core>/artifacts` |
| `UNILABOS_INSTALLER_PACKAGE` | 默认 `unilabos`；需要完整变体时设为 `unilabos-full` |
| `UNILAB_RATTLER_BUILD_COMMAND` | 默认 `rattler-build` |
| `UNILAB_CONSTRUCTOR_COMMAND` | 默认 `constructor` |
| `UNILAB_PNPM_COMMAND` | Unix 默认 `pnpm`，Windows 默认 `pnpm.cmd` |

命令内部设置 `UNILABOS_INSTALLER_CHANNEL`、`UNILAB_RUNTIME_INSTALLER`、
`UNILAB_RUNTIME_VERSION` 和 `UNILAB_RUNTIME_PLATFORM`，正常使用时不要手工覆盖。

## 产物位置

| 内容 | 目录 |
| --- | --- |
| 本地 Conda channel | `artifacts/runtime-conda/` |
| Constructor Runtime | `artifacts/runtime-installer/<platform>/` |
| Workbench macOS 安装包 | `uni-lab-fe/apps/workbench/release-macos/` |
| Workbench Linux 安装包 | `uni-lab-fe/apps/workbench/release-linux/` |
| Workbench Windows 安装包 | `uni-lab-fe/apps/workbench/release-windows/` |

本地命令完成后可生成或核验 SHA-256：

```bash
sha256sum \
  artifacts/runtime-installer/linux-64/Uni-Lab-OS-0.11.3-linux-64.sh \
  uni-lab-fe/apps/workbench/release-linux/*.AppImage
```

CI 会额外生成 `SHA256SUMS`。`development` 产物会标记为未签名；`production` 模式会
要求各平台签名材料，并在上传前验证 GPG、Authenticode 或 Apple notarization。

## 自动验证

验证统一入口的参数映射和本地 channel 行为：

```bash
pnpm test:package:unified
```

对最终桌面端还应执行：

```bash
pnpm --dir uni-lab-fe test
pnpm --dir uni-lab-fe typecheck
pnpm --dir uni-lab-fe build:web
pnpm --dir uni-lab-fe build:desktop
```

真实验收还要确认欢迎页在检测不到 `unilab` 时显示“安装内置 Runtime”，安装结束后
`unilab -h` 成功，随后能选择工作区；Theia 的“环境管理”必须投影同一安装状态。

## 常见错误

- `未知参数：--`：删除脚本名后多余的独立 `--`。
- `缺少 UNILAB_CONDA_EXE`：按当前平台设置 micromamba 或 conda-standalone 绝对路径。
- `可发布安装包必须原生构建`：改在目标平台主机运行，或使用统一 CI matrix。
- `Runtime 安装器不存在`：检查 `--runtime-installer` 路径；相对路径以 Core 根目录解析。
- `Constructor 产物数量异常`：清理对应 `artifacts/runtime-installer/<platform>/` 中无关的
  `.sh`/`.exe` 后重试。
- Workbench 打包缺少 Runtime manifest 或 SHA 不匹配：不要单独调用底层 `package:linux`、
  `package:mac`、`package:win`；从 Core 根目录使用统一入口。
