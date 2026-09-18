<div align="center">
  <img src="./assets/logo.png" alt="EasyGEE" width="96" />
  <h1>EasyGEE</h1>

  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-0F766E?style=flat-square" /></a>
  <a href="./.codex-plugin/plugin.json"><img alt="Plugin" src="https://img.shields.io/badge/plugin-Codex%20%7C%20Claude-2563EB?style=flat-square" /></a>
  <a href="./.mcp.json"><img alt="MCP" src="https://img.shields.io/badge/MCP-stdio-111827?style=flat-square" /></a>

  **中文** · [English](./README_en.md)

  面向 AI Agent 的 Google Earth Engine / geemap 工作台插件。

  [能力](#能力) · [结构](#结构) · [使用](#使用) · [安全](#安全) · [致谢](#致谢)
</div>

## 能力

EasyGEE 把 Google Earth Engine、geemap、GeoMaster 方法知识和本地浏览器地图工作台打包成一个可复用插件。它的目标不是复刻 GEE 网页控制台，而是让 Agent 用一句自然语言完成数据查找、授权引导、配额检查、地图预览和本地/云端地理空间分析编排。

- 在 5,000 多个 GEE 官方与社区目录记录中，按数据集 ID、名称、主题或中英文任务检索；排序会考虑来源、弃用状态和匹配证据。
- 把完整任务拆成数据角色组合，例如洪水风险的灾情、长期基线、地形、降雨和人口/建筑暴露，并支持候选比较与最终资产核验。
- 标准化 Earth Engine / geemap 授权流程，不暴露 OAuth token、验证码、凭据文件或 service account key。
- 查询 Earth Engine 项目配额和用量，并把结果转成 Agent 可读的摘要。
- 生成可持久化的 EasyGEE 地图工作台（Map Console），用于 AOI 绘制、图层叠加、底图配置和视觉检查；地图视图、收藏、自定义底图与近期图层按本机用户和项目恢复。在 EasyGEE 语境下，“打开地图”“地图工作台”和“地图控制台”都指向它。
- 支持 XYZ、TMS、ArcGIS、WMS、WMTS、栅格 PMTiles 与 COG 数据源，并内置天地图矢量、影像和地形预设；底图可叠加到图层后调整顺序、可见性和不透明度。
- 使用 HTTP Range、会话缓存和按需加载的 MapLibre WebGL 引擎加速 PMTiles/COG，并只向 Agent 同步精简性能摘要，影像字节与瓦片日志留在本地数据平面。
- 内置 GeoMaster skill，覆盖 CRS、本地 GIS、遥感、机器学习、STAC/COG、科学领域方法和排错经验。
- 内置 GeoAI Encyclopedia 作为遥感 AI 方法层，覆盖图像识别、目标检测、语义/实例分割、变化检测、像素回归、SAM、卫星嵌入、视觉语言模型和 QGIS GeoAI；按任务只加载相关章节，并明确 GEE 到本地模型的交接契约。
- 内置 GEE Growth Diary skill，将 GEEer成长日记 153 篇 GEE 文章蒸馏为数据集选择、指数、时序、分类、水体、图表和导出方法库。
- 内置遥感方法卡与可视化案例，覆盖 Landsat 去云、Sentinel-2 去云、HLS 跨传感器一致化、时间合成、Sentinel-1 SAR 以及 Landsat/Sentinel-2 对比。

## 结构

<details>
<summary>点击展开项目结构</summary>

```text
easygee/
├── .codex-plugin/       # Codex 插件元数据
├── .claude-plugin/      # Claude Code 插件与 marketplace 元数据
├── .mcp.json            # MCP 服务声明（Codex 与其他 MCP 客户端）
├── assets/              # EasyGEE logo
├── commands/            # Claude Code 快捷命令
├── scripts/             # MCP 服务与安装器（install.py）
├── skills/
│   ├── easygee/         # GEE / geemap / 地图工作台与遥感方法工作流
│   │   ├── references/  # 按需读取的方法资料
│   │   ├── assets/      # 地图工作台前端模板
│   │   └── scripts/     # 数据检索、任务路由、案例和离线评测
│   └── multimodal-geo-vector/ # 影像标注转 CRS 矢量
├── extras/
│   ├── geomaster/       # 本地 GIS 与遥感方法知识（由 easygee 按需读取）
│   └── gee-growth-diary/ # GEEer成长日记蒸馏方法库（由 easygee 按需读取）
└── requirements*.txt    # Python 依赖
```

</details>

## 使用

### 1. 快速安装

给 Agent 的一句话安装：

```text
帮我安装这个插件：[Rimagination/easygee](https://github.com/Rimagination/easygee)
```

Agent 应克隆仓库到 `~/plugins/easygee`，再运行 `python scripts/install.py`。

也可以手动运行（需要 Python 3.9+ 和 git）：

```bash
git clone https://github.com/Rimagination/easygee.git ~/plugins/easygee
python ~/plugins/easygee/scripts/install.py
```

Windows 上也可以运行这一行，它会克隆或更新仓库并调用同一个安装器：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command '$p=Join-Path $HOME "plugins\easygee"; if(Test-Path $p){ git -C $p pull --ff-only } else { git clone https://github.com/Rimagination/easygee.git $p }; & (Join-Path $p "scripts\install-easygee.ps1")'
```

安装器完成两件事：

1. 在 EasyGEE 用户目录下创建 Python 环境（有 uv 时用 uv），安装 `requirements.txt`，并把解释器路径写入 `settings.json`。所有 Agent 共用这个环境。
2. 向本机检测到的 Agent 注册：Codex 与 Claude Code 通过各自的插件命令注册，Qoder 通过技能目录链接接入。

常用参数：

| 参数 | 作用 |
| --- | --- |
| `--hosts codex,claude,qoder` | 指定要注册的 Agent；默认 `auto`，按本机检测结果 |
| `--skills-dir <目录>` | 把技能链接到任意读取 `SKILL.md` 的 Agent 目录 |
| `--python <路径>` | 使用已有的 Python 环境，不新建 |
| `--with-vector` | 同时安装多模态矢量化依赖 |
| `--print-mcp-config` | 输出 MCP 配置片段，供其他 MCP 客户端粘贴 |
| `--uninstall` / `--purge` | 取消注册；`--purge` 同时删除 Python 环境 |
| `--dry-run` | 只显示将执行的操作 |

EasyGEE 用户目录：Windows 为 `%LOCALAPPDATA%\EasyGEE`，其他系统为 `~/.config/easygee`。工作区、缓存与解释器路径可在 `settings.json` 中修改，或用环境变量 `EASYGEE_WORKSPACE`、`EASYGEE_CACHE_DIR`、`EASYGEE_PYTHON` 覆盖。

### 2. 快速使用

直接用自然语言告诉 Agent 你要做什么。下面这些例子覆盖了最常见的日常用法：

```text
帮我授权 geemap 到 example-ee-project-123456

打开地图工作台，我想先看看北京朝阳公园附近，然后手动画一个 AOI

我想做北京朝阳公园 2024 年夏季 NDVI，帮我选择合适的 GEE 数据集并解释为什么

在 5000 多个数据集中查找 DEM，只看未弃用的官方产品，并比较前三个

我要评估山区洪水风险；我还没选数据，请按灾情、地形、降雨和暴露角色推荐一组数据

比较 COPERNICUS/DEM/GLO30_2024_1 和 USGS/SRTMGL1_003，并在写代码前核验最终 ID

把 Sentinel-2 真彩色和 NDVI 叠加到地图上，我想在浏览器里检查云和植被情况

查看我的 Earth Engine 项目配额、用量层级和剩余额度

帮我把当前 AOI 的 NDVI 结果导出到 Google Drive，并告诉我导出参数是否合理

我有一个本地 GeoJSON，帮我判断应该用 GEE 处理还是本地 GIS 处理，并生成可运行脚本
```

## 安全

EasyGEE 默认把浏览器和凭据当作用户私有空间。Agent 可以生成授权计划、启动本地工具、查询安全摘要，但不能要求用户把 OAuth URL、验证码、token、credential 文件、service account key 或短期 access token 粘贴到聊天、日志、文档或提交里。

GeoMaster 以 skill snapshot 形式内置在插件中，而不是嵌套 git 仓库。这样插件保持自包含、轻量、离线可用，也避免把依赖目录、历史仓库状态或未知远端同步进插件包。

## 致谢

EasyGEE 参考并蒸馏了许多开放资料和项目经验。特别感谢：

- [Google Earth Engine 官方文档](https://developers.google.com/earth-engine)：认证、初始化、配额、导出、客户端/服务端模型和遥感工作流的主要依据。
- [Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/) 与 [Earth Engine STAC Catalog](https://storage.googleapis.com/earthengine-stac/catalog/catalog.json)：EasyGEE 数据目录、数据集介绍和图层搜索的核心来源。
- [GEE Community Catalog](https://gee-community-catalog.org/) 与 [community_datasets.csv](https://github.com/sadassimov/geemu-skill/blob/main/awesome-gee-community-datasets/community_datasets.csv)：用于扩展官方目录之外的社区数据集。
- 微信公众号 [GEEer成长日记](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkzNjMxNDk1NQ==&action=getalbum&album_id=2182256849633247236)：提供了大量中文 GEE 实践案例和任务灵感，帮助 EasyGEE 梳理更贴近中文用户表达的遥感工作流。
- 微信公众号 [野火遥感Fire Centre](https://mp.weixin.qq.com/s/pEVuV8Q4dH2BWv_zQCDmZQ)：提供了野火遥感、灾害监测与应用案例方面的中文实践参考。
- [GEEMu Skill](https://github.com/sadassimov/geemu-skill)：启发了 EasyGEE 对本地轻量知识检索、数据语义记录、边界/计算 gate 和导出 dry-run 模式的进一步整理。
- [geemap](https://geemap.org/) / [gee-community/geemap](https://github.com/gee-community/geemap)：GEE Python 交互式地图、Notebook 工作流、导出工具和数据集探索模式的重要参考。
- [Qiusheng Wu 的 Earth-Engine-Catalog](https://github.com/giswqs/Earth-Engine-Catalog)：轻量机器可读 GEE 数据目录索引。
- [OpenGeoAgent / GeoAgent](https://github.com/opengeos/GeoAgent)、[GeoLibre](https://github.com/opengeos/GeoLibre)、[leafmap](https://leafmap.org/) 与 [anymap](https://github.com/opengeos/anymap)：启发了 EasyGEE 的地图优先、Agent 驱动和本地优先 GIS 工作台设计。
- [Insight Maps](https://map.insightmaps.app/)：参考了其紧凑地图工具栏、图层目录和专业 Web GIS 交互风格。
- [netease-youdao/LobsterAI](https://github.com/netease-youdao/LobsterAI)：README 首屏结构、徽章和语言切换排版的参考。
- [GeoAI Book](https://book.opengeoai.org/) 与 [GeoAI-Book](https://github.com/giswqs/GeoAI-Book)：EasyGEE 内置 GeoAI Encyclopedia 的任务方法、训练/推理和空间评估来源。
- [Segment Geospatial](https://samgeo.gishub.org/)：GeoAI Encyclopedia 中地理空间 SAM 分割模式的重要参考。
- [NASA HLS L30](https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSL30_v002) 与 [HLS S30](https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSS30_v002)：Landsat/Sentinel-2 30 m NBAR、一致化处理、公共波段和 Fmask 语义的官方来源。
- [USGS CFMask](https://www.usgs.gov/landsat-missions/cfmask-algorithm) 与 [Landsat 云算法验证研究](https://www.usgs.gov/publications/cloud-detection-algorithm-comparison-and-validation-operational-landsat-data-products)：Landsat QA_PIXEL、CFMask 方法边界和验证依据。
- [Sentinel-1 Algorithms](https://developers.google.com/earth-engine/guides/sentinel1)：SAR GRD 预处理、极化/轨道筛选、dB 后向散射和地形限制的官方来源。
- [Earth Engine Compositing and Mosaicking](https://developers.google.com/earth-engine/guides/ic_composite_mosaic) 与 [`qualityMosaic()` API](https://developers.google.com/earth-engine/apidocs/ee-imagecollection-qualitymosaic)：时间合成、镶嵌、质量像元和像元来源语义的官方来源。

更完整的来源与归因记录见 [skills/easygee/references/SOURCES.md](./skills/easygee/references/SOURCES.md)。
