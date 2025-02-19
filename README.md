# Unity i18n Patch_Font

这是一款用于自动对 JSON 文件进行补丁更新的工具。工具会对比新旧 JSON 文件，根据预先定义的 Schema 判断文件类型，并对指定的键值进行更新替换。工具支持国际化，默认语言为英文（en-us），同时也提供中文（zh-cn）和日语（ja-jp）版本。

------

## 1. 需要准备的内容

### 1.1 Python 环境

- 确保电脑上已安装 Python（建议使用 Python 3.6 及以上版本）。

### 1.2 Schema 文件

- 在工具的主目录下创建一个名为 **Schema** 的文件夹。
- 将以下 Schema 文件放入该文件夹：
  - **UnityDefaultFont_Ext.json**
  - **TextMeshPro_MonoBehavior.json**
  - **NGUI_MonoBehavior.json**
  - **NGUI_Sprite_MonoBehavior.json**

这些 Schema 文件定义了 JSON 文件应当包含的最小结构，工具将依据它们判断 JSON 文件的类型。

### 1.3 国际化文件

- 工具使用 JSON 格式的国际化文件。默认语言为 **en-us**，另外还提供 **zh-cn.json**（简体中文）和 **ja-jp.json**（日语）版本。
- 请确保这些文件与源代码文件（如 `patch_tool.py`）位于同一目录中。

### 1.4 测试用 JSON 文件

- 准备一对旧文件和新文件，要求这两份文件均符合同一 Schema 类型。
- 新文件中应包含需要更新的键值，而旧文件则为待替换文件。建议事先备份原始文件以防操作失误。

------

## 2. 获得成品

### 2.1 下载/克隆项目代码

- 从项目代码仓库下载或克隆代码到本地电脑。
- 成品应包括：
  - 主程序文件 `patch_tool.py`
  - **Schema** 文件夹及其中的各个 Schema 文件
  - 国际化文件，如 `en-us.json`、`zh-cn.json`、`ja-jp.json`
  - 用于测试的 JSON 文件（根据实际情况准备）

### 2.2 文件结构示例

```
pgsqlCopyJSONPatchingTool/
│
├── patch_tool.py
├── en-us.json
├── zh-cn.json
├── ja-jp.json
├── Schema/
│   ├── UnityDefaultFont_Ext.json
│   ├── TextMeshPro_MonoBehavior.json
│   ├── NGUI_MonoBehavior.json
│   └── NGUI_Sprite_MonoBehavior.json
└── (测试用的 JSON 文件)
```

------

## 3. 使用说明

### 3.1 基本使用步骤

#### 3.1.1 打开终端或命令提示符

- **Windows 用户**：在开始菜单中搜索 “cmd” 或 “PowerShell” 并打开。
- **macOS/Linux 用户**：打开 “终端” 应用。

#### 3.1.2 进入项目目录

使用 `cd` 命令进入包含 `patch_tool.py` 的目录。例如：

- Windows 示例：

  ```
  bash
  
  
  Copy
  cd C:\Users\YourName\Documents\JSONPatchingTool
  ```

- macOS/Linux 示例：

  ```
  swift
  
  
  Copy
  cd /Users/YourName/Documents/JSONPatchingTool
  ```

#### 3.1.3 运行程序

在终端中输入如下命令（以下示例使用英文日志，如需中文请将 `-lang` 参数改为 `zh-cn`）：

```
pgsql


Copy
python patch_tool.py -new new_file.json -old old_file.json -lang en-us
```

- 参数说明

  ：

  - `-new`：指定新 JSON 文件的路径。
  - `-old`：指定旧 JSON 文件的路径。
  - `-lang`：指定国际化语言代码（默认 en-us，可选 zh-cn、ja-jp 等）。
  - `-debug`：可选参数，启用调试模式时不会生成补丁文件。

#### 3.1.4 操作提示

- 运行过程中，程序会在终端显示日志信息。
- 当新文件中包含旧文件没有的键时，程序会要求用户确认是否舍弃这些额外的键。此时输入 `Y` 表示确认，输入 `N` 表示取消，程序会据此终止或继续操作。
- 程序完成后，会生成一个补丁文件，其文件名为旧文件名加上 `_patched` 后缀，例如 `old_file_patched.json`。

#### 3.1.5 查看日志

- 程序运行时会生成日志文件，文件名格式为 `YYYY-MM-DD-HHMMSS_log.txt`。日志中记录了所有操作和错误信息，便于排查问题。

### 3.2 非终端用户的操作方式

#### 3.2.1 使用批处理文件（仅适用于 Windows 用户）

1. 打开记事本，复制以下内容（请根据实际情况修改文件名和路径）：

   ```
   batchCopy@echo off
   python patch_tool.py -new new_file.json -old old_file.json -lang en-us
   pause
   ```

2. 将文件保存为 `run_patch.bat`。

3. 双击 `run_patch.bat` 文件即可运行工具。

#### 3.2.2 使用桌面快捷方式

- 您可以在桌面创建一个快捷方式，快捷方式的目标指向上述批处理文件或直接指向 Python 命令（需配置好路径），以便双击运行工具。

------

## 4. 注意事项

- **文件路径**：请确保所有文件路径正确，Schema 文件和国际化文件应放在正确的位置。
- **备份原始数据**：在使用工具前，请备份好原始 JSON 文件，以防更新过程中出现意外。
- **日志检查**：如遇错误，请查看生成的日志文件，日志中记录了详细的错误信息，便于问题排查。
- **扩展与定制**：如需扩展工具功能或修改替换规则，请参考 `patch_tool.py` 源代码中的详细注释部分。
