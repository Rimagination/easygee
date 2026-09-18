    const STATE = __EASYGEE_STATE_JSON__;
    const COG_ENGINE_ASSETS = __EASYGEE_COG_ASSETS_JSON__;
    STATE.layers = Array.isArray(STATE.layers) ? STATE.layers : [];
    STATE.layerOrder = Array.isArray(STATE.layerOrder) ? STATE.layerOrder.map(value => String(value)) : [];
    STATE.catalog = Array.isArray(STATE.catalog) ? STATE.catalog : [];
    STATE.tasks = Array.isArray(STATE.tasks) ? STATE.tasks : [];
    STATE.uploads = Array.isArray(STATE.uploads) ? STATE.uploads : [];
    const logLines = [];
    const layerRegistry = new Map();
    const layerRefreshTokens = new Map();
    const I18N = {
      zh: {
        "tool.data": "添加图层",
        "tool.upload": "上传地图数据",
        "tool.layers": "图层",
        "tool.layersMeasurementReady": "图层：测距结果已加入",
        "tool.layersMeasurePrompt": "图层：测距结果会自动加入",
        "tool.inspector": "查看器",
        "tool.drawAoi": "绘制 AOI",
        "tool.measure": "测距",
        "tool.measureActive": "测距已开启 · 结果自动加入图层",
        "tool.measureUndo": "撤回上一步",
        "tool.clearMeasurements": "清除测距",
        "tool.basemap": "底图",
        "tool.quota": "配额状态",
        "tool.drive": "Google 云盘",
        "tool.driveRecent": "打开最近的 Drive 导出",
        "tool.driveRoot": "打开 Google 云盘",
        "tool.home": "回到初始视图",
        "tool.zoomIn": "放大",
        "tool.zoomOut": "缩小",
        "tool.lang": "切换语言",
        "tool.close": "关闭",
        "upload.title": "导入文件",
        "upload.sourceProjection": "源投影",
        "upload.projectionHelp": "仅用于 .shp 文件。ZIP 和 GPKG 会自动识别投影。",
        "upload.chooseFile": "选择文件",
        "upload.noFile": "未选择任何文件",
        "upload.submit": "上传",
        "upload.formats": "SHP, ZIP, KML, KMZ, GPX, GeoJSON, CSV, GPKG · 单个文件最大 50 MB",
        "upload.ready": "已选择 :count 个文件",
        "upload.saving": "正在保存上传文件",
        "upload.saved": "已上传 :count 个文件，并加入图层",
        "upload.savedPartial": "已上传 :total 个文件，其中 :added 个已加入图层",
        "upload.failed": "上传失败：:message",
        "upload.tooLarge": ":name 超过 50 MB",
        "upload.empty": "上传记录会显示在这里，并同步给 agent。",
        "upload.agentReady": "agent 可处理",
        "upload.layerAdded": "已加入图层",
        "upload.notRenderable": "未加入图层：缺少可渲染几何",
        "upload.remove": "移除上传记录",
        "tool.styleLayer": "设置图层样式",
        "tool.zoomToLayer": "缩放到图层",
        "tool.refreshLayer": "刷新图层",
        "tool.dragLayer": "拖动排序",
        "tool.removeLayer": "移除图层",
        "tool.basemapSource": "查看地图来源",
        "tool.clearAoi": "清除 AOI",
        "panel.data": "添加图层",
        "panel.dataSubtitle": "搜索与添加 Earth Engine 数据集",
        "panel.basemap": "底图",
        "source.title": "底图来源",
        "source.provider": "提供方",
        "source.date": "影像日期",
        "source.engine": "数据引擎",
        "source.performance": "加载性能",
        "source.performanceIdle": "尚未采样",
        "source.performanceLoading": "等待首屏…",
        "source.performanceSettling": "首屏 :first · 收尾中…",
        "source.performanceReady": "首屏 :first · 完成 :ready",
        "source.performanceFailed": "加载失败",
        "source.delivery": "传输",
        "source.deliveryIdle": "尚无本次加载数据",
        "source.deliveryLoading": ":cache · 统计中…",
        "source.cacheCold": "会话冷启",
        "source.cacheWarm": "会话热启",
        "source.cacheUnknown": "会话缓存未知",
        "source.renderedBlocks": ":count 个绘制块",
        "source.sourceRequests": ":count 次源请求",
        "source.networkRestricted": "网络统计受限",
        "source.nativeZoom": "原生层级",
        "source.nativeZoomValue": "Z0–Z:zoom",
        "source.attribution": "版权说明",
        "source.open": "查看官方数据源",
        "source.trigger": "查看当前底图来源",
        "panel.layers": "图层",
        "panel.inspector": "查看器",
        "section.layerStack": "图层栈",
        "section.operationalLayers": "数据与叠加图层",
        "section.layerReorderHint": "拖动排序",
        "section.primaryBasemap": "主底图",
        "section.primaryBasemapHint": "固定在最底层",
        "placeholder.searchDatasets": "按名称、类别或 ID 搜索图层",
        "placeholder.filterOptions": "筛选类别...",
        "catalog.categories": "分类（当前类型）",
        "catalog.all": "全部",
        "catalog.typeAll": "全部",
        "catalog.typeImageCollection": "影像集合",
        "catalog.typeImage": "影像",
        "catalog.typeTable": "矢量/表",
        "catalog.typeOther": "其他",
        "catalog.favorites": "收藏夹",
        "catalog.favoriteChip": "收藏 (:count)",
        "catalog.sourceOfficial": "官方",
        "catalog.sourceCommunity": "社区",
        "catalog.sourceCurated": "精选",
        "card.mapClick": "地图点击",
        "card.activeLayer": "当前图层",
        "card.legend": "图例",
        "card.tasks": "任务",
        "key.latitude": "纬度",
        "key.longitude": "经度",
        "key.zoom": "缩放",
        "key.name": "名称",
        "key.dataset": "数据集",
        "key.type": "类型",
        "key.recipe": "配方",
        "key.opacity": "不透明度",
        "label.opacity": "不透明度",
        "label.color": "颜色",
        "label.palette": "色带",
        "layers.empty": "还没有图层。点“添加图层”搜索 GEE 数据集。",
        "layers.emptyOperational": "还没有数据或叠加图层。",
        "tasks.empty": "暂无任务。Agent 发起的导出和后台处理会显示在这里。",
        "task.destination": "目的地",
        "task.folder": "文件夹",
        "task.prefix": "文件前缀",
        "task.id": "任务 ID",
        "task.params": "参数",
        "task.driveSearch": "Drive 搜索",
        "task.createdAt": "创建于",
        "layer.none": "未选择图层",
        "measurements.layerName": "测距",
        "measurements.layerDataset": "已保存测距标记（:count 条）",
        "measurements.legend": "测距线",
        "measurements.count": "数量",
        "measurements.summary": ":count 条，合计 :total",
        "badge.noLayer": "EasyGEE 地图",
        "badge.basemap": "底图：:basemap",
        "badge.basemapSource": "底图来源：:source",
        "bottom.project": "配额",
        "link.quota": "控制台",
        "action.copy": "复制",
        "action.json": "JSON",
        "action.copyTitle": "复制项目状态",
        "action.jsonTitle": "下载项目 JSON",
        "pill.project": "项目：:project",
        "pill.aoi": "AOI：:lat, :lon",
        "pill.layers": ":count 个图层",
        "pill.layersWithBasemap": ":count 个图层 · 1 个底图",
        "pill.datasets": ":count 个数据集",
        "pill.datasetMatches": ":shown/:total 个数据集",
        "pill.datasetLoaded": "已加载 :shown / 共 :matches",
        "pill.datasetLoadedFiltered": "已加载 :shown / 命中 :matches / 全部 :total",
        "data.loadingMore": "继续加载中",
        "data.ready": "可直接添加 · :count 个图层",
        "data.catalogItem": "可处理目录项",
        "data.addHint": "点击 + 后本地处理并加入地图",
        "data.noResults": "没有匹配的数据集",
        "data.noFavorites": "还没有收藏的数据集。点星标加入收藏夹。",
        "data.addTitle": "加入地图",
        "data.favoriteTitle": "收藏数据集",
        "data.unfavoriteTitle": "取消收藏",
        "data.openCatalog": "打开数据目录",
        "data.openSample": "示例代码",
        "data.addFromDetail": "加入地图",
        "data.copyId": "复制 ID",
        "data.copyContext": "复制上下文",
        "data.contextCopied": "数据集上下文已复制",
        "data.previewRecipe": "默认预览",
        "data.detailSource": "来源",
        "data.detailType": "类型",
        "data.detailProvider": "提供方",
        "data.detailLicense": "许可",
        "data.detailDates": "时间范围",
        "data.detailDescription": "简介",
        "data.detailTags": "标签",
        "data.detailNoDescription": "暂无详细简介。请打开数据目录或示例代码核对字段、许可和使用方式。",
        "data.detailCopied": "数据集 ID 已复制",
        "data.attrTime": "时间",
        "data.attrSpan": "跨度",
        "data.attrResolution": "分辨率",
        "data.attrType": "类型",
        "data.attrYear": ":count 年",
        "data.attrMonth": ":count 月",
        "data.processing": "正在处理并生成图层",
        "data.generated": "已可视化",
        "data.failed": "生成失败",
        "state.idle": "待命",
        "state.clicked": "已点击",
        "mode.datasetAdded": "已加入 :count 个图层",
        "mode.datasetBuilding": "正在生成 :dataset",
        "mode.datasetNeedsBuild": "需要用本地预览服务生成图层",
        "mode.datasetFailed": "生成失败：:message",
        "mode.favoriteAdded": "已收藏 :dataset",
        "mode.favoriteRemoved": "已取消收藏 :dataset",
        "mode.quotaReady": "配额：:summary",
        "mode.aoiStart": "AOI：选择第一个角",
        "mode.aoiCorner": "AOI：选择对角",
        "mode.aoiDone": "AOI 已更新",
        "mode.aoiOff": "AOI 绘制已关闭",
        "mode.aoiTooSmall": "AOI 太小",
        "mode.polygonStart": "多边形 AOI：点击添加顶点，双击或按 Enter 完成",
        "mode.polygonVertex": "多边形 AOI：已添加 :count 个顶点",
        "mode.polygonTooSmall": "多边形 AOI 至少需要 3 个顶点",
        "mode.ndviBuilding": "正在提取当前 AOI 的 NDVI",
        "mode.ndviDone": "NDVI 均值 :mean，像元 :count",
        "mode.ndviNoAoi": "请先绘制 AOI 再提取 NDVI",
        "mode.ndviFailed": "NDVI 提取失败：:message",
        "mode.driveExportBuilding": "正在发起 Drive 导出",
        "mode.driveExportDone": "Drive 导出任务已创建：:task",
        "mode.driveExportFailed": "Drive 导出失败：:message",
        "mode.styleBuilding": "正在更新图层样式：:layer",
        "mode.styleApplied": "图层样式已更新：:layer",
        "mode.styleFailed": "样式更新失败：:message",
        "mode.layerZooming": "正在缩放到图层：:layer",
        "mode.layerZoomed": "已缩放到图层：:layer",
        "mode.layerReordered": "图层顺序已更新",
        "mode.layerExtentUnavailable": "无法获取图层范围：:layer",
        "quota.project": "项目：:project",
        "quota.tier": "用量层级：:tier",
        "quota.tierInferred": "用量层级：:tier",
        "quota.tierUnknown": "用量层级：待连接",
        "quota.items": "额度项",
        "quota.summaryLiveUsage": "实时用量可用",
        "quota.summaryLiveLimit": "实时额度可用；用量未接通",
        "quota.summaryDefault": "默认额度；剩余未知",
        "quota.summaryEmpty": "配额数据不可用",
        "quota.issueCloudLogin": "需登录 Google Cloud CLI",
        "quota.issueCloudQuotasApi": "需启用 Cloud Quotas API",
        "quota.issueQuotaPermission": "缺少 Cloud Quotas 权限",
        "quota.issueMonitoringPermission": "缺少 Monitoring 用量权限",
        "quota.issueQuotaNetwork": "gcloud 配额组件/网络异常",
        "quota.issueLiveUnavailable": "实时配额不可用",
        "quota.total": "总额",
        "quota.used": "已用",
        "quota.remaining": "剩余",
        "quota.measured": "可量化",
        "quota.alerts": "预警",
        "quota.noAlerts": "0 项",
        "quota.alertCount": ":count 项",
        "quota.measuredOfTotal": ":count/:total",
        "quota.maxUsed": "最高用量 :percent",
        "quota.usedOfTotal": ":used/:total (:percent)",
        "quota.usedUnlimited": ":used/无限",
        "quota.totalOnly": "总额 :total",
        "quota.remainingValue": "剩余 :remaining",
        "quota.remainingUnlimited": "剩余 无限",
        "quota.unlimited": "无限",
        "quota.usageMissing": "用量未接通",
        "quota.usageUnavailable": "用量未提供",
        "quota.noUsageYet": "暂无用量",
        "quota.limitOnlyState": "仅额度",
        "quota.unlimitedState": "无限额度",
        "quota.noUsageState": "未产生",
        "quota.okState": "余量正常",
        "quota.warnState": "接近上限",
        "quota.notAvailable": "不可用",
        "quota.unknown": "未知",
        "quota.usageRequired": "需要 Cloud Monitoring 用量权限",
        "mode.basemap": "底图：:basemap",
        "mode.tiandituKeyRequired": "请先在底图面板配置天地图 Key",
        "mode.tiandituKeySaved": "天地图 Key 已应用到当前标签页",
        "mode.tiandituKeyRemembered": "天地图 Key 已用 Windows 加密保存在本机",
        "mode.tiandituKeySessionOnly": "已移除本机副本，当前标签页仍可使用",
        "mode.tiandituKeyRememberFailed": "当前标签页可继续使用，本机加密保存失败",
        "mode.basemapOverlayAdded": "已叠加到图层：:basemap",
        "mode.measureStart": "测距：点击两个点",
        "mode.measureOff": "测距已关闭",
        "mode.measureEndpoint": "测距：选择终点",
        "mode.distance": "距离：:distance",
        "mode.measureSaved": "测量已加入图层：:distance（共 :count 条，均值 :mean）",
        "mode.measureUndoDraft": "已撤回上一个测量点",
        "mode.measureUndoSaved": "已撤回上一条测量：:distance",
        "mode.measureUndoEmpty": "暂无可撤回的测量",
        "mode.measureCleared": "测距标记已清除",
        "basemap.osm": "OpenStreetMap",
        "basemap.osmNote": "道路与标注",
        "basemap.light": "浅色",
        "basemap.lightNote": "突出分析图层",
        "basemap.dark": "深色",
        "basemap.darkNote": "夜间对比",
        "basemap.voyager": "彩色",
        "basemap.voyagerNote": "清爽道路与地物",
        "basemap.topo": "地形",
        "basemap.topoNote": "等高线与地貌，高层级自动回退",
        "basemap.topoCoverage": "Esri World Topographic Map · 全球原生覆盖至 z13",
        "basemap.imagery": "影像",
        "basemap.imageryNote": "Esri 全球影像",
        "basemap.esriClarity": "Esri 清晰影像",
        "basemap.esriClarityNote": "清晰度优先的备用影像",
        "basemap.tiandituVector": "天地图·矢量",
        "basemap.tiandituVectorNote": "国家级矢量底图与中文注记",
        "basemap.tiandituImagery": "天地图·影像",
        "basemap.tiandituImageryNote": "国家级卫星影像与中文注记",
        "basemap.tiandituTerrain": "天地图·地形",
        "basemap.tiandituTerrainNote": "地形晕渲与中文注记",
        "basemap.tiandituKey": "天地图访问 Key",
        "basemap.tiandituKeyMissing": "未配置",
        "basemap.tiandituKeyReady": "已配置 · 本次会话",
        "basemap.tiandituKeyReadyDevice": "已配置 · 本机加密",
        "basemap.tiandituKeyConfiguredHint": "已应用，可直接使用天地图底图。",
        "basemap.tiandituKeyChange": "更换 Key",
        "basemap.tiandituKeyPlaceholder": "输入 tk（不会进入项目状态）",
        "basemap.tiandituKeyApply": "应用",
        "basemap.tiandituKeyHelp": "仅保存在当前浏览器标签页，关闭后自动清除。",
        "basemap.tiandituKeyRememberDevice": "记住此设备（Windows 加密）",
        "basemap.tiandituKeyRemember": "记住此设备",
        "basemap.tiandituKeyForget": "仅本次会话",
        "basemap.tiandituKeyLink": "申请 Key",
        "basemap.tiandituKeyInvalid": "Key 不能为空，且不能包含空格或 URL 分隔符",
        "basemap.addCustom": "自定义底图",
        "basemap.addOverlay": "叠加到图层",
        "basemap.overlayInLayers": "已在图层中",
        "basemap.primaryRole": "主底图",
        "basemap.overlayRole": "地图叠加",
        "basemap.customCount": ":count 个自定义",
        "basemap.editorAdd": "新建底图",
        "basemap.editorEdit": "编辑底图",
        "basemap.editorHint": "保存到本机用户档案",
        "basemap.fieldName": "名称",
        "basemap.fieldType": "服务类型",
        "basemap.fieldProvider": "提供方",
        "basemap.fieldUrl": "服务地址 / 瓦片模板",
        "basemap.urlPlaceholder": "https://.../{z}/{x}/{y}.png",
        "basemap.fieldSubdomains": "子域名",
        "basemap.fieldLayers": "图层名称",
        "basemap.fieldStyles": "样式",
        "basemap.fieldVersion": "WMS 版本",
        "basemap.fieldMatrixSet": "瓦片矩阵集",
        "basemap.fieldMatrixPrefix": "矩阵前缀",
        "basemap.matrixPrefixPlaceholder": "例如 EPSG:3857:",
        "basemap.fieldFormat": "图像格式",
        "basemap.advanced": "版权与缩放层级",
        "basemap.fieldAttribution": "版权说明",
        "basemap.fieldSourceUrl": "官方来源地址",
        "basemap.fieldMinZoom": "最小层级",
        "basemap.fieldMaxZoom": "最大层级",
        "basemap.fieldNativeZoom": "原生最大层级",
        "basemap.setDefaultAfterSave": "保存后设为默认底图",
        "basemap.test": "测试当前视图",
        "basemap.save": "保存底图",
        "basemap.testing": "正在测试当前视图的瓦片…",
        "basemap.pmtilesInspecting": "正在读取 PMTiles 归档索引…",
        "basemap.testPassed": "连接成功，可以保存",
        "basemap.testFailed": "连接失败：:message",
        "basemap.nameRequired": "请填写底图名称",
        "basemap.urlRequired": "请填写服务地址",
        "basemap.urlInvalid": "服务地址必须是有效的 HTTP(S) 地址",
        "basemap.urlCredentialsBlocked": "地址中含有 Key、Token 或账号信息；请改用专用凭据配置，避免明文写入项目状态",
        "basemap.pmtilesUnavailable": "PMTiles 数据引擎没有加载，请刷新页面后重试",
        "basemap.pmtilesInspectFailed": "无法读取 PMTiles 归档索引，请检查跨域与 HTTP Range 支持",
        "basemap.pmtilesRasterOnly": "当前归档是矢量 PMTiles；底图暂时只支持栅格 PMTiles",
        "basemap.pmtilesOutsideView": "当前视图不在 PMTiles 覆盖范围内",
        "basemap.pmtilesZoomOutside": "当前缩放层级不在 PMTiles 原生层级范围内",
        "basemap.pmtilesNoTile": "当前视图范围内没有实际栅格瓦片",
        "basemap.cogLoading": "正在按需加载 MapLibre COG 引擎…",
        "basemap.cogInspecting": "正在读取 COG 元数据与字节范围…",
        "basemap.cogUnavailable": "MapLibre COG 引擎加载失败，请检查本地资源或网络",
        "basemap.cogInspectFailed": "无法读取 COG，请检查跨域、HTTP Range 与文件结构",
        "basemap.cogWebMercatorOnly": "当前轻量 COG 通道要求 EPSG:3857（Web Mercator）",
        "basemap.cogOutsideView": "当前视图不在 COG 覆盖范围内",
        "basemap.cogFit": "已定位到 COG 覆盖范围，正在验证可见影像…",
        "basemap.layersRequired": "WMS/WMTS 需要填写图层名称",
        "basemap.matrixRequired": "WMTS 需要填写瓦片矩阵集",
        "basemap.testFirst": "请先测试连接",
        "basemap.tileTimeout": "等待瓦片超时，请确认当前视图位于服务覆盖范围内",
        "basemap.tileFailed": "当前视图没有加载到有效瓦片",
        "basemap.defaultTitle": "设为默认底图",
        "basemap.defaultCurrent": "默认底图",
        "basemap.edit": "编辑自定义底图",
        "basemap.moveUp": "上移",
        "basemap.moveDown": "下移",
        "basemap.remove": "删除自定义底图",
        "basemap.removeConfirm": "删除自定义底图“:name”？",
        "basemap.customNote": "自定义 :type · :provider",
        "basemap.saved": "自定义底图已保存：:name",
        "basemap.updated": "自定义底图已更新：:name",
        "basemap.removed": "自定义底图已删除：:name",
        "basemap.defaultChanged": "默认底图已设为：:name",
        "log.loaded": "EasyGEE 地图控制台已加载",
        "log.uploadSaved": "上传文件已保存：:file",
        "log.datasetSelected": "已选择数据集 :dataset",
        "log.datasetAdded": "已加入数据集：:dataset",
        "log.datasetBuilding": "正在生成数据集图层：:dataset",
        "log.datasetFailed": "数据集生成失败：:dataset",
        "log.catalogLoaded": "目录已刷新：:count 个数据集",
        "log.catalogOpened": "已打开数据目录：:dataset",
        "log.favoriteAdded": "已收藏数据集：:dataset",
        "log.favoriteRemoved": "已取消收藏数据集：:dataset",
        "log.layerOn": "已显示图层：:layer",
        "log.layerOff": "已隐藏图层：:layer",
        "log.layerRemoved": "已移除图层：:layer",
        "log.layerRefreshed": "已刷新图层：:layer",
        "log.layerReordered": "已调整图层顺序：:layer",
        "log.layerStyled": "已更新图层样式：:layer",
        "log.layerStyleFailed": "图层样式更新失败：:layer",
        "log.layerZoomed": "已缩放到图层：:layer",
        "log.layerExtentUnavailable": "无法获取图层范围：:layer",
        "log.home": "已回到研究区",
        "log.basemap": "底图已切换为 :basemap",
        "log.basemapOverlayAdded": "底图已叠加到图层：:basemap",
        "log.aoiOn": "AOI 绘制模式已开启",
        "log.aoiOff": "AOI 绘制模式已关闭",
        "log.aoiDrawn": "AOI 已更新：:bounds",
        "log.aoiRestored": "已从本地状态恢复 AOI",
        "log.aoiCleared": "AOI 已清除",
        "log.ndviStarted": "已开始 NDVI 提取",
        "log.ndviDone": "NDVI 摘要已生成：均值 :mean",
        "log.ndviFailed": "NDVI 提取失败",
        "log.driveExportStarted": "正在发起 Drive 导出",
        "log.driveExportDone": "Drive 导出任务已加入：:task",
        "log.driveExportFailed": "Drive 导出失败",
        "log.driveOpened": "已打开 Drive：:target",
        "log.taskAdded": "任务已记录：:task",
        "log.measureOn": "测距模式已开启",
        "log.measureOff": "测距模式已关闭",
        "log.measured": "测得距离：:distance",
        "log.measureSummary": "测量统计：共 :count 条，均值 :mean",
        "log.measureUndo": "已撤回测量：:distance",
        "log.measureCleared": "测距标记已清除：:count 条",
        "log.copied": "项目状态已复制",
        "log.clipboardUnavailable": "剪贴板不可用",
        "log.downloaded": "项目 JSON 已下载",
        "log.clicked": "点击坐标 :lat, :lon",
        "log.quotaOpened": "已打开配额详情",
        "log.language": "界面语言已切换为中文"
      },
      en: {
        "tool.data": "Add layers",
        "tool.upload": "Import file",
        "tool.layers": "Layers",
        "tool.layersMeasurementReady": "Layers: measurement added",
        "tool.layersMeasurePrompt": "Layers: measurement results will be added",
        "tool.inspector": "Inspector",
        "tool.drawAoi": "Draw AOI",
        "tool.measure": "Measure distance",
        "tool.measureActive": "Measure on · results are added to Layers",
        "tool.measureUndo": "Undo last step",
        "tool.clearMeasurements": "Clear measurements",
        "tool.basemap": "Basemap",
        "tool.quota": "Quota status",
        "tool.drive": "Google Drive",
        "tool.driveRecent": "Open latest Drive export",
        "tool.driveRoot": "Open Google Drive",
        "tool.home": "Home view",
        "tool.zoomIn": "Zoom in",
        "tool.zoomOut": "Zoom out",
        "tool.lang": "Switch language",
        "tool.close": "Close",
        "upload.title": "Import File",
        "upload.sourceProjection": "Source Projection",
        "upload.projectionHelp": "For .shp files only. ZIP and GPKG auto-detect their projection.",
        "upload.chooseFile": "Choose File",
        "upload.noFile": "No file selected",
        "upload.submit": "Upload",
        "upload.formats": "SHP, ZIP, KML, KMZ, GPX, GeoJSON, CSV, GPKG · Max 50 MB each",
        "upload.ready": ":count file(s) selected",
        "upload.saving": "Saving uploaded file(s)",
        "upload.saved": "Uploaded :count file(s) and added them to layers",
        "upload.savedPartial": "Uploaded :total file(s); :added added to layers",
        "upload.failed": "Upload failed: :message",
        "upload.tooLarge": ":name exceeds 50 MB",
        "upload.empty": "Upload records appear here and sync to agents.",
        "upload.agentReady": "agent-readable",
        "upload.layerAdded": "Added to layers",
        "upload.notRenderable": "Not added to layers: no renderable geometry",
        "upload.remove": "Remove upload record",
        "tool.styleLayer": "Style layer",
        "tool.zoomToLayer": "Zoom to layer",
        "tool.refreshLayer": "Refresh layer",
        "tool.dragLayer": "Drag to reorder",
        "tool.removeLayer": "Remove layer",
        "tool.basemapSource": "View map source",
        "tool.clearAoi": "Clear AOI",
        "panel.data": "Add Layers",
        "panel.dataSubtitle": "Search and add Earth Engine datasets",
        "panel.basemap": "Basemap",
        "source.title": "Basemap source",
        "source.provider": "Provider",
        "source.date": "Imagery date",
        "source.engine": "Data engine",
        "source.performance": "Load timing",
        "source.performanceIdle": "Not sampled yet",
        "source.performanceLoading": "Waiting for first render…",
        "source.performanceSettling": "First :first · settling…",
        "source.performanceReady": "First :first · ready :ready",
        "source.performanceFailed": "Load failed",
        "source.delivery": "Delivery",
        "source.deliveryIdle": "No activation data yet",
        "source.deliveryLoading": ":cache · measuring…",
        "source.cacheCold": "Cold session",
        "source.cacheWarm": "Warm session",
        "source.cacheUnknown": "Session cache unknown",
        "source.renderedBlocks": ":count rendered blocks",
        "source.sourceRequests": ":count source requests",
        "source.networkRestricted": "Network timing restricted",
        "source.nativeZoom": "Native zoom",
        "source.nativeZoomValue": "Z0–Z:zoom",
        "source.attribution": "Attribution",
        "source.open": "Open official source",
        "source.trigger": "View current basemap source",
        "panel.layers": "Layers",
        "panel.inspector": "Inspector",
        "section.layerStack": "Layer Stack",
        "section.operationalLayers": "Data and overlays",
        "section.layerReorderHint": "Drag to reorder",
        "section.primaryBasemap": "Primary basemap",
        "section.primaryBasemapHint": "Pinned to the bottom",
        "placeholder.searchDatasets": "Search layers by name, category, or id",
        "placeholder.filterOptions": "Filter options...",
        "catalog.categories": "Categories (current type)",
        "catalog.all": "All",
        "catalog.typeAll": "All",
        "catalog.typeImageCollection": "Image collections",
        "catalog.typeImage": "Images",
        "catalog.typeTable": "Vectors / tables",
        "catalog.typeOther": "Other",
        "catalog.favorites": "Favorites",
        "catalog.favoriteChip": "Favorites (:count)",
        "catalog.sourceOfficial": "Official",
        "catalog.sourceCommunity": "Community",
        "catalog.sourceCurated": "Curated",
        "card.mapClick": "Map Click",
        "card.activeLayer": "Active Layer",
        "card.legend": "Legend",
        "card.tasks": "Tasks",
        "key.latitude": "Latitude",
        "key.longitude": "Longitude",
        "key.zoom": "Zoom",
        "key.name": "Name",
        "key.dataset": "Dataset",
        "key.type": "Type",
        "key.recipe": "Recipe",
        "key.opacity": "Opacity",
        "label.opacity": "Opacity",
        "label.color": "Color",
        "label.palette": "Palette",
        "layers.empty": "No layers yet. Use Add layers to search the GEE catalog.",
        "layers.emptyOperational": "No data or overlay layers yet.",
        "tasks.empty": "No tasks yet. Agent-started exports and background processing appear here.",
        "task.destination": "Destination",
        "task.folder": "Folder",
        "task.prefix": "File prefix",
        "task.id": "Task ID",
        "task.params": "Params",
        "task.driveSearch": "Drive search",
        "task.createdAt": "Created",
        "layer.none": "No layer selected",
        "measurements.layerName": "Measurements",
        "measurements.layerDataset": "Saved distance markers (:count)",
        "measurements.legend": "Measurement line",
        "measurements.count": "Count",
        "measurements.summary": ":count total, :total",
        "badge.noLayer": "EasyGEE map",
        "badge.basemap": "Basemap: :basemap",
        "badge.basemapSource": "Basemap source: :source",
        "bottom.project": "Quotas",
        "link.quota": "Console",
        "action.copy": "Copy",
        "action.json": "JSON",
        "action.copyTitle": "Copy project state",
        "action.jsonTitle": "Download project JSON",
        "pill.project": "Project: :project",
        "pill.aoi": "AOI: :lat, :lon",
        "pill.layers": ":count layers",
        "pill.layersWithBasemap": ":count layers · 1 basemap",
        "pill.datasets": ":count datasets",
        "pill.datasetMatches": ":shown/:total datasets",
        "pill.datasetLoaded": "Loaded :shown / :matches",
        "pill.datasetLoadedFiltered": "Loaded :shown / :matches matches / :total total",
        "data.loadingMore": "Loading more",
        "data.ready": "Ready to add · :count layers",
        "data.catalogItem": "processable catalog item",
        "data.addHint": "Click + to process nearby and add",
        "data.noResults": "No matching datasets",
        "data.noFavorites": "No favorite datasets yet. Click a star to save one.",
        "data.addTitle": "Add to map",
        "data.favoriteTitle": "Favorite dataset",
        "data.unfavoriteTitle": "Remove favorite",
        "data.openCatalog": "Open catalog page",
        "data.openSample": "Sample code",
        "data.addFromDetail": "Add to map",
        "data.copyId": "Copy ID",
        "data.copyContext": "Copy context",
        "data.contextCopied": "Dataset context copied",
        "data.previewRecipe": "Default preview",
        "data.detailSource": "Source",
        "data.detailType": "Type",
        "data.detailProvider": "Provider",
        "data.detailLicense": "License",
        "data.detailDates": "Date range",
        "data.detailDescription": "Description",
        "data.detailTags": "Tags",
        "data.detailNoDescription": "No detailed description is available. Open the catalog page or sample code to verify fields, license, and usage.",
        "data.detailCopied": "Dataset ID copied",
        "data.attrTime": "Time",
        "data.attrSpan": "Span",
        "data.attrResolution": "Resolution",
        "data.attrType": "Type",
        "data.attrYear": ":count yr",
        "data.attrMonth": ":count mo",
        "data.processing": "Processing and generating layer",
        "data.generated": "Visualized",
        "data.failed": "Generation failed",
        "state.idle": "idle",
        "state.clicked": "clicked",
        "mode.datasetAdded": "Added :count layers",
        "mode.datasetBuilding": "Generating :dataset",
        "mode.datasetNeedsBuild": "Use the local preview service to generate the layer",
        "mode.datasetFailed": "Generation failed: :message",
        "mode.favoriteAdded": "Favorited :dataset",
        "mode.favoriteRemoved": "Removed favorite :dataset",
        "mode.quotaReady": "Quota: :summary",
        "mode.aoiStart": "AOI: choose first corner",
        "mode.aoiCorner": "AOI: choose opposite corner",
        "mode.aoiDone": "AOI updated",
        "mode.aoiOff": "AOI draw off",
        "mode.aoiTooSmall": "AOI too small",
        "mode.polygonStart": "Polygon AOI: add vertices, double-click or Enter to finish",
        "mode.polygonVertex": "Polygon AOI: :count vertices",
        "mode.polygonTooSmall": "Polygon AOI needs at least 3 vertices",
        "mode.ndviBuilding": "Extracting NDVI for current AOI",
        "mode.ndviDone": "NDVI mean :mean from :count pixels",
        "mode.ndviNoAoi": "Draw an AOI before extracting NDVI",
        "mode.ndviFailed": "NDVI failed: :message",
        "mode.driveExportBuilding": "Starting Drive export",
        "mode.driveExportDone": "Drive export task created: :task",
        "mode.driveExportFailed": "Drive export failed: :message",
        "mode.styleBuilding": "Updating layer style: :layer",
        "mode.styleApplied": "Layer style updated: :layer",
        "mode.styleFailed": "Style update failed: :message",
        "mode.layerZooming": "Zooming to layer: :layer",
        "mode.layerZoomed": "Zoomed to layer: :layer",
        "mode.layerReordered": "Layer order updated",
        "mode.layerExtentUnavailable": "Layer extent unavailable: :layer",
        "quota.project": "Project: :project",
        "quota.tier": "Usage tier: :tier",
        "quota.tierInferred": "Usage tier: :tier",
        "quota.tierUnknown": "Usage tier: pending",
        "quota.items": "Quota items",
        "quota.summaryLiveUsage": "Live usage available",
        "quota.summaryLiveLimit": "Live limits available; usage unavailable",
        "quota.summaryDefault": "Default limits; remaining unknown",
        "quota.summaryEmpty": "Quota data unavailable",
        "quota.issueCloudLogin": "Google Cloud CLI login required",
        "quota.issueCloudQuotasApi": "Cloud Quotas API must be enabled",
        "quota.issueQuotaPermission": "Cloud Quotas permission missing",
        "quota.issueMonitoringPermission": "Monitoring usage permission missing",
        "quota.issueQuotaNetwork": "gcloud quota component/network issue",
        "quota.issueLiveUnavailable": "Live quota unavailable",
        "quota.total": "Total",
        "quota.used": "Used",
        "quota.remaining": "Remaining",
        "quota.measured": "Measured",
        "quota.alerts": "Alerts",
        "quota.noAlerts": "0 items",
        "quota.alertCount": ":count items",
        "quota.measuredOfTotal": ":count/:total",
        "quota.maxUsed": "Max used :percent",
        "quota.usedOfTotal": ":used/:total (:percent)",
        "quota.usedUnlimited": ":used/unlimited",
        "quota.totalOnly": "Total :total",
        "quota.remainingValue": "Remaining :remaining",
        "quota.remainingUnlimited": "Remaining unlimited",
        "quota.unlimited": "Unlimited",
        "quota.usageMissing": "Usage unavailable",
        "quota.usageUnavailable": "Usage not provided",
        "quota.noUsageYet": "No usage yet",
        "quota.limitOnlyState": "Limit only",
        "quota.unlimitedState": "Unlimited",
        "quota.noUsageState": "No usage",
        "quota.okState": "Healthy",
        "quota.warnState": "Near limit",
        "quota.notAvailable": "N/A",
        "quota.unknown": "Unknown",
        "quota.usageRequired": "Cloud Monitoring usage permission required",
        "mode.basemap": "Basemap: :basemap",
        "mode.tiandituKeyRequired": "Configure a Tianditu key in the basemap panel first",
        "mode.tiandituKeySaved": "Tianditu key applied to this browser tab",
        "mode.tiandituKeyRemembered": "Tianditu key saved locally with Windows encryption",
        "mode.tiandituKeySessionOnly": "Local copy removed; this browser tab can still use the key",
        "mode.tiandituKeyRememberFailed": "This tab can keep using the key, but encrypted local storage failed",
        "mode.basemapOverlayAdded": "Added as overlay: :basemap",
        "mode.measureStart": "Measure: click two points",
        "mode.measureOff": "Measure off",
        "mode.measureEndpoint": "Measure: choose endpoint",
        "mode.distance": "Distance: :distance",
        "mode.measureSaved": "Measurement added to Layers: :distance (:count total, mean :mean)",
        "mode.measureUndoDraft": "Undid the last measurement point",
        "mode.measureUndoSaved": "Undid the last measurement: :distance",
        "mode.measureUndoEmpty": "No measurement to undo",
        "mode.measureCleared": "Measurement markers cleared",
        "basemap.osm": "OpenStreetMap",
        "basemap.osmNote": "Roads and labels",
        "basemap.light": "Light",
        "basemap.lightNote": "Clean overlay base",
        "basemap.dark": "Dark",
        "basemap.darkNote": "High contrast",
        "basemap.voyager": "Voyager",
        "basemap.voyagerNote": "Balanced roads and places",
        "basemap.topo": "Topo",
        "basemap.topoNote": "Terrain and contours with zoom fallback",
        "basemap.topoCoverage": "Esri World Topographic Map · global native coverage through z13",
        "basemap.imagery": "Imagery",
        "basemap.imageryNote": "Esri global imagery",
        "basemap.esriClarity": "Esri Clarity Imagery",
        "basemap.esriClarityNote": "Clarity-first archive imagery",
        "basemap.tiandituVector": "Tianditu Vector",
        "basemap.tiandituVectorNote": "National vector map with Chinese labels",
        "basemap.tiandituImagery": "Tianditu Imagery",
        "basemap.tiandituImageryNote": "National satellite imagery with Chinese labels",
        "basemap.tiandituTerrain": "Tianditu Terrain",
        "basemap.tiandituTerrainNote": "Terrain shading with Chinese labels",
        "basemap.tiandituKey": "Tianditu access key",
        "basemap.tiandituKeyMissing": "Not configured",
        "basemap.tiandituKeyReady": "Configured · this session",
        "basemap.tiandituKeyReadyDevice": "Configured · encrypted locally",
        "basemap.tiandituKeyConfiguredHint": "Ready for Tianditu basemaps.",
        "basemap.tiandituKeyChange": "Change key",
        "basemap.tiandituKeyPlaceholder": "Enter tk (excluded from project state)",
        "basemap.tiandituKeyApply": "Apply",
        "basemap.tiandituKeyHelp": "Stored only for this browser tab and cleared when it closes.",
        "basemap.tiandituKeyRememberDevice": "Remember on this device (Windows encrypted)",
        "basemap.tiandituKeyRemember": "Remember device",
        "basemap.tiandituKeyForget": "This session only",
        "basemap.tiandituKeyLink": "Get a key",
        "basemap.tiandituKeyInvalid": "The key cannot be empty or contain spaces or URL delimiters",
        "basemap.addCustom": "Custom basemap",
        "basemap.addOverlay": "Add as overlay",
        "basemap.overlayInLayers": "Already in layers",
        "basemap.primaryRole": "Primary basemap",
        "basemap.overlayRole": "Map overlay",
        "basemap.customCount": ":count custom",
        "basemap.editorAdd": "New basemap",
        "basemap.editorEdit": "Edit basemap",
        "basemap.editorHint": "Saved in the local user profile",
        "basemap.fieldName": "Name",
        "basemap.fieldType": "Service type",
        "basemap.fieldProvider": "Provider",
        "basemap.fieldUrl": "Service URL / tile template",
        "basemap.urlPlaceholder": "https://.../{z}/{x}/{y}.png",
        "basemap.fieldSubdomains": "Subdomains",
        "basemap.fieldLayers": "Layer name",
        "basemap.fieldStyles": "Style",
        "basemap.fieldVersion": "WMS version",
        "basemap.fieldMatrixSet": "Tile matrix set",
        "basemap.fieldMatrixPrefix": "Matrix prefix",
        "basemap.matrixPrefixPlaceholder": "For example EPSG:3857:",
        "basemap.fieldFormat": "Image format",
        "basemap.advanced": "Attribution and zoom levels",
        "basemap.fieldAttribution": "Attribution",
        "basemap.fieldSourceUrl": "Official source URL",
        "basemap.fieldMinZoom": "Min zoom",
        "basemap.fieldMaxZoom": "Max zoom",
        "basemap.fieldNativeZoom": "Native max",
        "basemap.setDefaultAfterSave": "Set as default after saving",
        "basemap.test": "Test current view",
        "basemap.save": "Save basemap",
        "basemap.testing": "Testing tiles for the current view…",
        "basemap.pmtilesInspecting": "Reading the PMTiles archive index…",
        "basemap.testPassed": "Connection passed; ready to save",
        "basemap.testFailed": "Connection failed: :message",
        "basemap.nameRequired": "Enter a basemap name",
        "basemap.urlRequired": "Enter a service URL",
        "basemap.urlInvalid": "The service URL must be a valid HTTP(S) address",
        "basemap.urlCredentialsBlocked": "The URL contains a key, token, or account credentials; use a dedicated credential field to keep secrets out of project state",
        "basemap.pmtilesUnavailable": "The PMTiles engine did not load; reload the page and try again",
        "basemap.pmtilesInspectFailed": "Could not read the PMTiles archive index; check CORS and HTTP Range support",
        "basemap.pmtilesRasterOnly": "This is a vector PMTiles archive; basemaps currently support raster PMTiles only",
        "basemap.pmtilesOutsideView": "The current view is outside the PMTiles coverage",
        "basemap.pmtilesZoomOutside": "The current zoom is outside the native PMTiles zoom range",
        "basemap.pmtilesNoTile": "No raster tile exists inside the current view",
        "basemap.cogLoading": "Loading the MapLibre COG engine on demand…",
        "basemap.cogInspecting": "Reading COG metadata and byte ranges…",
        "basemap.cogUnavailable": "The MapLibre COG engine failed to load; check local assets or network access",
        "basemap.cogInspectFailed": "Could not read the COG; check CORS, HTTP Range, and file structure",
        "basemap.cogWebMercatorOnly": "This lightweight COG path requires EPSG:3857 (Web Mercator)",
        "basemap.cogOutsideView": "The current view is outside the COG coverage",
        "basemap.cogFit": "Moved to the COG extent; validating visible imagery…",
        "basemap.layersRequired": "WMS/WMTS requires a layer name",
        "basemap.matrixRequired": "WMTS requires a tile matrix set",
        "basemap.testFirst": "Test the connection first",
        "basemap.tileTimeout": "Tile test timed out; check whether the current view is inside the service coverage",
        "basemap.tileFailed": "No valid tile loaded for the current view",
        "basemap.defaultTitle": "Set as default basemap",
        "basemap.defaultCurrent": "Default basemap",
        "basemap.edit": "Edit custom basemap",
        "basemap.moveUp": "Move up",
        "basemap.moveDown": "Move down",
        "basemap.remove": "Delete custom basemap",
        "basemap.removeConfirm": "Delete custom basemap “:name”?",
        "basemap.customNote": "Custom :type · :provider",
        "basemap.saved": "Custom basemap saved: :name",
        "basemap.updated": "Custom basemap updated: :name",
        "basemap.removed": "Custom basemap deleted: :name",
        "basemap.defaultChanged": "Default basemap set to: :name",
        "log.loaded": "EasyGEE Map Console loaded",
        "log.uploadSaved": "Upload saved: :file",
        "log.datasetSelected": "Selected dataset :dataset",
        "log.datasetAdded": "Added dataset: :dataset",
        "log.datasetBuilding": "Generating dataset layer: :dataset",
        "log.datasetFailed": "Dataset generation failed: :dataset",
        "log.catalogLoaded": "Catalog refreshed: :count datasets",
        "log.catalogOpened": "Opened catalog page: :dataset",
        "log.favoriteAdded": "Favorited dataset: :dataset",
        "log.favoriteRemoved": "Removed favorite dataset: :dataset",
        "log.layerOn": "Layer on: :layer",
        "log.layerOff": "Layer off: :layer",
        "log.layerRemoved": "Removed layer: :layer",
        "log.layerRefreshed": "Refreshed layer: :layer",
        "log.layerReordered": "Reordered layer: :layer",
        "log.layerStyled": "Updated layer style: :layer",
        "log.layerStyleFailed": "Layer style update failed: :layer",
        "log.layerZoomed": "Zoomed to layer: :layer",
        "log.layerExtentUnavailable": "Layer extent unavailable: :layer",
        "log.home": "Zoomed to AOI",
        "log.basemap": "Basemap switched to :basemap",
        "log.basemapOverlayAdded": "Basemap added as overlay: :basemap",
        "log.aoiOn": "AOI draw mode on",
        "log.aoiOff": "AOI draw mode off",
        "log.aoiDrawn": "AOI updated: :bounds",
        "log.aoiRestored": "AOI restored from local state",
        "log.aoiCleared": "AOI cleared",
        "log.ndviStarted": "NDVI extraction started",
        "log.ndviDone": "NDVI summary ready: mean :mean",
        "log.ndviFailed": "NDVI extraction failed",
        "log.driveExportStarted": "Starting Drive export",
        "log.driveExportDone": "Drive export task added: :task",
        "log.driveExportFailed": "Drive export failed",
        "log.driveOpened": "Opened Drive: :target",
        "log.taskAdded": "Task recorded: :task",
        "log.measureOn": "Measure mode on",
        "log.measureOff": "Measure mode off",
        "log.measured": "Measured distance: :distance",
        "log.measureSummary": "Measurements: :count total, mean :mean",
        "log.measureUndo": "Measurement undone: :distance",
        "log.measureCleared": "Measurement markers cleared: :count",
        "log.copied": "Project state copied",
        "log.clipboardUnavailable": "Clipboard write unavailable",
        "log.downloaded": "Project JSON downloaded",
        "log.clicked": "Clicked :lat, :lon",
        "log.quotaOpened": "Quota details opened",
        "log.language": "Interface language switched to English"
      }
    };
    let activeLayerId = STATE.layers.find(layer => layer.shown)?.id || STATE.layers[0]?.id || null;
    let draggedLayerId = null;
    let operationalLayerOrder = [...STATE.layerOrder];
    let operationalMapOrderDirty = true;
    let activeDatasetId = null;
    let activeBadgeTimer = null;
    let basemapSourceOpen = false;
    let basemapSourceDetailId = null;
    let currentLang = localStorage.getItem('easygee-lang') || 'zh';
    const TIANDITU_TOKEN_STORAGE_KEY = 'easygee-tianditu-tk';
    let tiandituToken = readTiandituToken();
    let tiandituTokenRemembered = false;
    let tiandituCredentialSupported = false;
    let tiandituKeyEditing = false;
    let restoredProfileView = null;
    let restoredProfileActiveLayerId = null;
    let pendingProfileLayers = [];
    let clickStateKey = 'state.idle';
    let currentModeKey = null;
    let quotaFocus = false;
    let catalogTypeFilter = 'all';
    let catalogCategoryFilter = 'all';
    let catalogFavoriteFilter = false;
    let catalogCategoryQuery = '';
    let catalogListItems = [];
    let catalogRenderedCount = 0;
    const CATALOG_RENDER_BATCH = 120;
    const FAVORITES_STORAGE_KEY = 'easygee-dataset-favorites';
    const PROJECT_STORAGE_SOURCE = String((STATE.project && STATE.project !== 'YOUR_EE_PROJECT') ? STATE.project : (STATE.title || 'default'));
    const PROJECT_STORAGE_ID = PROJECT_STORAGE_SOURCE.replace(/[^a-z0-9_-]+/gi, '-').slice(0, 80) || 'default';
    const LEGACY_PROJECT_STORAGE_ID = String(STATE.project || STATE.title || 'default').replace(/[^a-z0-9_-]+/gi, '-').slice(0, 80) || 'default';
    const AOI_STORAGE_KEYS = [...new Set([`easygee-aoi:${PROJECT_STORAGE_ID}`, `easygee-aoi:${LEGACY_PROJECT_STORAGE_ID}`])];
    const MEASUREMENTS_STORAGE_KEYS = [...new Set([`easygee-measurements:${PROJECT_STORAGE_ID}`, `easygee-measurements:${LEGACY_PROJECT_STORAGE_ID}`])];
    const TASKS_STORAGE_KEYS = [...new Set([`easygee-tasks:${PROJECT_STORAGE_ID}`, `easygee-tasks:${LEGACY_PROJECT_STORAGE_ID}`])];
    const UPLOADS_STORAGE_KEYS = [...new Set([`easygee-uploads:${PROJECT_STORAGE_ID}`, `easygee-uploads:${LEGACY_PROJECT_STORAGE_ID}`])];
    const UPLOAD_CAPABILITIES = {
      endpoint: '/api/uploads',
      maxBytes: 50 * 1024 * 1024,
      acceptedExtensions: ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.zip', '.kml', '.kmz', '.gpx', '.geojson', '.json', '.csv', '.gpkg'],
      formats: ['SHP', 'ZIP', 'KML', 'KMZ', 'GPX', 'GeoJSON', 'CSV', 'GPKG'],
      agentVisible: true,
      stateKey: 'uploads',
    };
    const AGENT_PROTOCOL_VERSION = 5;
    const SESSION_SYNC_INTERVAL_MS = 1200;
    const SESSION_ACTION_POLL_MS = 900;
    const ACTION_SET_AOI_STYLE = 'setAoiStyle';
    const ACTION_UPDATE_LAYER_STYLE = 'updateLayerStyle';
    const AOI_LAYER_ID = '__easygee_aoi__';
    const MEASUREMENTS_LAYER_ID = '__easygee_measurements__';
    const PRIMARY_BASEMAP_LAYER_ID = '__easygee_primary_basemap__';
    const PRIMARY_BASEMAP_PANE = 'easygeePrimaryBasemapPane';
    const DEFAULT_AOI_STYLE = { color: '#d23b3b', fillColor: '#d23b3b', opacity: 1, fillOpacity: 0.08, weight: 2, shown: true };
    const DEFAULT_MEASUREMENTS_STYLE = { color: '#16734d', opacity: 1, weight: 3, shown: true };
    const VIS_PRESETS = {
      ndvi: [
        { id: 'default', label: 'NDVI purple-green', visParams: { min: 0, max: 0.8, palette: ['#2c105c', '#4856a5', '#31a354', '#addd8e', '#f7fcb9'] }, legend: [['#2c105c', 'Low'], ['#31a354', 'Medium'], ['#f7fcb9', 'High']] },
        { id: 'natural-green', label: 'NDVI brown-green', visParams: { min: -0.2, max: 0.9, palette: ['#8c510a', '#d8b365', '#f6e8c3', '#5ab469', '#006837'] }, legend: [['#8c510a', 'Bare/low'], ['#f6e8c3', 'Moderate'], ['#006837', 'High']] },
        { id: 'soft-green', label: 'NDVI soft green', visParams: { min: 0, max: 0.8, palette: ['#f7fcf5', '#c7e9c0', '#74c476', '#238b45', '#00441b'] }, legend: [['#f7fcf5', 'Low'], ['#74c476', 'Medium'], ['#00441b', 'High']] },
        { id: 'contrast', label: 'NDVI high contrast', visParams: { min: -0.2, max: 1, palette: ['#440154', '#31688e', '#35b779', '#fde725'] }, legend: [['#440154', 'Low'], ['#35b779', 'Medium'], ['#fde725', 'High']] },
      ],
      water: [
        { id: 'default', label: 'Water blue', visParams: { min: 0, max: 100, palette: ['#f7fbff', '#6baed6', '#08306b'] }, legend: [['#f7fbff', 'Rare'], ['#6baed6', 'Seasonal'], ['#08306b', 'Persistent']] },
        { id: 'deep-blue', label: 'Water deep blue', visParams: { min: 0, max: 100, palette: ['#f0f9ff', '#38bdf8', '#075985'] }, legend: [['#f0f9ff', 'Rare'], ['#38bdf8', 'Seasonal'], ['#075985', 'Persistent']] },
        { id: 'cyan', label: 'Water cyan', visParams: { min: 0, max: 100, palette: ['#ecfeff', '#67e8f9', '#0e7490'] }, legend: [['#ecfeff', 'Rare'], ['#67e8f9', 'Seasonal'], ['#0e7490', 'Persistent']] },
        { id: 'single-blue', label: 'Water mask blue', visParams: { min: 1, max: 100, palette: ['#bfdbfe', '#1d4ed8'] }, legend: [['#bfdbfe', 'Low occurrence'], ['#1d4ed8', 'High occurrence']] },
      ],
      temperature: [
        { id: 'default', label: 'Temperature blue-red', visParams: { min: 0, max: 45, palette: ['#313695', '#74add1', '#ffffbf', '#f46d43', '#a50026'] }, legend: [['#313695', 'Cool'], ['#ffffbf', 'Moderate'], ['#a50026', 'Hot']] },
        { id: 'fire', label: 'Temperature fire', visParams: { min: 0, max: 45, palette: ['#081d58', '#225ea8', '#ffffb2', '#fd8d3c', '#bd0026'] }, legend: [['#081d58', 'Cool'], ['#ffffb2', 'Moderate'], ['#bd0026', 'Hot']] },
      ],
      terrain: [
        { id: 'default', label: 'Terrain green-brown', visParams: { min: 0, max: 1000, palette: ['#0f3b2e', '#3f7d3f', '#c9b96d', '#a2673f', '#f4f1e8'] }, legend: [['#0f3b2e', 'Low'], ['#c9b96d', 'Mid'], ['#f4f1e8', 'High']] },
        { id: 'gray', label: 'Terrain gray', visParams: { min: 0, max: 1000, palette: ['#111827', '#6b7280', '#f9fafb'] }, legend: [['#111827', 'Low'], ['#6b7280', 'Mid'], ['#f9fafb', 'High']] },
      ],
      nightlights: [
        { id: 'default', label: 'Night lights amber', visParams: { min: 0, max: 60, palette: ['#03071e', '#370617', '#f48c06', '#ffba08'] }, legend: [['#03071e', 'Low'], ['#f48c06', 'Medium'], ['#ffba08', 'High']] },
        { id: 'purple-gold', label: 'Night lights purple-gold', visParams: { min: 0, max: 60, palette: ['#1e1b4b', '#7e22ce', '#facc15'] }, legend: [['#1e1b4b', 'Low'], ['#7e22ce', 'Medium'], ['#facc15', 'High']] },
      ],
      population: [
        { id: 'default', label: 'Population red', visParams: { min: 0, max: 100, palette: ['#fff7ec', '#fdbb84', '#e34a33', '#7f0000'] }, legend: [['#fff7ec', 'Sparse'], ['#e34a33', 'Dense']] },
        { id: 'magenta', label: 'Population magenta', visParams: { min: 0, max: 100, palette: ['#fdf2f8', '#f472b6', '#831843'] }, legend: [['#fdf2f8', 'Sparse'], ['#831843', 'Dense']] },
      ],
      raster: [
        { id: 'default', label: 'Raster teal', visParams: { min: 0, max: 1, palette: ['#132b43', '#2c7fb8', '#7fcdbb', '#ffffcc'] }, legend: [['#132b43', 'Low'], ['#7fcdbb', 'Mid'], ['#ffffcc', 'High']] },
        { id: 'gray', label: 'Raster gray', visParams: { min: 0, max: 1, palette: ['#111827', '#9ca3af', '#f9fafb'] }, legend: [['#111827', 'Low'], ['#9ca3af', 'Mid'], ['#f9fafb', 'High']] },
      ],
      vector: [
        { id: 'default', label: 'Vector green', visParams: {}, legend: [['#16734d', 'Features']] },
      ],
      rgb: [
        { id: 'default', label: 'RGB default', visParams: {}, legend: [['#6f9fcf', 'RGB composite']] },
      ],
    };
    let lastSessionStateText = '';
    let lastSessionActionId = 0;
    let sessionSyncBusy = false;
    let sessionActionBusy = false;
    const pendingDatasetIds = new Set();
    const failedDatasetIds = new Map();
    const DATASET_QUERY_ALIASES = {
      '人口': 'population people worldpop ghsl ciesin',
      '建筑': 'building buildings footprint open-buildings built',
      '建筑物': 'building buildings footprint open-buildings built',
      '降水': 'precipitation rainfall rain chirps era5 gpm',
      '雨量': 'precipitation rainfall rain chirps gpm',
      '温度': 'temperature lst land surface temperature era5 modis',
      '地表温度': 'land surface temperature lst modis landsat',
      '夜光': 'nighttime lights viirs dnb radiance',
      '土地覆盖': 'land cover landcover dynamic world worldcover esa',
      '地类': 'land cover landcover dynamic world worldcover esa',
      '水体': 'water surface water occurrence jrc gsw',
      '地表水': 'water surface water occurrence jrc gsw',
      '洪水': 'flood water sentinel sar s1 inundation',
      '植被': 'vegetation ndvi evi modis sentinel landsat',
      '农作物': 'crop agriculture cropland aafc usda',
      '农业': 'agriculture crop cropland',
      '高程': 'elevation dem terrain srtm copernicus',
      '地形': 'terrain elevation dem srtm copernicus',
      '土壤': 'soil smap soilgrids moisture',
      '火灾': 'fire burned wildfire modis viirs',
      '空气': 'air quality atmosphere no2 aerosol',
      '气候': 'climate era5 temperature precipitation wind',
      '哨兵': 'sentinel copernicus s1 s2 s3 s5p',
      '雷达': 'sar radar sentinel-1 s1',
      '光学': 'optical sentinel-2 landsat modis',
    };

    function $(id) { return document.getElementById(id); }
    function t(key, vars = {}) {
      const text = (I18N[currentLang] && I18N[currentLang][key]) || I18N.en[key] || key;
      return Object.entries(vars).reduce((value, [name, replacement]) => value.split(`:${name}`).join(String(replacement)), text);
    }
    function log(message) {
      const stamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      logLines.unshift(`${stamp}  ${message}`);
      const target = $('session-log');
      if (target) {
        target.innerHTML = logLines.slice(0, 8).map(line => `<div class="log-line">${escapeHtml(line)}</div>`).join('');
      }
    }
    function logMsg(key, vars = {}) { log(t(key, vars)); }
    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
    }
    function fmt(num, digits = 5) { return Number(num).toFixed(digits); }
    function normalizeFavoriteDatasetIds(value) {
      if (!Array.isArray(value)) return [];
      return [...new Set(value.map(item => String(item || '').trim()).filter(Boolean))].sort();
    }
    function loadFavoriteDatasetIds() {
      try {
        const parsed = JSON.parse(localStorage.getItem(FAVORITES_STORAGE_KEY) || '[]');
        return new Set(normalizeFavoriteDatasetIds(parsed));
      } catch {
        return new Set();
      }
    }
    let favoriteDatasetIds = loadFavoriteDatasetIds();
    STATE.aoiStyle = { ...DEFAULT_AOI_STYLE, ...(STATE.aoiStyle || {}) };
    STATE.aoiShown = STATE.aoiShown !== false;
    STATE.measurementsShown = STATE.measurementsShown !== false;
    STATE.measurementsOpacity = normalizeMeasurementsOpacity(STATE.measurementsOpacity);
    let visualPreferences = (STATE.visualPreferences && typeof STATE.visualPreferences === 'object') ? { ...STATE.visualPreferences } : {};
    function saveFavoriteDatasetIds() {
      localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify([...favoriteDatasetIds].sort()));
    }
    function isFavoriteDataset(datasetId) {
      return favoriteDatasetIds.has(String(datasetId || ''));
    }
    function favoriteCatalogItems(items = STATE.catalog) {
      const catalog = Array.isArray(items) ? items : [];
      return catalog.filter(item => isFavoriteDataset(item.id));
    }
    function toggleFavoriteDataset(datasetId) {
      const id = String(datasetId || '');
      if (!id) return;
      const added = !favoriteDatasetIds.has(id);
      if (added) favoriteDatasetIds.add(id);
      else favoriteDatasetIds.delete(id);
      saveFavoriteDatasetIds();
      renderDatasets(filteredCatalog());
      showModeKey(added ? 'mode.favoriteAdded' : 'mode.favoriteRemoved', { dataset: id });
      logMsg(added ? 'log.favoriteAdded' : 'log.favoriteRemoved', { dataset: id });
      syncSessionState('favorites');
    }
    function normalizeBounds(value) {
      if (!Array.isArray(value) || value.length !== 2 || !Array.isArray(value[0]) || !Array.isArray(value[1])) return null;
      const south = Number(value[0][0]);
      const west = Number(value[0][1]);
      const north = Number(value[1][0]);
      const east = Number(value[1][1]);
      if (![south, west, north, east].every(Number.isFinite)) return null;
      if (south >= north || west >= east) return null;
      if (south < -90 || north > 90 || west < -180 || east > 180) return null;
      return [[south, west], [north, east]];
    }
    function aoiFromBounds(bounds) {
      const normalized = normalizeBounds(bounds);
      if (!normalized) return null;
      const [[south, west], [north, east]] = normalized;
      return {
        type: 'rectangle',
        bounds: normalized,
        coordinates: [[south, west], [south, east], [north, east], [north, west]],
        coordinateOrder: 'latlng',
      };
    }
    function normalizeLatLngPair(pair) {
      if (!Array.isArray(pair) || pair.length < 2) return null;
      const lat = Number(pair[0]);
      const lng = Number(pair[1]);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
      if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
      return [lat, lng];
    }
    function normalizeLonLatPair(pair) {
      if (!Array.isArray(pair) || pair.length < 2) return null;
      const lng = Number(pair[0]);
      const lat = Number(pair[1]);
      return normalizeLatLngPair([lat, lng]);
    }
    function boundsFromAoiCoordinates(coordinates) {
      if (!Array.isArray(coordinates) || coordinates.length < 3) return null;
      const lats = coordinates.map(point => point[0]);
      const lngs = coordinates.map(point => point[1]);
      const south = Math.min(...lats);
      const north = Math.max(...lats);
      const west = Math.min(...lngs);
      const east = Math.max(...lngs);
      return normalizeBounds([[south, west], [north, east]]);
    }
    function normalizeAoiCoordinates(raw, order = 'latlng') {
      if (!Array.isArray(raw) || !raw.length) return null;
      let points = raw;
      let pointOrder = order;
      if (Array.isArray(raw[0]) && raw[0].length && Array.isArray(raw[0][0])) {
        points = raw[0];
        pointOrder = 'lonlat';
      }
      const normalized = points.map(point => pointOrder === 'lonlat' ? normalizeLonLatPair(point) : normalizeLatLngPair(point)).filter(Boolean);
      const deduped = [];
      normalized.forEach(point => {
        const previous = deduped[deduped.length - 1];
        if (!previous || Math.abs(previous[0] - point[0]) > 1e-12 || Math.abs(previous[1] - point[1]) > 1e-12) {
          deduped.push(point);
        }
      });
      if (deduped.length > 3) {
        const first = deduped[0];
        const last = deduped[deduped.length - 1];
        if (Math.abs(first[0] - last[0]) < 1e-12 && Math.abs(first[1] - last[1]) < 1e-12) deduped.pop();
      }
      return deduped.length >= 3 && boundsFromAoiCoordinates(deduped) ? deduped : null;
    }
    function normalizeAoi(value) {
      if (!value || typeof value !== 'object') return null;
      if (String(value.type || '').toLowerCase() === 'feature' && value.geometry) return normalizeAoi(value.geometry);
      const type = String(value.type || '').toLowerCase();
      if (type === 'polygon' || type === 'multipolygon') {
        const coordinates = normalizeAoiCoordinates(
          value.coordinates || value.latLngs || value.points,
          String(value.coordinateOrder || '').toLowerCase() === 'lonlat' ? 'lonlat' : 'latlng'
        );
        const bounds = coordinates ? boundsFromAoiCoordinates(coordinates) : null;
        if (!coordinates || !bounds) return null;
        return { type: 'polygon', bounds, coordinates, coordinateOrder: 'latlng' };
      }
      return aoiFromBounds(value.bounds || value.bbox || value);
    }
    function cloneAoi(aoi) {
      return aoi ? JSON.parse(JSON.stringify(aoi)) : null;
    }
    function isHexColor(value) {
      return /^#[0-9a-f]{6}$/i.test(String(value || '').trim());
    }
    function normalizeAoiStyle(value = {}) {
      const source = value && typeof value === 'object' ? value : {};
      const color = isHexColor(source.color) ? source.color : DEFAULT_AOI_STYLE.color;
      const fillColor = isHexColor(source.fillColor) ? source.fillColor : color;
      const opacity = Number.isFinite(Number(source.opacity)) ? Math.max(0, Math.min(1, Number(source.opacity))) : DEFAULT_AOI_STYLE.opacity;
      const fillOpacity = Number.isFinite(Number(source.fillOpacity)) ? Math.max(0, Math.min(0.6, Number(source.fillOpacity))) : DEFAULT_AOI_STYLE.fillOpacity;
      const weight = Number.isFinite(Number(source.weight)) ? Math.max(1, Math.min(6, Number(source.weight))) : DEFAULT_AOI_STYLE.weight;
      return { color, fillColor, opacity, fillOpacity, weight, shown: source.shown !== false };
    }
    function normalizeMeasurementsOpacity(value) {
      const opacity = Number(value);
      return Number.isFinite(opacity) ? Math.max(0, Math.min(1, opacity)) : DEFAULT_MEASUREMENTS_STYLE.opacity;
    }
    function layerStyleProfile(layer) {
      if (!layer) return 'raster';
      if (layer.id === AOI_LAYER_ID || layer.type === 'aoi') return 'aoi';
      if (layer.id === MEASUREMENTS_LAYER_ID || layer.type === 'measurements') return 'measurements';
      if (Array.isArray(layer.visParams?.bands) && layer.visParams.bands.length > 1) return 'rgb';
      if (layer.styleProfile) return layer.styleProfile;
      const text = `${layer.dataset || ''} ${layer.type || ''} ${layer.method || ''} ${layer.name || ''}`.toLowerCase();
      if (text.includes('ndvi') || text.includes('vegetation')) return 'ndvi';
      if (text.includes('water') || text.includes('jrc') || text.includes('gsw')) return 'water';
      if (text.includes('lst') || text.includes('temperature') || text.includes('thermal')) return 'temperature';
      if (text.includes('dem') || text.includes('elevation') || text.includes('terrain')) return 'terrain';
      if (text.includes('viirs') || text.includes('night')) return 'nightlights';
      if (text.includes('population') || text.includes('worldpop') || text.includes('ghsl')) return 'population';
      if (String(layer.type || '').includes('categorical')) return 'categorical';
      if (String(layer.type || '').includes('vector')) return 'vector';
      return 'raster';
    }
    function stylePresetOptions(layer) {
      const profile = layerStyleProfile(layer);
      return VIS_PRESETS[profile] || VIS_PRESETS.raster;
    }
    function stylePresetForLayer(layer, presetId) {
      const options = stylePresetOptions(layer);
      return options.find(item => item.id === presetId) || options[0];
    }
    function isLocalVectorLayer(meta) {
      if (!meta || typeof meta !== 'object') return false;
      if (meta.recipe?.kind === 'localVectorOverlay') return true;
      const candidates = [
        meta.previewUrl,
        meta.sourceUrl,
        meta.recipe?.previewUrl,
        meta.recipe?.sourceUrl,
        meta.recipe?.url,
        meta.recipe?.path,
        meta.summary?.geojson,
        meta.summary?.path,
      ];
      return candidates.some(value => typeof value === 'string' && value.trim());
    }
    function isUploadPlaceholderLayer(meta) {
      return meta?.recipe?.kind === 'localUploadPlaceholder' || meta?.type === 'local-upload';
    }
    function appendCacheBust(url, token) {
      if (!url || !token) return url;
      const separator = String(url).includes('?') ? '&' : '?';
      return `${url}${separator}_easygeeRefresh=${encodeURIComponent(token)}`;
    }
    function localVectorSourceUrl(meta) {
      const raw = [
        meta?.previewUrl,
        meta?.sourceUrl,
        meta?.recipe?.previewUrl,
        meta?.recipe?.sourceUrl,
        meta?.recipe?.url,
        meta?.recipe?.path,
        meta?.summary?.geojson,
        meta?.summary?.path,
      ].find(value => typeof value === 'string' && value.trim());
      if (!raw) return '';
      const text = String(raw).trim();
      const refreshToken = layerRefreshTokens.get(meta?.id);
      const withRefresh = url => appendCacheBust(url, refreshToken);
      if (/^https?:\/\//i.test(text) || text.startsWith('/')) return withRefresh(text);
      const cleaned = text.replace(/\\/g, '/');
      const file = cleaned.split('/').filter(Boolean).pop();
      return file ? withRefresh(`./${encodeURIComponent(file)}`) : '';
    }
    function localVectorBaseStyle(meta, feature) {
      const properties = feature?.properties || {};
      const confidence = Number(properties.confidence);
      const opacity = Number.isFinite(Number(meta?.opacity)) ? Number(meta.opacity) : 0.95;
      const datasetText = `${meta?.dataset || ''} ${meta?.name || ''} ${properties.object_class || ''} ${properties.road_type || ''}`.toLowerCase();
      const geometryType = String(feature?.geometry?.type || '').toLowerCase();
      const isLine = geometryType.includes('line');
      const isPoint = geometryType.includes('point');
      const isRoad = datasetText.includes('road');
      const isCar = datasetText.includes('car') || datasetText.includes('vehicle');
      if (isRoad) {
        const stroke = confidence >= 0.9 ? '#f59e0b' : confidence >= 0.75 ? '#22c55e' : '#38bdf8';
        return {
          color: stroke,
          weight: confidence >= 0.9 ? 4 : confidence >= 0.75 ? 3.2 : 2.6,
          opacity,
          fill: false,
          dashArray: confidence >= 0.75 ? null : '6 6',
        };
      }
      if (isCar) {
        const stroke = confidence >= 0.85 ? '#f97316' : confidence >= 0.7 ? '#06b6d4' : '#d946ef';
        return {
          color: stroke,
          weight: 1.4,
          opacity,
          fill: true,
          fillColor: stroke,
          fillOpacity: Math.max(0.12, Math.min(0.55, opacity * 0.32)),
        };
      }
      if (isLine) {
        return {
          color: '#16734d',
          weight: 2.8,
          opacity,
          fill: false,
        };
      }
      return {
        color: '#16734d',
        weight: 2.4,
        opacity,
        fill: !isLine,
        fillColor: '#16734d',
        fillOpacity: isPoint ? Math.max(0.18, Math.min(0.55, opacity * 0.28)) : Math.max(0.1, Math.min(0.45, opacity * 0.2)),
      };
    }
    function localVectorTooltip(feature) {
      const properties = feature?.properties || {};
      const parts = [
        properties.name,
        properties.id,
        properties.object_class,
        properties.road_type,
        properties.status_hint,
      ].filter(Boolean);
      const confidence = Number(properties.confidence);
      if (Number.isFinite(confidence)) parts.push(`confidence ${confidence.toFixed(2)}`);
      return parts.join(' | ');
    }
    function refreshLocalVectorLayer(record) {
      const overlay = record?.tile?.__vectorOverlay;
      if (!overlay) return;
      overlay.eachLayer(layer => {
        if (typeof layer.setStyle === 'function') {
          layer.setStyle(localVectorBaseStyle(record.meta, layer.feature));
        }
      });
    }
    function createLocalVectorLayer(meta) {
      const group = L.layerGroup();
      const sourceUrl = localVectorSourceUrl(meta);
      if (!sourceUrl) return { layer: group, refresh: () => {} };
      const refresh = () => refreshLocalVectorLayer({ meta, tile: group });
      group.__vectorReady = fetch(sourceUrl)
        .then(response => {
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          return response.json();
        })
        .then(data => {
          const overlay = L.geoJSON(data, {
            style: feature => localVectorBaseStyle(meta, feature),
            pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
              ...localVectorBaseStyle(meta, feature),
              radius: 6,
            }),
            onEachFeature: (feature, layer) => {
              const tooltip = localVectorTooltip(feature);
              if (tooltip && typeof layer.bindTooltip === 'function') layer.bindTooltip(tooltip, { sticky: true });
            },
          });
          group.__vectorOverlay = overlay;
          group.addLayer(overlay);
          refresh();
          return overlay;
        })
        .catch(error => {
          console.warn('EasyGEE local vector layer load failed:', meta?.name || meta?.id || 'layer', error);
          return null;
        });
      return { layer: group, refresh };
    }
    function normalizeStateLayer(meta) {
      if (!meta || typeof meta !== 'object') return null;
      if (isUploadPlaceholderLayer(meta) && meta.summary?.renderable === false) return null;
      const next = {
        ...meta,
        shown: meta.shown !== false,
        opacity: Number.isFinite(Number(meta.opacity)) ? Math.max(0, Math.min(1, Number(meta.opacity))) : 0.82,
      };
      if (isBasemapOverlayLayer(next)) {
        next.sourceId = String(next.sourceId || '').trim();
        if (!next.sourceId) return null;
        next.role = 'overlay';
        next.styleProfile = 'basemap';
      }
      next.styleProfile = next.styleProfile || layerStyleProfile(next);
      if (!next.stylePreset && visualPreferences[next.styleProfile]) next.stylePreset = visualPreferences[next.styleProfile];
      return next;
    }
    function replaceStateLayers(layers) {
      Array.from(layerRegistry.values()).forEach(record => {
        if (record?.tile && map.hasLayer(record.tile)) map.removeLayer(record.tile);
      });
      layerRegistry.clear();
      STATE.layers = (Array.isArray(layers) ? layers : []).map(normalizeStateLayer).filter(Boolean);
      STATE.layers.forEach(registerLayer);
      operationalMapOrderDirty = true;
      syncOperationalLayerOrder();
      if (activeLayerId && !layerModels().some(layer => layer?.id === activeLayerId)) {
        activeLayerId = null;
      }
    }
    function uploadExtension(name = '') {
      const text = String(name || '').toLowerCase();
      const dot = text.lastIndexOf('.');
      return dot >= 0 ? text.slice(dot) : '';
    }
    function uploadFormatForName(name = '') {
      const ext = uploadExtension(name);
      if (ext === '.geojson' || ext === '.json') return 'GeoJSON';
      if (ext === '.zip') return 'ZIP/Shapefile';
      if (['.shp', '.shx', '.dbf', '.prj', '.cpg'].includes(ext)) return 'Shapefile';
      if (ext === '.kml' || ext === '.kmz') return ext.slice(1).toUpperCase();
      if (ext === '.gpx') return 'GPX';
      if (ext === '.csv') return 'CSV';
      if (ext === '.gpkg') return 'GPKG';
      return 'Unknown';
    }
    function uploadProcessingHints(record) {
      const format = String(record?.format || uploadFormatForName(record?.name)).toLowerCase();
      if (record?.renderable || record?.previewUrl) {
        return {
          browserPreview: true,
          agentAction: 'loaded as a local preview layer; optional QA or convert to EE FeatureCollection',
          expectedGeometry: 'browser-renderable GeoJSON preview',
        };
      }
      if (format.includes('geojson')) {
        return {
          browserPreview: true,
          agentAction: 'optional QA or convert GeoJSON to EE FeatureCollection',
          expectedGeometry: 'GeoJSON FeatureCollection or Geometry',
        };
      }
      if (format.includes('csv')) {
        return {
          browserPreview: false,
          agentAction: 'inspect columns, detect lon/lat or WKT, then convert to GeoJSON/EE table',
          expectedGeometry: 'point table or WKT geometry columns',
        };
      }
      if (format.includes('shapefile') || format.includes('zip')) {
        return {
          browserPreview: false,
          agentAction: 'read saved shapefile bundle with geopandas/ogr, apply projection if missing, then add vector layer',
          expectedGeometry: 'vector features',
        };
      }
      if (format.includes('gpkg')) {
        return {
          browserPreview: false,
          agentAction: 'inspect GeoPackage layers with geopandas/ogr and choose a layer to add',
          expectedGeometry: 'vector or raster package layer',
        };
      }
      if (format.includes('kml') || format.includes('kmz') || format.includes('gpx')) {
        return {
          browserPreview: false,
          agentAction: 'convert GPS/KML features to GeoJSON before map overlay',
          expectedGeometry: 'vector tracks, points, or polygons',
        };
      }
      return {
        browserPreview: false,
        agentAction: 'inspect saved file and choose a geospatial conversion path',
        expectedGeometry: 'unknown',
      };
    }
    function normalizeUploadRecord(record) {
      if (!record || typeof record !== 'object') return null;
      const name = String(record.name || record.storedName || 'upload');
      const format = record.format || uploadFormatForName(name);
      const extension = record.extension || uploadExtension(name);
      const shapefileSidecarOnly = ['.dbf', '.shx', '.prj', '.cpg'].includes(String(extension).toLowerCase());
      const renderable = record.renderable === true || Boolean(record.previewUrl) || String(format || '').toLowerCase().includes('geojson');
      const timestamp = new Date().toISOString();
      const next = {
        id: String(record.id || `upload-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`),
        name,
        storedName: record.storedName || name,
        extension,
        format,
        size: Number(record.size || 0),
        projection: record.projection || $('upload-projection')?.value || 'EPSG:4326',
        savedPath: record.savedPath || null,
        url: record.url || null,
        componentPaths: record.componentPaths || null,
        previewPath: record.previewPath || null,
        previewUrl: record.previewUrl || null,
        previewFormat: record.previewFormat || null,
        previewFeatureCount: Number.isFinite(Number(record.previewFeatureCount)) ? Number(record.previewFeatureCount) : null,
        previewLimited: record.previewLimited === true,
        previewError: record.previewError || null,
        renderable,
        agentReadable: record.agentReadable !== false,
        status: record.status || 'saved',
        createdAt: record.createdAt || timestamp,
        updatedAt: record.updatedAt || record.createdAt || timestamp,
        layerId: renderable ? (record.layerId || null) : null,
      };
      if (shapefileSidecarOnly && !next.renderable) {
        next.status = 'missing-shapefile-components';
        next.previewError = next.previewError || 'Shapefile upload is incomplete. Select the .shp geometry file together with .shx and .dbf, or upload a ZIP containing all components.';
      }
      next.processingHints = record.processingHints || uploadProcessingHints(next);
      next.recommendedAgentAction = record.recommendedAgentAction || next.processingHints.agentAction;
      return next;
    }
    function persistUploads() {
      localStorage.setItem(UPLOADS_STORAGE_KEYS[0], JSON.stringify((STATE.uploads || []).slice(0, 50)));
    }
    function restoreUploads() {
      for (const key of UPLOADS_STORAGE_KEYS) {
        try {
          const parsed = JSON.parse(localStorage.getItem(key) || '[]');
          const uploads = Array.isArray(parsed) ? parsed.map(normalizeUploadRecord).filter(Boolean) : [];
          if (uploads.length) return uploads;
        } catch {}
      }
      return [];
    }
    function formatBytes(value) {
      const size = Number(value || 0);
      if (!Number.isFinite(size) || size <= 0) return '0 B';
      if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`;
      if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`;
      return `${Math.round(size)} B`;
    }
    function renderUploads() {
      const fileInput = $('upload-file-input');
      const fileCount = fileInput?.files?.length || 0;
      const nameTarget = $('upload-file-name');
      if (nameTarget) {
        if (!fileCount) nameTarget.textContent = t('upload.noFile');
        else if (fileCount === 1) nameTarget.textContent = fileInput.files[0].name;
        else nameTarget.textContent = t('upload.ready', { count: fileCount });
      }
      const submit = $('upload-submit-btn');
      if (submit) submit.disabled = fileCount <= 0;
      const list = $('upload-list');
      if (!list) return;
      const uploads = (Array.isArray(STATE.uploads) ? STATE.uploads : []).map(normalizeUploadRecord).filter(Boolean);
      if (!uploads.length) {
        list.innerHTML = `<div class="upload-status">${escapeHtml(t('upload.empty'))}</div>`;
        return;
      }
      list.innerHTML = uploads.slice(0, 8).map(record => `
        <div class="upload-item" data-upload="${escapeHtml(record.id)}">
          <div class="upload-item-top">
            <div class="upload-item-name">${escapeHtml(record.name)}</div>
            <div class="upload-item-actions">
              <span class="upload-item-tag">${escapeHtml(record.format)}</span>
              <button class="upload-remove icon-btn" data-upload-remove="${escapeHtml(record.id)}" title="${escapeHtml(t('upload.remove'))}" aria-label="${escapeHtml(t('upload.remove'))}" type="button">__EASYGEE_ICON_TRASH__</button>
            </div>
          </div>
          <div class="upload-item-meta">${escapeHtml(formatBytes(record.size))} · ${escapeHtml(record.projection || '-')} · ${escapeHtml(t('upload.agentReady'))}</div>
          <div class="upload-item-meta">${escapeHtml(record.savedPath || record.url || record.status || '')}</div>
          ${record.layerId ? `<div class="upload-item-meta">${escapeHtml(t('upload.layerAdded'))}</div>` : ''}
          ${!record.layerId && !record.renderable ? `<div class="upload-item-meta">${escapeHtml(record.previewError || t('upload.notRenderable'))}</div>` : ''}
        </div>
      `).join('');
      list.querySelectorAll('[data-upload-remove]').forEach(button => {
        button.addEventListener('click', event => {
          event.stopPropagation();
          removeUpload(button.dataset.uploadRemove);
        });
      });
    }
    function uploadedLayerId(record) {
      return `upload-${record.id.replace(/[^a-z0-9_-]+/gi, '-')}-vector`;
    }
    function addUploadedLayer(record) {
      if (!record) return null;
      const layerId = uploadedLayerId(record);
      const sourceUrl = record.previewUrl || (String(record.format || '').toLowerCase().includes('geojson') ? record.url : null);
      const baseName = record.name.replace(/\.(geojson|json|csv|kml|kmz|gpx|shp|zip|gpkg)$/i, '');
      if (!sourceUrl) {
        const placeholder = {
          id: layerId,
          name: baseName,
          dataset: `local-upload:${record.name}`,
          type: 'local-upload',
          shown: true,
          opacity: 1,
          styleProfile: 'vector',
          stylePreset: 'default',
          legend: [['#64748b', 'Uploaded file']],
          recipe: {
            kind: 'localUploadPlaceholder',
            source: 'userUpload',
            savedPath: record.savedPath,
            componentPaths: record.componentPaths,
            projection: record.projection,
            format: record.format,
            status: record.status,
            previewError: record.previewError,
            recommendedAgentAction: record.recommendedAgentAction,
          },
          summary: {
            format: record.format,
            size: record.size,
            uploadedAt: record.createdAt,
            savedPath: record.savedPath,
            componentPaths: record.componentPaths,
            previewError: record.previewError,
            renderable: false,
          },
        };
        addGeneratedLayer(placeholder);
        return layerId;
      }
      const layer = {
        id: layerId,
        name: baseName,
        dataset: `local-upload:${record.name}`,
        type: 'local-vector',
        shown: true,
        opacity: 0.92,
        sourceUrl,
        previewUrl: sourceUrl,
        styleProfile: 'vector',
        stylePreset: 'default',
        legend: [['#16734d', 'Uploaded features']],
        recipe: {
          kind: 'localVectorOverlay',
          source: 'userUpload',
          sourceUrl,
          previewUrl: sourceUrl,
          savedPath: record.savedPath,
          previewPath: record.previewPath,
          componentPaths: record.componentPaths,
          projection: record.projection,
          format: record.format,
          previewFeatureCount: record.previewFeatureCount,
        },
        summary: {
          format: record.format,
          size: record.size,
          uploadedAt: record.createdAt,
          savedPath: record.savedPath,
          previewPath: record.previewPath,
          previewFeatureCount: record.previewFeatureCount,
          previewLimited: record.previewLimited,
          renderable: true,
        },
      };
      addGeneratedLayer(layer);
      return layerId;
    }
    function rememberUploads(records) {
      const existing = new Map((STATE.uploads || []).map(item => [item.id, item]));
      records.map(normalizeUploadRecord).filter(Boolean).forEach(record => existing.set(record.id, record));
      STATE.uploads = Array.from(existing.values()).slice(-50).reverse();
      persistUploads();
      renderUploads();
    }
    function removeUpload(uploadId) {
      const id = String(uploadId || '');
      if (!id) return false;
      const uploads = (Array.isArray(STATE.uploads) ? STATE.uploads : []).map(normalizeUploadRecord).filter(Boolean);
      const record = uploads.find(item => item.id === id);
      if (!record) return false;
      STATE.uploads = uploads.filter(item => item.id !== id);
      persistUploads();
      if (record.layerId) removeLayer(record.layerId);
      renderUploads();
      syncSessionState('upload-removed');
      return true;
    }
    async function uploadSelectedFiles() {
      const input = $('upload-file-input');
      const files = Array.from(input?.files || []);
      if (!files.length) return false;
      const oversized = files.find(file => file.size > UPLOAD_CAPABILITIES.maxBytes);
      const status = $('upload-status');
      if (oversized) {
        status.textContent = t('upload.tooLarge', { name: oversized.name });
        status.classList.add('error');
        return false;
      }
      status.textContent = t('upload.saving');
      status.classList.remove('error');
      const form = new FormData();
      files.forEach(file => form.append('files', file, file.name));
      form.append('projection', $('upload-projection').value || 'EPSG:4326');
      try {
        const response = await fetch(UPLOAD_CAPABILITIES.endpoint, { method: 'POST', body: form });
        const payload = await response.json().catch(() => ({ ok: false, error: response.statusText || 'upload failed' }));
        if (!response.ok || !payload.ok) throw new Error(payload.error || `HTTP ${response.status}`);
        const savedRecords = (Array.isArray(payload.uploads) ? payload.uploads : []).map(normalizeUploadRecord).filter(Boolean);
        savedRecords.forEach(record => {
          if (record.renderable) {
            record.layerId = addUploadedLayer(record);
            if (record.layerId) record.status = 'layer-added';
          } else {
            record.layerId = null;
            if (!record.status || record.status === 'saved') record.status = 'saved-needs-conversion';
          }
          addTask({
            type: 'upload',
            name: `Upload: ${record.name}`,
            status: record.layerId && record.renderable ? 'done' : 'ready',
            destination: 'EasyGEE local uploads',
            createdAt: record.createdAt,
            params: {
              format: record.format,
              projection: record.projection,
              savedPath: record.savedPath,
              previewPath: record.previewPath,
              url: record.url,
              previewUrl: record.previewUrl,
              renderable: record.renderable,
              previewError: record.previewError,
              recommendedAgentAction: record.recommendedAgentAction,
            },
            notes: [record.previewError, record.recommendedAgentAction].filter(Boolean),
          }, { reason: 'upload-task' });
          logMsg('log.uploadSaved', { file: record.name });
        });
        rememberUploads(savedRecords);
        input.value = '';
        const addedCount = savedRecords.filter(record => record.layerId).length;
        status.textContent = addedCount === savedRecords.length
          ? t('upload.saved', { count: savedRecords.length })
          : t('upload.savedPartial', { total: savedRecords.length, added: addedCount });
        status.classList.toggle('error', addedCount < savedRecords.length);
        renderUploads();
        syncSessionState('uploads');
        return true;
      } catch (error) {
        const message = error && error.message ? error.message : String(error);
        status.textContent = t('upload.failed', { message });
        status.classList.add('error');
        syncSessionState('upload-failed');
        return false;
      }
    }
    function palettePreviewHtml(palette = []) {
      if (!Array.isArray(palette) || !palette.length) return '';
      return `<div class="palette-preview">${palette.map(color => `<span style="background:${escapeHtml(color)}"></span>`).join('')}</div>`;
    }
    function sanitizeVisParams(value) {
      if (!value || typeof value !== 'object') return {};
      const out = {};
      ['min', 'max', 'gamma'].forEach(key => {
        const num = Number(value[key]);
        if (Number.isFinite(num)) out[key] = num;
      });
      if (Array.isArray(value.bands)) out.bands = value.bands.map(String).filter(Boolean).slice(0, 4);
      if (Array.isArray(value.palette)) out.palette = value.palette.map(String).filter(isHexColor).slice(0, 32);
      return out;
    }
    function readLocalJson(keys, fallbackText = 'null') {
      for (const key of keys) {
        try {
          const raw = localStorage.getItem(key);
          if (raw != null) return JSON.parse(raw);
        } catch {}
      }
      try {
        return JSON.parse(fallbackText);
      } catch {
        return null;
      }
    }
    function loadPersistedAoi() {
      try {
        const parsed = readLocalJson(AOI_STORAGE_KEYS, 'null');
        const restored = normalizeAoi(parsed && parsed.aoi ? parsed.aoi : parsed);
        return restored || null;
      } catch {
        return null;
      }
    }
    function persistAoi() {
      if (!STATE.aoi) {
        AOI_STORAGE_KEYS.forEach(key => localStorage.removeItem(key));
        return;
      }
      localStorage.setItem(AOI_STORAGE_KEYS[0], JSON.stringify({
        project: STATE.project,
        title: STATE.title,
        aoi: STATE.aoi,
        updatedAt: new Date().toISOString(),
      }));
    }
    function hasAoi() {
      return Boolean(STATE.aoi && normalizeAoi(STATE.aoi));
    }
    function hasAoiBounds() {
      return Boolean(hasAoi() && normalizeBounds(STATE.aoi.bounds));
    }
    function currentAoiBounds() {
      return hasAoiBounds() ? STATE.aoi.bounds : null;
    }
    function cogBasemapBounds(meta) {
      if (!meta?.custom || meta.type !== 'cog' || !Array.isArray(meta.bounds) || meta.bounds.length !== 4) return null;
      const values = meta.bounds.map(Number);
      if (!values.every(Number.isFinite) || values[0] >= values[2] || values[1] >= values[3]) return null;
      return L.latLngBounds([[values[1], values[0]], [values[3], values[2]]]);
    }
    function fitCogBasemapBounds(meta, force = false) {
      const bounds = cogBasemapBounds(meta);
      if (!bounds || (!force && map.getBounds().intersects(bounds))) return false;
      map.fitBounds(bounds, { padding: [42, 42], maxZoom: Math.min(meta.maxNativeZoom || 17, 17) });
      return true;
    }
    function resetHomeView() {
      const activeBasemap = BASEMAPS.find(meta => meta.id === currentBasemap);
      const activeCogBounds = cogBasemapBounds(activeBasemap);
      const aoiBounds = hasAoiBounds() ? L.latLngBounds(STATE.aoi.bounds) : null;
      if (activeCogBounds && (!aoiBounds || !aoiBounds.intersects(activeCogBounds))) {
        fitCogBasemapBounds(activeBasemap, true);
        return;
      }
      if (hasAoiBounds()) {
        map.fitBounds(STATE.aoi.bounds, { padding: [24, 24] });
      } else {
        map.setView(STATE.center || [__EASYGEE_DEFAULT_CENTER_LAT__, __EASYGEE_DEFAULT_CENTER_LON__], STATE.zoom || __EASYGEE_DEFAULT_ZOOM__);
      }
    }
    function mapBoundsAoi() {
      const bounds = map.getBounds();
      return aoiFromBounds([[bounds.getSouth(), bounds.getWest()], [bounds.getNorth(), bounds.getEast()]]);
    }
    function currentProcessingAoi() {
      return hasAoi() ? cloneAoi(STATE.aoi) : mapBoundsAoi();
    }
    function currentProcessingBounds() {
      const aoi = currentProcessingAoi();
      return aoi ? aoi.bounds : null;
    }
    function normalizeMeasurement(item) {
      if (!item || typeof item !== 'object') return null;
      const start = normalizeLatLngPair(item.start);
      const end = normalizeLatLngPair(item.end);
      const lengthMeters = Number(item.lengthMeters);
      if (!start || !end || !Number.isFinite(lengthMeters) || lengthMeters < 0) return null;
      return {
        id: String(item.id || `measure-${Date.now().toString(36)}`),
        start,
        end,
        lengthMeters,
        lengthLabel: item.lengthLabel || formatDistance(lengthMeters),
        createdAt: item.createdAt || new Date().toISOString(),
      };
    }
    function loadPersistedMeasurements() {
      try {
        const parsed = readLocalJson(MEASUREMENTS_STORAGE_KEYS, '[]');
        return Array.isArray(parsed) ? parsed.map(normalizeMeasurement).filter(Boolean) : [];
      } catch {
        return [];
      }
    }
    function persistMeasurements() {
      localStorage.setItem(MEASUREMENTS_STORAGE_KEYS[0], JSON.stringify(STATE.measurements || []));
    }
    function normalizeTask(item) {
      if (!item || typeof item !== 'object') return null;
      const taskId = item.taskId || item.eeTaskId || item.id || '';
      const id = String(item.id || taskId || item.name || item.title || `task-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`);
      const title = String(item.title || item.name || item.analysis || item.type || 'Task');
      const status = String(item.status || item.state || 'ready').toLowerCase();
      const normalized = {
        ...item,
        id,
        title,
        status,
        type: item.type || 'task',
        createdAt: item.createdAt || new Date().toISOString(),
        updatedAt: item.updatedAt || item.createdAt || new Date().toISOString(),
      };
      if (taskId) normalized.taskId = String(taskId);
      return normalized;
    }
    function loadPersistedTasks() {
      try {
        const parsed = readLocalJson(TASKS_STORAGE_KEYS, '[]');
        return Array.isArray(parsed) ? parsed.map(normalizeTask).filter(Boolean) : [];
      } catch {
        return [];
      }
    }
    function persistTasks() {
      localStorage.setItem(TASKS_STORAGE_KEYS[0], JSON.stringify((STATE.tasks || []).slice(0, 30)));
    }
    function taskStatusClass(status) {
      return String(status || 'ready').toLowerCase().replace(/[^a-z0-9_-]+/g, '-');
    }
    function taskParamsText(task) {
      const params = task && typeof task.params === 'object' ? task.params : null;
      if (!params) return '';
      return [
        params.index,
        params.dataset,
        params.startDate && params.endDate ? `${params.startDate} to ${params.endDate}` : '',
        params.scale ? `${params.scale} m` : '',
      ].filter(Boolean).join(' | ');
    }
    function latestDriveTask() {
      return (Array.isArray(STATE.tasks) ? STATE.tasks : []).map(normalizeTask).filter(task => {
        return task && (task.driveSearchUrl || task.destination === 'Google Drive' || task.type === 'drive-export');
      })[0] || null;
    }
    function driveTargetUrl() {
      const task = latestDriveTask();
      if (task?.driveSearchUrl) return task.driveSearchUrl;
      if (task?.fileNamePrefix) return `https://drive.google.com/drive/search?q=${encodeURIComponent(task.fileNamePrefix)}`;
      return 'https://drive.google.com/drive/my-drive';
    }
    function driveTargetLabel() {
      const task = latestDriveTask();
      if (task?.fileNamePrefix) return task.fileNamePrefix;
      if (task?.title) return task.title;
      return 'Google Drive';
    }
    function updateDriveButtonTitle() {
      const button = $('drive-btn');
      if (!button) return;
      const key = latestDriveTask() ? 'tool.driveRecent' : 'tool.driveRoot';
      const label = t(key);
      button.title = label;
      button.setAttribute('aria-label', label);
    }
    function openDriveTarget() {
      const url = driveTargetUrl();
      const opened = window.open(url, '_blank', 'noopener,noreferrer');
      if (!opened) window.location.href = url;
      logMsg('log.driveOpened', { target: driveTargetLabel() });
    }
    function renderTasks() {
      const target = $('task-list');
      if (!target) return;
      const rows = Array.isArray(STATE.tasks) ? STATE.tasks.map(normalizeTask).filter(Boolean) : [];
      STATE.tasks = rows;
      updateDriveButtonTitle();
      if (!rows.length) {
        target.innerHTML = `<div class="quota-note">${escapeHtml(t('tasks.empty'))}</div>`;
        return;
      }
      target.innerHTML = rows.slice(0, 12).map(task => {
        const title = task.title || task.name || 'Task';
        const status = task.status || 'ready';
        const meta = [
          task.destination ? `${t('task.destination')}: ${task.destination}` : '',
          task.folder ? `${t('task.folder')}: ${task.folder}` : '',
          task.fileNamePrefix ? `${t('task.prefix')}: ${task.fileNamePrefix}` : '',
          task.taskId ? `${t('task.id')}: ${task.taskId}` : '',
          taskParamsText(task) ? `${t('task.params')}: ${taskParamsText(task)}` : '',
        ].filter(Boolean);
        const search = task.driveSearchUrl
          ? `<a class="task-link" href="${escapeHtml(task.driveSearchUrl)}" target="_blank" rel="noreferrer">${escapeHtml(t('task.driveSearch'))}</a>`
          : '';
        const note = Array.isArray(task.notes) && task.notes.length ? `<div>${escapeHtml(task.notes[0])}</div>` : '';
        return `
          <div class="task-row status-${escapeHtml(taskStatusClass(status))}">
            <div class="task-head">
              <div class="task-title">${escapeHtml(title)}</div>
              <div class="task-status" title="${escapeHtml(status)}">${escapeHtml(status)}</div>
            </div>
            <div class="task-meta">${meta.map(item => `<div>${escapeHtml(item)}</div>`).join('')}${note}</div>
            ${search ? `<div class="task-actions">${search}</div>` : ''}
          </div>
        `;
      }).join('');
    }
    function addTask(task, options = {}) {
      const normalized = normalizeTask(task);
      if (!normalized) return false;
      const index = (STATE.tasks || []).findIndex(item => {
        const existing = normalizeTask(item);
        return existing && (existing.id === normalized.id || (existing.taskId && normalized.taskId && existing.taskId === normalized.taskId));
      });
      normalized.updatedAt = new Date().toISOString();
      if (index >= 0) {
        STATE.tasks.splice(index, 1);
      }
      STATE.tasks.unshift(normalized);
      STATE.tasks = STATE.tasks.slice(0, 30);
      persistTasks();
      renderTasks();
      updateDriveButtonTitle();
      logMsg(options.logKey || 'log.taskAdded', { task: normalized.title });
      syncSessionState(options.reason || 'task-added');
      return true;
    }
    function measurementSummary(measurements = STATE.measurements) {
      const rows = Array.isArray(measurements) ? measurements.filter(item => Number.isFinite(Number(item.lengthMeters))) : [];
      const lengths = rows.map(item => Number(item.lengthMeters));
      const totalMeters = lengths.reduce((sum, value) => sum + value, 0);
      const count = lengths.length;
      const meanMeters = count ? totalMeters / count : 0;
      return {
        count,
        totalMeters,
        meanMeters,
        minMeters: count ? Math.min(...lengths) : 0,
        maxMeters: count ? Math.max(...lengths) : 0,
        totalLabel: formatDistance(totalMeters),
        meanLabel: formatDistance(meanMeters),
        minLabel: formatDistance(count ? Math.min(...lengths) : 0),
        maxLabel: formatDistance(count ? Math.max(...lengths) : 0),
      };
    }
    function initializePersistentState() {
      const generatedAoi = normalizeAoi(STATE.aoi) || aoiFromBounds(STATE.bounds);
      const restoredAoi = loadPersistedAoi();
      STATE.aoi = restoredAoi || generatedAoi || null;
      STATE.bounds = STATE.aoi ? STATE.aoi.bounds : null;
      STATE.aoiStyle = normalizeAoiStyle(STATE.aoiStyle);
      STATE.aoiShown = STATE.aoiShown !== false;
      STATE.measurementsShown = STATE.measurementsShown !== false;
      STATE.measurementsOpacity = normalizeMeasurementsOpacity(STATE.measurementsOpacity);
      const generatedMeasurements = Array.isArray(STATE.measurements) ? STATE.measurements.map(normalizeMeasurement).filter(Boolean) : [];
      const restoredMeasurements = loadPersistedMeasurements();
      STATE.measurements = restoredMeasurements.length ? restoredMeasurements : generatedMeasurements;
      const generatedTasks = Array.isArray(STATE.tasks) ? STATE.tasks.map(normalizeTask).filter(Boolean) : [];
      const restoredTasks = loadPersistedTasks();
      STATE.tasks = restoredTasks.length ? restoredTasks : generatedTasks;
      const generatedUploads = Array.isArray(STATE.uploads) ? STATE.uploads.map(normalizeUploadRecord).filter(Boolean) : [];
      const restoredUploads = restoreUploads();
      STATE.uploads = restoredUploads.length ? restoredUploads : generatedUploads;
      if (restoredAoi) logMsg('log.aoiRestored');
    }
    function profileProjectEntry(profile) {
      if (!profile || typeof profile !== 'object' || !profile.projects || typeof profile.projects !== 'object') return null;
      if (profile.projects[PROJECT_STORAGE_ID] && typeof profile.projects[PROJECT_STORAGE_ID] === 'object') return profile.projects[PROJECT_STORAGE_ID];
      const project = String(STATE.project || '');
      const title = String(STATE.title || '');
      return Object.values(profile.projects).find(entry => entry && typeof entry === 'object' && (entry.project === project || entry.title === title)) || null;
    }
    function applySessionProfile(profile) {
      if (!profile || typeof profile !== 'object') return false;
      let changed = false;
      let basemapProfileChanged = false;
      let preferredBasemap = null;
      if (Array.isArray(profile.favoriteDatasets) && (profile.updatedAt || profile.favoriteDatasets.length)) {
        const nextFavorites = normalizeFavoriteDatasetIds(profile.favoriteDatasets);
        const currentFavorites = [...favoriteDatasetIds].sort();
        if (JSON.stringify(nextFavorites) !== JSON.stringify(currentFavorites)) {
          favoriteDatasetIds = new Set(nextFavorites);
          saveFavoriteDatasetIds();
          changed = true;
        }
      }
      if (profile.visualPreferences && typeof profile.visualPreferences === 'object') {
        visualPreferences = { ...visualPreferences, ...profile.visualPreferences };
        changed = true;
      }
      if (Array.isArray(profile.customBasemaps)) {
        const nextCustomBasemaps = normalizeCustomBasemaps(profile.customBasemaps);
        const currentText = JSON.stringify(customBasemaps.map(serializableCustomBasemap));
        const nextText = JSON.stringify(nextCustomBasemaps.map(serializableCustomBasemap));
        if (currentText !== nextText) {
          customBasemaps = nextCustomBasemaps;
          basemapProfileChanged = true;
        }
      }
      if (typeof profile.defaultBasemap === 'string' && profile.defaultBasemap.trim()) {
        const nextDefault = profile.defaultBasemap.trim();
        if (nextDefault !== defaultBasemapId) basemapProfileChanged = true;
        defaultBasemapId = nextDefault;
        preferredBasemap = nextDefault;
      }
      const entry = profileProjectEntry(profile);
      if (entry) {
        if (entry.view && typeof entry.view === 'object') {
          const center = Array.isArray(entry.view.center) ? entry.view.center.map(Number) : [];
          const zoom = Number(entry.view.zoom);
          if (center.length === 2 && center.every(Number.isFinite) && center[0] >= -90 && center[0] <= 90 && center[1] >= -180 && center[1] <= 180 && Number.isFinite(zoom)) {
            restoredProfileView = { center, zoom: Math.max(0, Math.min(24, zoom)) };
            STATE.center = [...center];
            STATE.zoom = restoredProfileView.zoom;
            changed = true;
          }
        }
        if (entry.view && typeof entry.view === 'object' && typeof entry.view.basemap === 'string') {
          preferredBasemap = entry.view.basemap;
          basemapProfileChanged = true;
        }
        if (entry.view && typeof entry.view === 'object' && typeof entry.view.basemapShown === 'boolean') {
          primaryBasemapShown = entry.view.basemapShown;
          basemapProfileChanged = true;
        }
        if (entry.view && typeof entry.view === 'object' && Number.isFinite(Number(entry.view.basemapOpacity))) {
          primaryBasemapOpacity = Math.max(0, Math.min(1, Number(entry.view.basemapOpacity)));
          basemapProfileChanged = true;
        }
        const profileAoi = normalizeAoi(entry.aoi);
        if (profileAoi && JSON.stringify(profileAoi) !== JSON.stringify(STATE.aoi || null)) {
          STATE.aoi = profileAoi;
          STATE.bounds = profileAoi.bounds;
          persistAoi();
          changed = true;
          logMsg('log.aoiRestored');
        }
        if (entry.aoiStyle && typeof entry.aoiStyle === 'object') {
          STATE.aoiStyle = normalizeAoiStyle(entry.aoiStyle);
          changed = true;
        }
        if (typeof entry.aoiShown === 'boolean') {
          STATE.aoiShown = entry.aoiShown;
          changed = true;
        }
        if (Array.isArray(entry.measurements)) {
          const profileMeasurements = entry.measurements.map(normalizeMeasurement).filter(Boolean);
          if (JSON.stringify(profileMeasurements) !== JSON.stringify(STATE.measurements || [])) {
            STATE.measurements = profileMeasurements;
            persistMeasurements();
            changed = true;
          }
        }
        if (typeof entry.measurementsShown === 'boolean') {
          STATE.measurementsShown = entry.measurementsShown;
          changed = true;
        }
        if (entry.measurementsOpacity !== undefined) {
          const opacity = normalizeMeasurementsOpacity(entry.measurementsOpacity);
          if (opacity !== STATE.measurementsOpacity) {
            STATE.measurementsOpacity = opacity;
            changed = true;
          }
        }
        if (Array.isArray(entry.tasks)) {
          const profileTasks = entry.tasks.map(normalizeTask).filter(Boolean);
          if (JSON.stringify(profileTasks) !== JSON.stringify(STATE.tasks || [])) {
            STATE.tasks = profileTasks;
            persistTasks();
            changed = true;
          }
        }
        if (Array.isArray(entry.uploads)) {
          const profileUploads = entry.uploads.map(normalizeUploadRecord).filter(Boolean);
          if (JSON.stringify(profileUploads) !== JSON.stringify(STATE.uploads || [])) {
            STATE.uploads = profileUploads;
            persistUploads();
            changed = true;
          }
        }
        const describeLayers = layers => JSON.stringify((layers || []).map(layer => ({
            id: layer.id,
            name: layer.name,
            dataset: layer.dataset,
            type: layer.type,
            shown: layer.shown !== false,
            opacity: layer.opacity,
            role: layer.role || null,
            sourceId: layer.sourceId || null,
            styleProfile: layer.styleProfile || null,
            stylePreset: layer.stylePreset || null,
            recipe: layer.recipe || null,
            summary: layer.summary || null,
        })));
        if (Array.isArray(entry.layers)) {
          const restoredLayers = entry.layers.map(normalizeStateLayer).filter(Boolean);
          if (describeLayers(restoredLayers) !== describeLayers(STATE.layers || [])) {
            replaceStateLayers(restoredLayers);
            changed = true;
          }
        } else if (Array.isArray(entry.recentLayers)) {
          const recentById = new Map(entry.recentLayers
            .filter(layer => layer && typeof layer === 'object' && layer.id)
            .map(layer => [String(layer.id), layer]));
          const restoredGeneratedLayers = (STATE.layers || []).filter(layer => !isBasemapOverlayLayer(layer)).map(layer => {
            const recent = recentById.get(String(layer.id));
            return recent
              ? normalizeStateLayer({ ...layer, ...recent, tileUrl: layer.tileUrl })
              : layer;
          }).filter(Boolean);
          const restoredBasemapOverlays = entry.recentLayers
            .filter(layer => isBasemapOverlayLayer(layer) && basemapMetaById(layer.sourceId))
            .map(normalizeStateLayer)
            .filter(Boolean);
          const restoredLayers = [...restoredBasemapOverlays, ...restoredGeneratedLayers];
          const restoredIds = new Set(restoredLayers.map(layer => String(layer.id)));
          // ponytail: restore at most eight remote EE layers per startup; add a queued loader if larger workspaces become common.
          pendingProfileLayers = entry.recentLayers
            .filter(layer => profileLayerCanBeRebuilt(layer) && !restoredIds.has(String(layer.id)))
            .slice(0, 8);
          if (pendingProfileLayers.length) changed = true;
          if (describeLayers(restoredLayers) !== describeLayers(STATE.layers || [])) {
            replaceStateLayers(restoredLayers);
            changed = true;
          }
        }
        if (Array.isArray(entry.layerOrder)) {
          const nextLayerOrder = entry.layerOrder.map(value => String(value));
          if (JSON.stringify(nextLayerOrder) !== JSON.stringify(operationalLayerOrder)) {
            operationalLayerOrder = nextLayerOrder;
            operationalMapOrderDirty = true;
            changed = true;
          }
        }
        restoredProfileActiveLayerId = typeof entry.activeLayerId === 'string' && entry.activeLayerId.trim()
          ? entry.activeLayerId.trim()
          : null;
      }
      if (basemapProfileChanged) {
        if (![...BUILTIN_BASEMAPS, ...customBasemaps].some(meta => meta.id === defaultBasemapId)) defaultBasemapId = 'OSM';
        rebuildBasemapRegistry(preferredBasemap || defaultBasemapId);
        changed = true;
      }
      return changed;
    }
    function profileLayerCanBeRebuilt(layer) {
      if (!layer || typeof layer !== 'object' || isBasemapOverlayLayer(layer) || layer.type === 'local-upload') return false;
      return Boolean(String(layer.dataset || '').trim() && layer.recipe && typeof layer.recipe === 'object');
    }
    function profileRestorePlaceholder(saved) {
      return normalizeStateLayer({
        ...saved,
        type: 'ee-restore-pending',
        shown: saved.shown !== false,
        summary: { ...(saved.summary || {}), restorePending: true },
      });
    }
    function restoreProfileMapView() {
      if (!restoredProfileView) return false;
      map.setView(restoredProfileView.center, restoredProfileView.zoom, { animate: false });
      return true;
    }
    async function rebuildProfileLayer(saved) {
      const datasetId = String(saved?.dataset || saved?.recipe?.datasetId || '').trim();
      if (!datasetId) return false;
      const item = datasetById(datasetId) || { id: datasetId, label: saved.name || datasetId, type: saved.type };
      const recipe = saved.recipe && typeof saved.recipe === 'object' ? saved.recipe : null;
      const savedAoi = normalizeAoi(saved.aoi) || currentProcessingAoi();
      try {
        const response = await fetch('/api/layer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project: STATE.project,
            datasetId,
            catalogItem: item,
            recipe,
            aoi: savedAoi,
            bounds: savedAoi?.bounds || currentProcessingBounds(),
            startDate: recipe?.startDate || saved.summary?.startDate || STATE.startDate,
            endDate: recipe?.endDate || saved.summary?.endDate || STATE.endDate,
            cloudPct: saved.summary?.cloudPct ?? STATE.cloudPct,
            name: saved.name,
            visParams: saved.visParams,
            legend: saved.legend,
            stylePreset: saved.stylePreset,
          }),
        });
        const payload = await response.json().catch(() => ({ ok: false }));
        if (!response.ok || !payload.ok || !payload.layer) return false;
        addGeneratedLayer({
          ...payload.layer,
          id: String(saved.id || payload.layer.id),
          name: saved.name || payload.layer.name,
          opacity: Number.isFinite(Number(saved.opacity)) ? Number(saved.opacity) : payload.layer.opacity,
          styleProfile: saved.styleProfile || payload.layer.styleProfile,
          stylePreset: saved.stylePreset || payload.layer.stylePreset,
          visParams: saved.visParams || payload.layer.visParams,
          legend: saved.legend || payload.layer.legend,
          recipe: recipe || payload.layer.recipe,
          summary: saved.summary || payload.layer.summary,
          aoi: savedAoi || payload.layer.aoi,
        }, { activate: false, sync: false, shown: saved.shown !== false });
        return true;
      } catch {
        return false;
      }
    }
    async function restoreRecentProfileLayers() {
      const layers = pendingProfileLayers;
      pendingProfileLayers = [];
      let restored = 0;
      for (const layer of layers) {
        if (await rebuildProfileLayer(layer)) {
          restored += 1;
          continue;
        }
        const placeholder = profileRestorePlaceholder(layer);
        if (placeholder && !STATE.layers.some(item => item.id === placeholder.id)) {
          STATE.layers.push(placeholder);
          registerLayer(placeholder);
        }
      }
      return restored;
    }
    async function restoreProfileFromServer() {
      try {
        await restoreTiandituCredential();
        const response = await fetch('/api/session/profile');
        if (!response.ok) return false;
        const payload = await response.json();
        const changed = applySessionProfile(payload.profile);
        const restoredLayerCount = await restoreRecentProfileLayers();
        if (changed) {
          renderAoiLayer();
          renderLayers();
          renderMeasurements();
          renderTasks();
          renderUploads();
          renderDatasets(filteredCatalog());
          if (!restoreProfileMapView()) resetHomeView();
          const desiredLayerId = restoredProfileActiveLayerId;
          if (desiredLayerId && layerModels().some(layer => layer?.id === desiredLayerId)) setActiveLayer(desiredLayerId, { reveal: false });
          syncSessionState('profile-restored');
        }
        return changed || restoredLayerCount > 0;
      } catch {
        return false;
      }
    }
    function showMode(message, persist = false) {
      currentModeKey = null;
      const chip = $('mode-chip');
      chip.textContent = message;
      chip.classList.add('show');
      window.clearTimeout(showMode.timer);
      if (!persist) {
        showMode.timer = window.setTimeout(() => chip.classList.remove('show'), 2200);
      }
    }
    function showModeKey(key, vars = {}, persist = false) {
      currentModeKey = { key, vars, persist };
      showMode(t(key, vars), persist);
      currentModeKey = { key, vars, persist };
    }
    function setToolActive(id, active) {
      const button = $(id);
      if (button) button.classList.toggle('active', active);
    }
    function syncMeasurementIndicator() {
      const active = measureMode === true;
      const badge = $('active-layer-badge');
      if (badge) {
        badge.classList.toggle('measure-active', active);
        const activeLabel = badge.dataset.activeLabel;
        if (activeLabel) {
          const sourceHint = t('source.trigger');
          const modeHint = active ? t('tool.measureActive') : '';
          const hints = [sourceHint, modeHint].filter(Boolean).join(' · ');
          badge.title = `${activeLabel} · ${hints}`;
          badge.setAttribute('aria-label', `${hints} · ${activeLabel}`);
        }
      }
      const measureButton = $('measure-btn');
      if (measureButton) {
        measureButton.classList.toggle('measure-active', active);
        measureButton.setAttribute('aria-pressed', active ? 'true' : 'false');
        const label = t(active ? 'tool.measureActive' : 'tool.measure');
        measureButton.title = label;
        measureButton.setAttribute('aria-label', label);
      }
      const undoButton = $('measure-undo-btn');
      if (undoButton) {
        const canUndo = measurePoints.length > 0 || (Array.isArray(STATE.measurements) && STATE.measurements.length > 0);
        undoButton.hidden = !active;
        undoButton.disabled = !canUndo;
        const label = t('tool.measureUndo');
        undoButton.title = label;
        undoButton.setAttribute('aria-label', label);
      }
      const layersButton = $('layers-btn');
      if (layersButton) {
        const layersOpen = document.querySelector('.layers-panel')?.classList.contains('open');
        const prompt = !layersOpen && (active || measurementLayerNotice);
        layersButton.classList.toggle('measurement-prompt', prompt);
        layersButton.classList.toggle('measurement-ready', measurementLayerNotice);
        const label = measurementLayerNotice
          ? t('tool.layersMeasurementReady')
          : prompt
            ? t('tool.layersMeasurePrompt')
            : t('tool.layers');
        layersButton.title = label;
        layersButton.setAttribute('aria-label', label);
      }
    }
    function collapseActiveBadge() {
      const badge = $('active-layer-badge');
      if (!badge) return;
      badge.classList.add('collapsed');
      window.clearTimeout(activeBadgeTimer);
      activeBadgeTimer = null;
    }
    function revealActiveBadge(duration = 2600) {
      const badge = $('active-layer-badge');
      if (!badge) return;
      badge.classList.remove('collapsed');
      window.clearTimeout(activeBadgeTimer);
      activeBadgeTimer = null;
      if (duration > 0) {
        activeBadgeTimer = window.setTimeout(collapseActiveBadge, duration);
      }
    }
    function syncToolState() {
      setToolActive('data-btn', document.querySelector('.data-panel').classList.contains('open'));
      setToolActive('upload-btn', document.querySelector('.upload-panel').classList.contains('open'));
      setToolActive('layers-btn', document.querySelector('.layers-panel').classList.contains('open'));
      setToolActive('inspector-btn', document.querySelector('.right').classList.contains('open'));
      setToolActive('draw-aoi-btn', drawAoiMode || drawPolygonMode);
      setToolActive('measure-btn', measureMode);
      syncMeasurementIndicator();
      setToolActive('basemap-btn', document.querySelector('.basemap-panel').classList.contains('open'));
      setToolActive('quota-btn', quotaFocus && document.querySelector('.bottom').classList.contains('open'));
    }
    function applyI18n() {
      document.documentElement.lang = currentLang === 'zh' ? 'zh-CN' : 'en';
      document.querySelectorAll('[data-i18n]').forEach(element => {
        element.textContent = t(element.dataset.i18n);
      });
      document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const label = t(element.dataset.i18nTitle);
        element.title = label;
        element.setAttribute('aria-label', label);
      });
      document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        element.placeholder = t(element.dataset.i18nPlaceholder);
      });
      $('lang-code').textContent = currentLang === 'zh' ? 'EN' : '中';
      $('catalog-count').textContent = t('pill.datasets', { count: STATE.catalog.length });
      $('layer-count').textContent = t('pill.layers', { count: layerCount() });
      $('click-state').textContent = t(clickStateKey);
      renderCatalogFacets();
      renderQuota();
      renderTasks();
      renderUploads();
      renderTiandituAuth();
      renderBasemapChoices();
      updateInspector();
      if (currentModeKey && $('mode-chip').classList.contains('show')) {
        $('mode-chip').textContent = t(currentModeKey.key, currentModeKey.vars);
      }
    }
    function layerKind(layer) {
      if (layer.type === 'aoi') return { label: 'A', className: 'aoi' };
      if (layer.type === 'measurements') return { label: 'M', className: 'measurements' };
      if (layer.type === 'primary-basemap') return { label: 'B', className: 'basemap' };
      if (layer.type === 'basemap-overlay') return { label: 'O', className: 'basemap-overlay' };
      if (String(layer.type || '').includes('vector')) return { label: 'V', className: 'vector' };
      if (layer.type.includes('categorical')) return { label: 'C', className: 'categorical' };
      if (layer.type.includes('derived')) return { label: 'D', className: 'derived' };
      return { label: 'R', className: 'raster' };
    }
    function distanceMeters(a, b) {
      const toRad = value => value * Math.PI / 180;
      const earth = 6371008.8;
      const dLat = toRad(b.lat - a.lat);
      const dLng = toRad(b.lng - a.lng);
      const lat1 = toRad(a.lat);
      const lat2 = toRad(b.lat);
      const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
      return 2 * earth * Math.asin(Math.min(1, Math.sqrt(h)));
    }
    function formatDistance(meters) {
      return meters >= 1000 ? `${(meters / 1000).toFixed(2)} km` : `${meters.toFixed(0)} m`;
    }
    function formatScaleDistance(meters) {
      if (meters >= 1000) {
        const km = meters / 1000;
        return `${km >= 10 ? km.toFixed(0) : km.toFixed(1)} km`;
      }
      return `${Math.round(meters)} m`;
    }
    function setClickState(key) {
      clickStateKey = key;
      $('click-state').textContent = t(clickStateKey);
    }
    function displayBasemapName() {
      const meta = currentBasemapMeta();
      return meta.nameKey ? t(meta.nameKey) : String(meta.name || meta.id || 'Basemap');
    }
    function currentBasemapMeta() {
      return BASEMAPS.find(item => item.id === currentBasemap) || BASEMAPS[0];
    }
    function basemapDisplayName(meta) {
      return meta?.nameKey ? t(meta.nameKey) : String(meta?.name || meta?.id || 'Basemap');
    }
    function basemapDisplayNote(meta) {
      if (meta?.noteKey) return t(meta.noteKey);
      const provider = String(meta?.provider || meta?.service || '-');
      return t('basemap.customNote', { type: String(meta?.type || 'xyz').toUpperCase(), provider });
    }
    function normalizeTiandituToken(value) {
      const token = String(value || '').trim();
      return token && !/[\s&?#]/.test(token) ? token.slice(0, 256) : '';
    }
    function readTiandituToken() {
      try { return normalizeTiandituToken(window.sessionStorage.getItem(TIANDITU_TOKEN_STORAGE_KEY)); } catch { return ''; }
    }
    function isTiandituBasemap(meta) {
      return Boolean(meta?.tiandituBase && meta?.tiandituLabels);
    }
    function renderTiandituAuth() {
      const card = $('tianditu-auth');
      const status = $('tianditu-auth-state');
      const summary = $('tianditu-auth-summary');
      const editor = $('tianditu-auth-editor');
      const input = $('tianditu-token');
      const remember = $('tianditu-token-remember');
      const persistence = $('tianditu-token-persistence');
      if (!card || !status) return;
      const configured = Boolean(tiandituToken);
      const editing = !configured || tiandituKeyEditing;
      card.classList.toggle('configured', configured);
      status.textContent = t(configured
        ? (tiandituTokenRemembered ? 'basemap.tiandituKeyReadyDevice' : 'basemap.tiandituKeyReady')
        : 'basemap.tiandituKeyMissing');
      if (summary) summary.hidden = !configured || editing;
      if (editor) editor.hidden = !editing;
      if (remember) {
        remember.checked = tiandituTokenRemembered;
        remember.disabled = !tiandituCredentialSupported;
      }
      if (persistence) {
        persistence.hidden = !configured || editing || !tiandituCredentialSupported;
        persistence.textContent = t(tiandituTokenRemembered ? 'basemap.tiandituKeyForget' : 'basemap.tiandituKeyRemember');
      }
      if (configured && !editing && input) input.value = '';
    }
    function setTiandituAuthOpen(open) {
      const card = $('tianditu-auth');
      const body = $('tianditu-auth-body');
      const toggle = $('tianditu-auth-toggle');
      if (!card || !body || !toggle) return false;
      card.classList.toggle('open', Boolean(open));
      body.hidden = !open;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      return true;
    }
    function requestTiandituToken() {
      document.querySelector('.basemap-panel')?.classList.add('open');
      tiandituKeyEditing = true;
      renderTiandituAuth();
      setTiandituAuthOpen(true);
      $('tianditu-token')?.focus();
      showModeKey('mode.tiandituKeyRequired', {}, true);
      syncToolState();
      return false;
    }
    function editTiandituToken() {
      if (!tiandituToken) return false;
      tiandituKeyEditing = true;
      renderTiandituAuth();
      $('tianditu-token')?.focus();
      return true;
    }
    async function restoreTiandituCredential() {
      try {
        const response = await fetch('/api/session/credentials/tianditu', { cache: 'no-store' });
        if (!response.ok) return false;
        const payload = await response.json();
        tiandituCredentialSupported = payload.supported === true;
        const token = payload.remembered ? normalizeTiandituToken(payload.token) : '';
        if (token) {
          tiandituToken = token;
          tiandituTokenRemembered = true;
          try { window.sessionStorage.setItem(TIANDITU_TOKEN_STORAGE_KEY, token); } catch {}
          rebuildBasemapRegistry(currentBasemap);
          renderBasemapChoices();
        }
        renderTiandituAuth();
        return Boolean(token);
      } catch {
        renderTiandituAuth();
        return false;
      }
    }
    async function persistTiandituCredential(token, remember) {
      if (!tiandituCredentialSupported) return !remember;
      try {
        const response = await fetch('/api/session/credentials/tianditu', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: remember ? token : '', remember: remember === true }),
        });
        const payload = await response.json().catch(() => ({ ok: false }));
        if (!response.ok || !payload.ok) return false;
        tiandituTokenRemembered = payload.remembered === true;
        return true;
      } catch {
        return false;
      }
    }
    async function toggleTiandituPersistence() {
      if (!tiandituToken || !tiandituCredentialSupported) return false;
      const remember = !tiandituTokenRemembered;
      const saved = await persistTiandituCredential(tiandituToken, remember);
      renderTiandituAuth();
      showModeKey(saved
        ? (remember ? 'mode.tiandituKeyRemembered' : 'mode.tiandituKeySessionOnly')
        : 'mode.tiandituKeyRememberFailed', {}, !saved);
      return saved;
    }
    async function applyTiandituToken() {
      const input = $('tianditu-token');
      const token = normalizeTiandituToken(input?.value);
      if (!token) {
        showModeKey('basemap.tiandituKeyInvalid', {}, true);
        input?.focus();
        return false;
      }
      try { window.sessionStorage.setItem(TIANDITU_TOKEN_STORAGE_KEY, token); } catch {}
      tiandituToken = token;
      const remember = $('tianditu-token-remember')?.checked === true && tiandituCredentialSupported;
      const persistenceUpdated = remember || tiandituTokenRemembered
        ? await persistTiandituCredential(token, remember)
        : true;
      tiandituKeyEditing = false;
      if (input) input.value = '';
      rebuildBasemapRegistry(currentBasemap);
      [...new Set(STATE.layers
        .filter(layer => isBasemapOverlayLayer(layer) && isTiandituBasemap(basemapMetaById(layer.sourceId)))
        .map(layer => layer.sourceId))]
        .forEach(sourceId => reloadBasemapOverlays(sourceId));
      renderTiandituAuth();
      renderBasemapChoices();
      setTiandituAuthOpen(false);
      showModeKey(persistenceUpdated
        ? (tiandituTokenRemembered ? 'mode.tiandituKeyRemembered' : 'mode.tiandituKeySaved')
        : 'mode.tiandituKeyRememberFailed', {}, !persistenceUpdated);
      return true;
    }
    function basemapThumbSvg(meta) {
      switch (meta.thumb) {
        case 'osm':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#f1eed8"/><path d="M0 32C13 28 22 31 31 38C40 44 52 43 64 36V48H0Z" fill="#b8d4a4"/><path d="M-5 8 69 43" stroke="#fff9e7" stroke-width="9"/><path d="M-5 8 69 43" stroke="#cf6b60" stroke-width="3"/><path d="M47-6C44 12 37 29 24 54" stroke="#fff9e7" stroke-width="8"/><path d="M47-6C44 12 37 29 24 54" stroke="#d7a14d" stroke-width="2.6"/><circle cx="40" cy="22" r="3.2" fill="#fff9e7" stroke="#526e61" stroke-width="1.2"/></svg>`;
        case 'light':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#f5f7f4"/><path d="M8 0v48M25 0v48M46 0v48M0 13h64M0 31h64" stroke="#dce3de" stroke-width="1"/><path d="M-4 42C14 31 23 21 35 5C42-4 51-7 68-6" fill="none" stroke="#a9c7ba" stroke-width="5"/><path d="M-4 42C14 31 23 21 35 5C42-4 51-7 68-6" fill="none" stroke="#f9fbf9" stroke-width="2"/><path d="M17-4 55 52" stroke="#cbd5cf" stroke-width="2"/><circle cx="32" cy="9" r="2.7" fill="#6b9e85"/></svg>`;
        case 'dark':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#172425"/><path d="M9 0v48M23 0v48M43 0v48M56 0v48M0 11h64M0 27h64M0 40h64" stroke="#314142" stroke-width="1"/><path d="M-8 44C9 33 18 31 30 19C40 9 47 5 70 4" fill="none" stroke="#59c8ad" stroke-width="3.2"/><path d="M16-6 48 55" stroke="#6577c4" stroke-width="3.4"/><circle cx="30" cy="19" r="3.2" fill="#d0f1e6" stroke="#172425" stroke-width="1.5"/></svg>`;
        case 'voyager':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#eee3c9"/><path d="M0 32C11 26 23 27 32 35C42 43 52 44 64 40V48H0Z" fill="#b9d4b2"/><path d="M-5 7 69 39" stroke="#fff3d8" stroke-width="8"/><path d="M-5 7 69 39" stroke="#e78663" stroke-width="3"/><path d="M48-5C43 12 34 29 19 52" fill="none" stroke="#f8edcf" stroke-width="7"/><path d="M48-5C43 12 34 29 19 52" fill="none" stroke="#75a9b8" stroke-width="2.8"/><path d="M5 16h13v10H5zM48 27h12v9H48z" fill="#e4cda6" stroke="#c9b58f" stroke-width="1"/></svg>`;
        case 'topo':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#e9e4c7"/><path d="M-5 36C6 18 17 10 31 12C44 14 51 28 69 20" fill="none" stroke="#a99365" stroke-width="1.4"/><path d="M-4 42C8 22 18 16 31 18C43 20 51 33 68 27" fill="none" stroke="#b29c6e" stroke-width="1.25"/><path d="M4 47C14 30 22 24 32 25C42 26 49 38 61 34" fill="none" stroke="#b9a678" stroke-width="1.1"/><path d="M11 0C17 8 20 11 29 8C38 4 45 3 55 10C59 13 62 15 67 14" fill="none" stroke="#8da27c" stroke-width="2.2"/><path d="m31 17 5 9H26Z" fill="#7d6c4b"/><circle cx="31" cy="17" r="2" fill="#f7f0d5"/></svg>`;
        case 'imagery':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#284336"/><path d="M0 0h30L18 22 0 19Z" fill="#3f6b47"/><path d="m30 0 20 0 4 20-19 7-17-5Z" fill="#6d7645"/><path d="m50 0 14 0v28l-10-8Z" fill="#947b50"/><path d="M0 19 18 22l7 26H0Z" fill="#4f7a4b"/><path d="m18 22 17 5 8 21H25Z" fill="#8b8258"/><path d="m35 27 19-7 10 8v20H43Z" fill="#45634b"/><path d="M42-5C37 9 38 24 47 53" fill="none" stroke="#366779" stroke-width="4"/><path d="M42-5C37 9 38 24 47 53" fill="none" stroke="#7aa3a5" stroke-opacity=".55" stroke-width="1"/></svg>`;
        case 'clarity':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#858d69"/><path d="M0 0h24L19 18 0 14ZM24 0h22l-6 16-21 2ZM46 0h18v20l-24-4ZM0 14l19 4 5 18-24 7ZM19 18l21-2 5 19-21 1ZM40 16l24 4v20l-19-5ZM0 43l24-7 4 12H0ZM24 36l21-1 9 13H28ZM45 35l19 5v8H54Z" fill="none" stroke="#dfe2bd" stroke-opacity=".66" stroke-width="1.1"/><path d="M8 7h17v10H8z" fill="#cbd8a3"/><path d="M35 25h20v12H35z" fill="#687b58"/><path d="M-3 31 68 8" stroke="#e8e0b8" stroke-width="2.2"/></svg>`;
        case 'tianditu-vector':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#edf2de"/><path d="M0 34c12-8 22-8 32-1s20 8 32 3v12H0Z" fill="#c5ddae"/><path d="M-5 9 69 40" stroke="#fff9df" stroke-width="7"/><path d="M-5 9 69 40" stroke="#d46f5e" stroke-width="2.2"/><path d="M49-5C44 10 37 26 21 53" fill="none" stroke="#f9f6dc" stroke-width="7"/><path d="M49-5C44 10 37 26 21 53" fill="none" stroke="#6ba8bd" stroke-width="2.4"/><circle cx="36" cy="21" r="2.8" fill="#fff" stroke="#507461"/></svg>`;
        case 'tianditu-imagery':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#315342"/><path d="M0 0h25L17 21 0 17ZM25 0h21l-7 18-22 3ZM46 0h18v22l-25-4ZM0 17l17 4 7 27H0ZM17 21l22-3 7 30H24ZM39 18l25 4v26H46Z" fill="none" stroke="#8fa56b" stroke-width="1.2"/><path d="M-4 39C15 31 23 19 34 21c11 2 15 12 34-4" fill="none" stroke="#8bc9c4" stroke-width="3"/><path d="M-4 39C15 31 23 19 34 21c11 2 15 12 34-4" fill="none" stroke="#e8df9c" stroke-width="1"/></svg>`;
        case 'tianditu-terrain':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#ded8b7"/><path d="M-7 39C8 18 20 11 34 15c12 3 17 15 37 5" fill="none" stroke="#9c8b5f" stroke-width="1.5"/><path d="M-6 45C10 25 21 18 34 21c12 3 18 15 36 10" fill="none" stroke="#aa986b" stroke-width="1.25"/><path d="M5 49c11-15 20-21 30-20 11 1 17 11 27 11" fill="none" stroke="#b7a779" stroke-width="1"/><path d="M4 4c12 9 19 11 27 6 9-6 17-6 30 3" fill="none" stroke="#7f9f7b" stroke-width="2.4"/><path d="m33 15 5 9H28Z" fill="#766445"/></svg>`;
        case 'custom-xyz':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#dcebe2"/><path d="M0 13h64M0 34h64M17 0v48M45 0v48" stroke="#aac7b7" stroke-width="1"/><path d="M-6 41C12 30 22 17 34 18c10 1 18 12 36-8" fill="none" stroke="#3f8c69" stroke-width="4"/><circle cx="34" cy="18" r="3.5" fill="#f4c968" stroke="#fff" stroke-width="1.5"/></svg>`;
        case 'custom-tms':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#ebe3cf"/><path d="M8 6h17v15H8zM39 6h17v15H39zM8 27h17v15H8zM39 27h17v15H39z" fill="#d8c89e" stroke="#9c8962"/><path d="m32 9 5 6h-3v18h3l-5 6-5-6h3V15h-3Z" fill="#6f947d"/></svg>`;
        case 'custom-arcgis':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#dce7ef"/><path d="M7 36 21 12l11 18L43 7l14 29Z" fill="#6d9a86" opacity=".78"/><path d="M5 39h54" stroke="#426f87" stroke-width="2"/><circle cx="44" cy="13" r="6" fill="none" stroke="#f2b84b" stroke-width="2"/><path d="m48 17 6 6" stroke="#f2b84b" stroke-width="2"/></svg>`;
        case 'custom-wms':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#dfe8ec"/><path d="M7 10h35v24H7z" fill="#b8d3c5" stroke="#5f8975"/><path d="M15 17c7-7 15 9 23 0v11c-8 9-16-8-23 0Z" fill="#5f9eb1" opacity=".85"/><path d="m38 31 9 9 11-18" fill="none" stroke="#d2a847" stroke-width="4"/></svg>`;
        case 'custom-wmts':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#e1e8dc"/><g fill="#aac5b3" stroke="#668774"><path d="M7 6h15v15H7zM25 6h15v15H25zM43 6h14v15H43zM7 24h15v18H7zM25 24h15v18H25zM43 24h14v18H43z"/></g><path d="M11 35c11-11 19-5 27-14 6-6 11-5 19-10" fill="none" stroke="#f5e8bd" stroke-width="3"/></svg>`;
        case 'custom-pmtiles':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" rx="7" fill="#193342"/><path d="M7 11h22v14H7zM35 7h22v14H35zM10 30h19v11H10zM35 27h22v14H35z" fill="#315464" stroke="#7894a0" stroke-width=".8"/><path d="M-4 38C9 32 15 19 27 20c11 1 15 10 24 7 7-2 10-9 17-11" fill="none" stroke="#63c6aa" stroke-width="3.1"/><path d="M4 42C17 35 21 24 31 25c10 1 16 8 29-2" fill="none" stroke="#f2bc72" stroke-width="1.4"/><circle cx="49" cy="13" r="4.5" fill="#e9f2ee"/><path d="M47 13h4M49 11v4" stroke="#315464" stroke-width="1.2"/></svg>`;
        case 'custom-cog':
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><defs><linearGradient id="cog-g" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#17343c"/><stop offset=".52" stop-color="#27685f"/><stop offset="1" stop-color="#d6a960"/></linearGradient></defs><rect width="64" height="48" rx="7" fill="url(#cog-g)"/><path d="M-5 39C8 28 18 33 28 22S45 6 69 13" fill="none" stroke="#d9f0d5" stroke-opacity=".78" stroke-width="2.2"/><path d="M-4 44C11 34 20 39 31 28S49 12 68 19" fill="none" stroke="#f2cf83" stroke-opacity=".8" stroke-width="1.2"/><g fill="none" stroke="#f4faf6" stroke-width="1.1"><path d="M9 9h13v10H9zM26 9h13v10H26zM43 9h12v10H43zM9 23h13v10H9z"/></g><circle cx="49" cy="34" r="7" fill="#102f35" fill-opacity=".78"/><path d="M46 34h6M49 31v6" stroke="#eaf7f1" stroke-width="1.4"/></svg>`;
        default:
          return `<svg viewBox="0 0 64 48" aria-hidden="true"><rect width="64" height="48" fill="#dfe8e2"/><path d="M-4 39C12 23 25 17 39 20C49 22 57 17 68 7" fill="none" stroke="#5f9278" stroke-width="4"/></svg>`;
      }
    }
    function setBasemapVisual(element, meta) {
      if (!element || !meta) return;
      if (element.dataset.thumb) element.classList.remove(element.dataset.thumb);
      element.dataset.thumb = meta.thumb || 'custom-xyz';
      element.classList.add(element.dataset.thumb);
      element.innerHTML = basemapThumbSvg(meta);
    }
    function setActiveBadgeLabel(label) {
      const badge = $('active-layer-badge');
      if (!badge) return;
      badge.dataset.activeLabel = label;
      const sourceHint = t('source.trigger');
      const modeHint = measureMode ? t('tool.measureActive') : '';
      const hints = [sourceHint, modeHint].filter(Boolean).join(' · ');
      badge.title = `${label} · ${hints}`;
      badge.setAttribute('aria-label', `${hints} · ${label}`);
    }
    function formatBasemapDuration(value) {
      const milliseconds = Number(value);
      if (!Number.isFinite(milliseconds) || milliseconds < 0) return '-';
      if (milliseconds < 1000) return `${Math.round(milliseconds)} ms`;
      return `${(milliseconds / 1000).toFixed(milliseconds < 10000 ? 1 : 0).replace(/[.]0$/, '')} s`;
    }
    function formatBasemapBytes(value) {
      const bytes = Number(value);
      if (!Number.isFinite(bytes) || bytes < 0) return '-';
      if (bytes < 1024) return `${Math.round(bytes)} B`;
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(bytes < 10240 ? 1 : 0).replace(/[.]0$/, '')} KB`;
      return `${(bytes / (1024 * 1024)).toFixed(bytes < 10 * 1024 * 1024 ? 1 : 0).replace(/[.]0$/, '')} MB`;
    }
    function basemapCacheLabel(cache) {
      if (cache === 'cold') return t('source.cacheCold');
      if (cache === 'warm') return t('source.cacheWarm');
      return t('source.cacheUnknown');
    }
    function renderBasemapPerformanceDetails(meta) {
      const diagnostics = publicBasemapPerformance(meta);
      const performanceTarget = $('basemap-source-performance');
      const deliveryTarget = $('basemap-source-delivery');
      if (!diagnostics) {
        performanceTarget.textContent = t('source.performanceIdle');
        deliveryTarget.textContent = t('source.deliveryIdle');
        return;
      }
      const first = Number.isFinite(diagnostics.firstRenderMs) ? formatBasemapDuration(diagnostics.firstRenderMs) : null;
      const ready = Number.isFinite(diagnostics.readyMs) ? formatBasemapDuration(diagnostics.readyMs) : null;
      if (diagnostics.status === 'error') performanceTarget.textContent = t('source.performanceFailed');
      else if (ready) performanceTarget.textContent = t('source.performanceReady', { first: first || ready, ready });
      else if (first) performanceTarget.textContent = t('source.performanceSettling', { first });
      else performanceTarget.textContent = t('source.performanceLoading');

      const cache = basemapCacheLabel(diagnostics.cache);
      if (diagnostics.status === 'loading') {
        deliveryTarget.textContent = t('source.deliveryLoading', { cache });
        return;
      }
      const delivery = [cache];
      if (Number.isFinite(diagnostics.renderedBlocks) && diagnostics.renderedBlocks > 0) {
        delivery.push(t('source.renderedBlocks', { count: diagnostics.renderedBlocks }));
      }
      if (Number.isFinite(diagnostics.sourceRequests)) {
        delivery.push(t('source.sourceRequests', { count: diagnostics.sourceRequests }));
      }
      if (Number.isFinite(diagnostics.transferredBytes)) delivery.push(formatBasemapBytes(diagnostics.transferredBytes));
      else delivery.push(t('source.networkRestricted'));
      deliveryTarget.textContent = delivery.join(' · ');
    }
    function renderBasemapSourceDetails() {
      const meta = (basemapSourceDetailId && BASEMAPS.find(item => item.id === basemapSourceDetailId)) || currentBasemapMeta();
      setBasemapVisual($('basemap-source-visual'), meta);
      $('basemap-source-name').textContent = basemapDisplayName(meta);
      $('basemap-source-service').textContent = meta.serviceKey ? t(meta.serviceKey) : (meta.service || basemapDisplayNote(meta));
      $('basemap-source-provider').textContent = meta.provider || basemapAttributionText(meta);
      $('basemap-source-engine').textContent = basemapEngineLabel(meta);
      renderBasemapPerformanceDetails(meta);
      const dateRow = $('basemap-source-date-row');
      const hasDate = Boolean(meta.sourceDate);
      dateRow.hidden = !hasDate;
      $('basemap-source-date').textContent = hasDate ? meta.sourceDate : '';
      const nativeZoom = Number(meta.options?.maxNativeZoom ?? meta.options?.maxZoom);
      $('basemap-source-zoom').textContent = Number.isFinite(nativeZoom)
        ? t('source.nativeZoomValue', { zoom: nativeZoom })
        : '-';
      $('basemap-source-attribution').textContent = basemapAttributionText(meta) || '-';
      const sourceLink = $('basemap-source-link');
      sourceLink.href = meta.sourceUrl || '#';
      sourceLink.hidden = !meta.sourceUrl;
    }
    function setBasemapSourceOpen(open, sourceId = null) {
      basemapSourceOpen = Boolean(open);
      basemapSourceDetailId = basemapSourceOpen ? String(sourceId || currentBasemap) : null;
      const card = $('basemap-source-card');
      const badge = $('active-layer-badge');
      card.classList.toggle('open', basemapSourceOpen);
      card.setAttribute('aria-hidden', basemapSourceOpen ? 'false' : 'true');
      badge.setAttribute('aria-expanded', basemapSourceOpen ? 'true' : 'false');
      badge.classList.toggle('source-open', basemapSourceOpen);
      if (basemapSourceOpen) {
        renderBasemapSourceDetails();
        revealActiveBadge(0);
      } else {
        collapseActiveBadge();
      }
    }
    function basemapAttributionText(meta = currentBasemapMeta()) {
      const holder = document.createElement('span');
      holder.innerHTML = String((meta.options && meta.options.attribution) || '');
      return (holder.textContent || holder.innerText || '').replace(/\s+/g, ' ').trim();
    }
    function basemapEngineLabel(meta) {
      const type = String(meta?.type || 'xyz').toLowerCase();
      if (meta?.custom && type === 'pmtiles') return 'PMTiles __EASYGEE_PMTILES_VERSION__ · HTTP Range';
      if (meta?.custom && type === 'cog') return 'MapLibre __EASYGEE_MAPLIBRE_VERSION__ · COG __EASYGEE_COG_PROTOCOL_VERSION__ · WebGL / HTTP Range';
      if (meta?.custom) return `Leaflet · ${type.toUpperCase()}`;
      return 'Leaflet · XYZ tiles';
    }
    function displayBasemapSource() {
      const attribution = basemapAttributionText();
      const name = displayBasemapName();
      return attribution ? `${name} - ${attribution}` : name;
    }
    function compactBasemapBadge() {
      return t('badge.basemap', { basemap: displayBasemapName() });
    }
    function fullBasemapBadge() {
      return t('badge.basemapSource', { source: displayBasemapSource() });
    }
    function layerBadgeDataset(dataset) {
      return `${dataset} · ${compactBasemapBadge()}`;
    }
    function layerBadgeTitle(name, dataset) {
      return `${name} - ${dataset} | ${fullBasemapBadge()}`;
    }
    function renderBasemapChoices() {
      const current = $('basemap-current');
      if (current) current.textContent = displayBasemapName();
      const count = $('basemap-custom-count');
      if (count) count.textContent = t('basemap.customCount', { count: customBasemaps.length });
      const list = $('basemap-list');
      if (list) {
        list.innerHTML = BASEMAPS.map(meta => {
          const customIndex = customBasemaps.findIndex(item => item.id === meta.id);
          const isCustom = customIndex >= 0;
          const isDefault = meta.id === defaultBasemapId;
          const hasOverlay = STATE.layers.some(layer => isBasemapOverlayLayer(layer) && layer.sourceId === meta.id);
          const overlayLabel = t(hasOverlay ? 'basemap.overlayInLayers' : 'basemap.addOverlay');
          const overlayAction = `<button class="basemap-overlay-add" data-basemap-overlay="${escapeHtml(meta.id)}" type="button" title="${escapeHtml(overlayLabel)}" aria-label="${escapeHtml(overlayLabel)}" ${hasOverlay ? 'disabled' : ''}>__EASYGEE_ICON_OVERLAY_ADD__<span>${escapeHtml(overlayLabel)}</span></button>`;
          const customActions = isCustom ? `
            <div class="basemap-custom-actions">
              <button class="basemap-entry-action" data-basemap-up="${escapeHtml(meta.id)}" type="button" title="${escapeHtml(t('basemap.moveUp'))}" aria-label="${escapeHtml(t('basemap.moveUp'))}" ${customIndex === 0 ? 'disabled' : ''}>__EASYGEE_ICON_UP__</button>
              <button class="basemap-entry-action" data-basemap-down="${escapeHtml(meta.id)}" type="button" title="${escapeHtml(t('basemap.moveDown'))}" aria-label="${escapeHtml(t('basemap.moveDown'))}" ${customIndex === customBasemaps.length - 1 ? 'disabled' : ''}>__EASYGEE_ICON_DOWN__</button>
              <button class="basemap-entry-action" data-basemap-edit="${escapeHtml(meta.id)}" type="button" title="${escapeHtml(t('basemap.edit'))}" aria-label="${escapeHtml(t('basemap.edit'))}">__EASYGEE_ICON_EDIT__</button>
              <button class="basemap-entry-action danger" data-basemap-remove="${escapeHtml(meta.id)}" type="button" title="${escapeHtml(t('basemap.remove'))}" aria-label="${escapeHtml(t('basemap.remove'))}">__EASYGEE_ICON_TRASH__</button>
            </div>` : '';
          return `
            <div class="basemap-entry ${meta.id === currentBasemap ? 'active' : ''}">
              <button class="basemap-entry-default ${isDefault ? 'active' : ''}" data-basemap-default="${escapeHtml(meta.id)}" type="button" title="${escapeHtml(t(isDefault ? 'basemap.defaultCurrent' : 'basemap.defaultTitle'))}" aria-label="${escapeHtml(t(isDefault ? 'basemap.defaultCurrent' : 'basemap.defaultTitle'))}">__EASYGEE_ICON_FAVORITE__</button>
              <button class="basemap-choice" data-basemap="${escapeHtml(meta.id)}" type="button">
                <span class="basemap-thumb ${escapeHtml(meta.thumb)}" aria-hidden="true">${basemapThumbSvg(meta)}</span>
                <span class="basemap-copy">
                  <span class="basemap-name">${escapeHtml(basemapDisplayName(meta))}</span>
                  <span class="basemap-note">${escapeHtml(basemapDisplayNote(meta))}</span>
                  ${isCustom ? `<span class="basemap-type-chip">${escapeHtml(String(meta.type || 'xyz'))}</span>` : ''}
                </span>
              </button>
              <div class="basemap-entry-footer">${overlayAction}${customActions}</div>
            </div>`;
        }).join('');
        list.querySelectorAll('.basemap-choice').forEach(button => {
          button.addEventListener('click', () => {
            if (setBasemap(button.dataset.basemap)) {
              document.querySelector('.basemap-panel').classList.remove('open');
              syncToolState();
            }
          });
        });
        list.querySelectorAll('[data-basemap-overlay]').forEach(button => {
          button.addEventListener('click', () => addBasemapOverlay(button.dataset.basemapOverlay));
        });
        list.querySelectorAll('[data-basemap-default]').forEach(button => {
          button.addEventListener('click', () => setDefaultBasemap(button.dataset.basemapDefault));
        });
        list.querySelectorAll('[data-basemap-edit]').forEach(button => {
          button.addEventListener('click', () => openBasemapEditor(button.dataset.basemapEdit));
        });
        list.querySelectorAll('[data-basemap-up]').forEach(button => {
          button.addEventListener('click', () => moveCustomBasemap(button.dataset.basemapUp, -1));
        });
        list.querySelectorAll('[data-basemap-down]').forEach(button => {
          button.addEventListener('click', () => moveCustomBasemap(button.dataset.basemapDown, 1));
        });
        list.querySelectorAll('[data-basemap-remove]').forEach(button => {
          button.addEventListener('click', () => removeCustomBasemap(button.dataset.basemapRemove));
        });
      }
      const title = `${t('tool.basemap')} - ${displayBasemapName()}`;
      $('basemap-btn').title = title;
      $('basemap-btn').setAttribute('aria-label', title);
      renderBasemapSourceDetails();
    }
    function createCustomBasemapId(name) {
      const slug = String(name || 'basemap').trim().toLowerCase().replace(/[^a-z0-9一-鿿]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48) || 'basemap';
      const base = customBasemapIdentifier(`custom-${slug}`);
      let candidate = base;
      let suffix = 2;
      while (customBasemaps.some(meta => meta.id === candidate)) {
        candidate = `${base.slice(0, 70)}-${suffix}`;
        suffix += 1;
      }
      return candidate;
    }
    function setBasemapFormStatus(key = '', vars = {}, tone = '') {
      const status = $('basemap-form-status');
      if (!status) return;
      status.textContent = key ? t(key, vars) : '';
      status.className = `basemap-form-status${tone ? ` ${tone}` : ''}`;
    }
    function updateBasemapTypeFields() {
      const type = String($('basemap-form-type')?.value || 'xyz');
      document.querySelectorAll('.basemap-type-field').forEach(field => {
        const supported = String(field.dataset.basemapTypes || '').split(',');
        field.hidden = !supported.includes(type);
      });
      const url = $('basemap-form-url');
      if (url) url.placeholder = type === 'arcgis'
        ? 'https://.../ArcGIS/rest/services/.../MapServer'
        : type === 'wms'
          ? 'https://.../wms'
          : type === 'wmts'
            ? 'https://.../wmts'
            : type === 'pmtiles'
              ? 'https://.../imagery.pmtiles'
              : type === 'cog'
                ? 'https://.../imagery-cog.tif'
              : 'https://.../{z}/{x}/{y}.png';
    }
    function closeBasemapEditor() {
      const editor = $('basemap-editor');
      if (editor) editor.hidden = true;
      basemapEditorId = null;
      testedBasemapSignature = '';
      testedCogDetails = null;
      if ($('basemap-save-btn')) $('basemap-save-btn').disabled = true;
      setBasemapFormStatus();
    }
    function openBasemapEditor(id = null) {
      const meta = id ? customBasemaps.find(item => item.id === id) : null;
      basemapEditorId = meta?.id || null;
      testedCogDetails = meta?.type === 'cog'
        ? { url: meta.url, bounds: meta.bounds, crs: meta.crs || 'EPSG:3857', bandCount: meta.bandCount || 0 }
        : null;
      $('basemap-editor').hidden = false;
      $('basemap-editor-title').textContent = t(meta ? 'basemap.editorEdit' : 'basemap.editorAdd');
      $('basemap-form-name').value = meta?.name || '';
      $('basemap-form-type').value = meta?.type || 'xyz';
      $('basemap-form-provider').value = meta?.provider || '';
      $('basemap-form-url').value = meta?.url || '';
      $('basemap-form-subdomains').value = meta?.subdomains || '';
      $('basemap-form-layers').value = meta?.layers || '';
      $('basemap-form-styles').value = meta?.styles || '';
      $('basemap-form-version').value = meta?.type === 'wms' && meta?.version === '1.1.1' ? '1.1.1' : '1.3.0';
      $('basemap-form-matrix-set').value = meta?.tileMatrixSet || 'GoogleMapsCompatible';
      $('basemap-form-matrix-prefix').value = meta?.matrixPrefix || '';
      $('basemap-form-format').value = meta?.format || 'image/png';
      $('basemap-form-attribution').value = meta?.attribution || '';
      $('basemap-form-source-url').value = meta?.sourceUrl || '';
      $('basemap-form-min-zoom').value = meta?.minZoom ?? 0;
      $('basemap-form-max-zoom').value = meta?.maxZoom ?? 19;
      $('basemap-form-native-zoom').value = meta?.maxNativeZoom ?? 19;
      $('basemap-form-default').checked = Boolean(meta && meta.id === defaultBasemapId);
      testedBasemapSignature = '';
      $('basemap-save-btn').disabled = true;
      setBasemapFormStatus();
      updateBasemapTypeFields();
      $('basemap-form-name').focus();
      $('basemap-editor').scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
    function readBasemapForm() {
      const type = String($('basemap-form-type').value || 'xyz').toLowerCase();
      const url = $('basemap-form-url').value;
      const cogDetails = type === 'cog' && testedCogDetails?.url === String(url || '').trim()
        ? testedCogDetails
        : {};
      return normalizeCustomBasemap({
        id: basemapEditorId || createCustomBasemapId($('basemap-form-name').value),
        name: $('basemap-form-name').value,
        type,
        provider: $('basemap-form-provider').value,
        url,
        subdomains: $('basemap-form-subdomains').value,
        layers: $('basemap-form-layers').value,
        styles: $('basemap-form-styles').value,
        version: type === 'wmts' ? '1.0.0' : $('basemap-form-version').value,
        tileMatrixSet: $('basemap-form-matrix-set').value,
        matrixPrefix: $('basemap-form-matrix-prefix').value,
        format: $('basemap-form-format').value,
        attribution: $('basemap-form-attribution').value,
        sourceUrl: $('basemap-form-source-url').value,
        minZoom: $('basemap-form-min-zoom').value,
        maxZoom: $('basemap-form-max-zoom').value,
        maxNativeZoom: $('basemap-form-native-zoom').value,
        ...cogDetails,
        transparent: true,
      });
    }
    function validHttpTemplate(value) {
      try {
        const parsed = new URL(String(value || '').replace(/\{[^}]+\}/g, 'tile'));
        return parsed.protocol === 'http:' || parsed.protocol === 'https:';
      } catch {
        return false;
      }
    }
    const SENSITIVE_URL_QUERY_NAMES = new Set(['access_key', 'access_token', 'accesskey', 'api_key', 'apikey', 'app_key', 'appkey', 'auth', 'authorization', 'client_secret', 'credential', 'key', 'passwd', 'password', 'private_key', 'secret', 'sig', 'signature', 'subscription_key', 'tk', 'token']);
    function sensitiveUrlParameterName(value) {
      const name = String(value || '').trim().toLowerCase().replace(/-/g, '_');
      return SENSITIVE_URL_QUERY_NAMES.has(name) || ['_credential', '_key', '_password', '_secret', '_signature', '_token'].some(suffix => name.endsWith(suffix));
    }
    function urlContainsCredentials(value) {
      const text = String(value || '').trim();
      if (!text) return false;
      try {
        const parsed = new URL(text.replace(/\{[^}]+\}/g, 'tile'));
        if (parsed.username || parsed.password) return true;
        const parameterNames = `${parsed.search.slice(1)}&${parsed.hash.slice(1)}`
          .split(/[&;]/)
          .map(part => part.split('=', 1)[0]);
        return parameterNames.some(raw => {
          let key = String(raw || '').replace(/\+/g, ' ');
          for (let count = 0; count < 2; count += 1) {
            try { key = decodeURIComponent(key); } catch { break; }
          }
          return sensitiveUrlParameterName(key);
        });
      } catch {
        return false;
      }
    }
    function validateBasemapForm(meta) {
      if (!String($('basemap-form-name').value || '').trim()) return 'basemap.nameRequired';
      const url = String($('basemap-form-url').value || '').trim();
      if (!url) return 'basemap.urlRequired';
      if (urlContainsCredentials(url) || urlContainsCredentials($('basemap-form-source-url').value)) return 'basemap.urlCredentialsBlocked';
      if (!meta || !validHttpTemplate(url)) return 'basemap.urlInvalid';
      if ((meta.type === 'xyz' || meta.type === 'tms') && !['{z}', '{x}', '{y}'].every(token => url.includes(token))) return 'basemap.urlInvalid';
      if ((meta.type === 'wms' || meta.type === 'wmts') && !meta.layers) return 'basemap.layersRequired';
      if (meta.type === 'wmts' && !meta.tileMatrixSet) return 'basemap.matrixRequired';
      return '';
    }
    function invalidateBasemapTest() {
      testedBasemapSignature = '';
      testedCogDetails = null;
      if ($('basemap-save-btn')) $('basemap-save-btn').disabled = true;
      setBasemapFormStatus();
    }
    function testBasemapLayer(meta) {
      return new Promise(resolve => {
        let layer = null;
        let finished = false;
        let errors = 0;
        const finish = (ok, key) => {
          if (finished) return;
          finished = true;
          window.clearTimeout(timer);
          window.setTimeout(() => {
            if (layer && map.hasLayer(layer)) map.removeLayer(layer);
          }, 0);
          resolve({ ok, key });
        };
        const timer = window.setTimeout(() => finish(false, 'basemap.tileTimeout'), meta.type === 'cog' ? 15000 : 8000);
        try {
          layer = createBasemapLayer(meta, { opacity: 0.001, maxZoom: Math.max(meta.maxZoom || 19, map.getZoom()), zIndex: -100 });
          layer.on('tileload', () => finish(true, 'basemap.testPassed'));
          layer.on('tileerror', () => {
            errors += 1;
            if (errors >= 4) finish(false, 'basemap.tileFailed');
          });
          layer.addTo(map);
        } catch {
          finish(false, 'basemap.tileFailed');
        }
      });
    }
    function currentViewTileCoordinates(zoom) {
      const pixelBounds = map.getPixelBounds();
      const min = pixelBounds.min.divideBy(256).floor();
      const max = pixelBounds.max.divideBy(256).floor();
      const worldWidth = Math.pow(2, zoom);
      const coordinates = [];
      const seen = new Set();
      for (let y = min.y; y <= max.y; y += 1) {
        if (y < 0 || y >= worldWidth) continue;
        for (let x = min.x; x <= max.x; x += 1) {
          const wrappedX = ((x % worldWidth) + worldWidth) % worldWidth;
          const key = `${zoom}/${wrappedX}/${y}`;
          if (!seen.has(key)) {
            seen.add(key);
            coordinates.push({ z: zoom, x: wrappedX, y });
          }
        }
      }
      return coordinates.slice(0, 64);
    }
    async function pmtilesHasVisibleRasterTile(archive, zoom) {
      const coordinates = currentViewTileCoordinates(zoom);
      if (!coordinates.length) return false;
      let cursor = 0;
      let found = false;
      const worker = async () => {
        while (!found && cursor < coordinates.length) {
          const coordinate = coordinates[cursor];
          cursor += 1;
          const tile = await archive.getZxy(coordinate.z, coordinate.x, coordinate.y);
          if (tile?.data?.byteLength > 0) found = true;
        }
      };
      await Promise.all(Array.from({ length: Math.min(4, coordinates.length) }, worker));
      return found;
    }
    async function inspectPmtilesArchive(meta, options = {}) {
      if (!window.pmtiles?.PMTiles || !window.pmtiles?.leafletRasterLayer) {
        return { ok: false, key: 'basemap.pmtilesUnavailable' };
      }
      let timeoutId = null;
      const timeout = new Promise(resolve => {
        timeoutId = window.setTimeout(() => resolve({ ok: false, key: 'basemap.pmtilesInspectFailed' }), 10000);
      });
      try {
        const archive = getPmtilesArchive(meta.url, { refresh: options.refresh === true });
        const inspection = (async () => {
          const header = await archive.getHeader();
          if (![2, 3, 4, 5].includes(Number(header?.tileType))) {
            return { ok: false, key: 'basemap.pmtilesRasterOnly' };
          }
          if (options.requireVisibleTile !== false) {
            const zoom = Math.round(map.getZoom());
            if (zoom < Number(header.minZoom) || zoom > Number(header.maxZoom)) {
              return { ok: false, key: 'basemap.pmtilesZoomOutside' };
            }
            const bounds = [header?.minLat, header?.minLon, header?.maxLat, header?.maxLon].map(Number);
            if (bounds.every(Number.isFinite)) {
              const coverage = L.latLngBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]]);
              if (!map.getBounds().intersects(coverage)) return { ok: false, key: 'basemap.pmtilesOutsideView' };
            }
            if (!await pmtilesHasVisibleRasterTile(archive, zoom)) {
              return { ok: false, key: 'basemap.pmtilesNoTile' };
            }
          }
          return { ok: true, header };
        })();
        const result = await Promise.race([inspection, timeout]);
        if (!result.ok) discardPmtilesArchive(meta.url);
        return result;
      } catch {
        discardPmtilesArchive(meta.url);
        return { ok: false, key: 'basemap.pmtilesInspectFailed' };
      } finally {
        if (timeoutId !== null) window.clearTimeout(timeoutId);
      }
    }
    async function inspectCogSource(meta, options = {}) {
      let timeoutId = null;
      const timeout = new Promise(resolve => {
        timeoutId = window.setTimeout(() => resolve({ ok: false, key: 'basemap.cogInspectFailed' }), 20000);
      });
      try {
        const inspection = (async () => {
          await ensureCogEngine();
          const metadata = await getCogSourceMetadata(meta.url, { refresh: options.refresh === true });
          const bounds = normalizeBasemapBounds(metadata?.bbox);
          const zooms = (Array.isArray(metadata?.images) ? metadata.images : [])
            .filter(image => !image?.isMask)
            .map(image => Number(image?.zoom))
            .filter(Number.isFinite);
          const maxZoom = zooms.length ? Math.max(...zooms) : Number(meta.maxNativeZoom || meta.maxZoom || 19);
          const bandCount = Array.isArray(metadata?.bitsPerSample) ? metadata.bitsPerSample.length : Number(meta.bandCount || 0);
          const details = {
            url: meta.url,
            ...(bounds ? { bounds } : {}),
            crs: 'EPSG:3857',
            bandCount,
            minZoom: 0,
            maxZoom: basemapZoom(maxZoom, 19),
            maxNativeZoom: basemapZoom(maxZoom, 19),
          };
          const checkedMeta = normalizeCustomBasemap({ ...meta, ...details });
          if (!checkedMeta) return { ok: false, key: 'basemap.cogInspectFailed' };
          if (options.requireVisibleTile !== false) {
            if (bounds) {
              const coverage = L.latLngBounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]]);
              if (!map.getBounds().intersects(coverage)) {
                if (options.fitBounds === false) return { ok: false, key: 'basemap.cogOutsideView' };
                await new Promise(resolve => {
                  let finished = false;
                  const finish = () => {
                    if (finished) return;
                    finished = true;
                    map.off('moveend', finish);
                    resolve();
                  };
                  map.once('moveend', finish);
                  map.fitBounds(coverage, { padding: [42, 42], maxZoom: Math.min(details.maxNativeZoom, 17) });
                  window.setTimeout(finish, 1400);
                });
              }
            }
            const tileResult = await testBasemapLayer(checkedMeta);
            if (!tileResult.ok) return tileResult;
          }
          return { ok: true, metadata, details, meta: checkedMeta };
        })();
        return await Promise.race([inspection, timeout]);
      } catch (error) {
        discardCogSource(meta.url);
        const message = String(error?.message || error || '').toLowerCase();
        const key = message.includes('3857') || message.includes('projection') || message.includes('projectedcstype')
          ? 'basemap.cogWebMercatorOnly'
          : cogEngineStatus === 'error'
            ? 'basemap.cogUnavailable'
            : 'basemap.cogInspectFailed';
        return { ok: false, key, error: message.slice(0, 200) };
      } finally {
        if (timeoutId !== null) window.clearTimeout(timeoutId);
      }
    }
    async function testBasemapForm() {
      let meta = readBasemapForm();
      const validationKey = validateBasemapForm(meta);
      testedBasemapSignature = '';
      $('basemap-save-btn').disabled = true;
      if (validationKey) {
        setBasemapFormStatus(validationKey, {}, 'error');
        return false;
      }
      $('basemap-test-btn').disabled = true;
      if (meta.type === 'pmtiles') {
        setBasemapFormStatus('basemap.pmtilesInspecting');
        const inspection = await inspectPmtilesArchive(meta, { refresh: true });
        if (!inspection.ok) {
          $('basemap-test-btn').disabled = false;
          setBasemapFormStatus('basemap.testFailed', { message: t(inspection.key) }, 'error');
          return false;
        }
        const minZoom = Number(inspection.header?.minZoom);
        const maxZoom = Number(inspection.header?.maxZoom);
        if (Number.isFinite(minZoom)) $('basemap-form-min-zoom').value = minZoom;
        if (Number.isFinite(maxZoom)) {
          $('basemap-form-max-zoom').value = maxZoom;
          $('basemap-form-native-zoom').value = maxZoom;
        }
        meta = readBasemapForm();
        testedBasemapSignature = customBasemapSignature(meta);
        $('basemap-test-btn').disabled = false;
        $('basemap-save-btn').disabled = false;
        setBasemapFormStatus('basemap.testPassed', {}, 'success');
        return true;
      }
      if (meta.type === 'cog') {
        setBasemapFormStatus(cogEngineStatus === 'idle' ? 'basemap.cogLoading' : 'basemap.cogInspecting');
        const inspection = await inspectCogSource(meta, { refresh: true, requireVisibleTile: true, fitBounds: true });
        if (!inspection.ok) {
          $('basemap-test-btn').disabled = false;
          setBasemapFormStatus('basemap.testFailed', { message: t(inspection.key) }, 'error');
          return false;
        }
        testedCogDetails = inspection.details;
        $('basemap-form-min-zoom').value = inspection.details.minZoom;
        $('basemap-form-max-zoom').value = inspection.details.maxZoom;
        $('basemap-form-native-zoom').value = inspection.details.maxNativeZoom;
        meta = readBasemapForm();
        testedBasemapSignature = customBasemapSignature(meta);
        $('basemap-test-btn').disabled = false;
        $('basemap-save-btn').disabled = false;
        setBasemapFormStatus('basemap.testPassed', {}, 'success');
        return true;
      }
      setBasemapFormStatus('basemap.testing');
      const result = await testBasemapLayer(meta);
      $('basemap-test-btn').disabled = false;
      if (result.ok) {
        testedBasemapSignature = customBasemapSignature(meta);
        $('basemap-save-btn').disabled = false;
        setBasemapFormStatus('basemap.testPassed', {}, 'success');
        return true;
      }
      setBasemapFormStatus('basemap.testFailed', { message: t(result.key) }, 'error');
      return false;
    }
    function saveBasemapForm() {
      const meta = readBasemapForm();
      const validationKey = validateBasemapForm(meta);
      if (validationKey) {
        setBasemapFormStatus(validationKey, {}, 'error');
        return false;
      }
      if (!testedBasemapSignature || testedBasemapSignature !== customBasemapSignature(meta)) {
        setBasemapFormStatus('basemap.testFirst', {}, 'error');
        $('basemap-save-btn').disabled = true;
        return false;
      }
      const editing = Boolean(basemapEditorId);
      const index = customBasemaps.findIndex(item => item.id === meta.id);
      const previous = index >= 0 ? customBasemaps[index] : null;
      if (previous?.type === 'pmtiles' && (meta.type !== 'pmtiles' || previous.url !== meta.url)) {
        discardPmtilesArchive(previous.url);
      }
      if (previous?.type === 'cog' && (meta.type !== 'cog' || previous.url !== meta.url)) discardCogSource(previous.url);
      if (index >= 0) customBasemaps.splice(index, 1, meta);
      else customBasemaps.push(meta);
      customBasemaps = normalizeCustomBasemaps(customBasemaps);
      if ($('basemap-form-default').checked) defaultBasemapId = meta.id;
      rebuildBasemapRegistry(meta.id);
      reloadBasemapOverlays(meta.id);
      closeBasemapEditor();
      showMode(t(editing ? 'basemap.updated' : 'basemap.saved', { name: meta.name }));
      syncSessionState(editing ? 'custom-basemap-updated' : 'custom-basemap-added');
      return true;
    }
    function setDefaultBasemap(id) {
      const meta = BASEMAPS.find(item => item.id === id);
      if (!meta) return false;
      if (isTiandituBasemap(meta) && !tiandituToken) return requestTiandituToken();
      defaultBasemapId = meta.id;
      renderBasemapChoices();
      showMode(t('basemap.defaultChanged', { name: basemapDisplayName(meta) }));
      syncSessionState('default-basemap-changed');
      return true;
    }
    function moveCustomBasemap(id, direction) {
      const index = customBasemaps.findIndex(meta => meta.id === id);
      const target = index + Number(direction || 0);
      if (index < 0 || target < 0 || target >= customBasemaps.length) return false;
      [customBasemaps[index], customBasemaps[target]] = [customBasemaps[target], customBasemaps[index]];
      rebuildBasemapRegistry(currentBasemap);
      syncSessionState('custom-basemap-reordered');
      return true;
    }
    function removeCustomBasemap(id, options = {}) {
      const meta = customBasemaps.find(item => item.id === id);
      if (!meta) return false;
      if (options.confirm !== false && !window.confirm(t('basemap.removeConfirm', { name: meta.name }))) return false;
      if (meta.type === 'pmtiles') discardPmtilesArchive(meta.url);
      if (meta.type === 'cog') discardCogSource(meta.url);
      STATE.layers.filter(layer => isBasemapOverlayLayer(layer) && layer.sourceId === id).forEach(layer => removeLayer(layer.id));
      customBasemaps = customBasemaps.filter(item => item.id !== id);
      if (defaultBasemapId === id) defaultBasemapId = 'OSM';
      if (basemapEditorId === id) closeBasemapEditor();
      rebuildBasemapRegistry(currentBasemap === id ? defaultBasemapId : currentBasemap);
      showMode(t('basemap.removed', { name: meta.name }));
      syncSessionState('custom-basemap-removed');
      return true;
    }
    function normalizeCatalogType(item) {
      const raw = String(item.type || item.scale || '').toLowerCase();
      if (raw.includes('image_collection') || raw.includes('image collection')) return 'image_collection';
      if (raw.includes('image')) return 'image';
      if (raw.includes('table') || raw.includes('feature') || raw.includes('vector')) return 'table';
      return 'other';
    }
    function catalogTypeLabel(type) {
      const labels = {
        all: 'catalog.typeAll',
        image_collection: 'catalog.typeImageCollection',
        image: 'catalog.typeImage',
        table: 'catalog.typeTable',
        other: 'catalog.typeOther',
      };
      return t(labels[type] || labels.other);
    }
    function catalogCategoryKey(item) {
      const raw = String(item.category || '').trim().toLowerCase();
      const categoryMap = {
        'satellite-imagery': 'imagery',
        imagery: 'imagery',
        orthophotos: 'imagery',
        radar: 'imagery',
        'analysis ready data': 'imagery',
        climate: 'climate-atmosphere',
        atmosphere: 'climate-atmosphere',
        precipitation: 'climate-atmosphere',
        'water-vapor': 'climate-atmosphere',
        'weather and climate layers': 'climate-atmosphere',
        'surface-ground-water': 'water-ocean',
        hydrology: 'water-ocean',
        water: 'water-ocean',
        ocean: 'water-ocean',
        oceans: 'water-ocean',
        'oceans and shorelines': 'water-ocean',
        'vegetation-indices': 'vegetation-ecosystems',
        'forest-biomass': 'vegetation-ecosystems',
        'plant-productivity': 'vegetation-ecosystems',
        ecosystems: 'vegetation-ecosystems',
        agriculture: 'vegetation-ecosystems',
        'agriculture and food security': 'vegetation-ecosystems',
        'agriculture vegetation and forestry': 'vegetation-ecosystems',
        'biodiversity ecosystems habitat layers': 'vegetation-ecosystems',
        'landuse-landcover': 'land-cover',
        'land-cover': 'land-cover',
        'land use land cover': 'land-cover',
        'regional land use and land cover': 'land-cover',
        'global land use and land cover': 'land-cover',
        'elevation-topography': 'terrain',
        elevation: 'terrain',
        topography: 'terrain',
        bathymetry: 'terrain',
        'elevation and bathymetry': 'terrain',
        'terrain and topography': 'terrain',
        population: 'human-built',
        'infrastructure-boundaries': 'human-built',
        'population-built': 'human-built',
        'infrastructure and boundaries': 'human-built',
        'population socioeconomic': 'human-built',
        'global utilities assets and amenities layers': 'human-built',
        soil: 'soil-geology',
        soils: 'soil-geology',
        geology: 'soil-geology',
        'soil properties': 'soil-geology',
        'geophysical biological biogeochemical': 'soil-geology',
        fire: 'hazards',
        disasters: 'hazards',
        'fire monitoring and analysis': 'hazards',
        'global events layers': 'hazards',
        cryosphere: 'cryosphere',
        other: 'other',
      };
      const priority = [
        'imagery',
        'climate-atmosphere',
        'water-ocean',
        'vegetation-ecosystems',
        'land-cover',
        'terrain',
        'human-built',
        'soil-geology',
        'hazards',
        'cryosphere',
        'other',
      ];
      if (raw) {
        const compactRaw = raw.replace(/&/g, 'and').replace(/[^a-z0-9]+/g, ' ').trim();
        const groups = raw
          .split(',')
          .map(part => part.trim())
          .filter(Boolean)
          .map(part => {
            const compactPart = part.replace(/&/g, 'and').replace(/[^a-z0-9]+/g, ' ').trim();
            return categoryMap[part] || categoryMap[compactPart] || '';
          })
          .filter(Boolean);
        const direct = categoryMap[raw] || categoryMap[compactRaw] || priority.find(group => groups.includes(group));
        if (direct && direct !== 'other') return direct;
      }
      const haystack = datasetSearchText(item);
      if (/(climate|weather|temperature|precipitation|rain|era5|chirps|atmosphere|aerosol|ozone|water vapor)/.test(haystack)) return 'climate-atmosphere';
      if (/(water|hydro|flood|ocean|surface-ground-water|marine)/.test(haystack)) return 'water-ocean';
      if (/(ndvi|evi|vegetation|forest|biomass|ecosystem|crop|agriculture|productivity)/.test(haystack)) return 'vegetation-ecosystems';
      if (/(landcover|land cover|landuse|dynamic world|worldcover)/.test(haystack)) return 'land-cover';
      if (/(elevation|dem|terrain|topography|srtm)/.test(haystack)) return 'terrain';
      if (/(population|building|built|ghsl|worldpop|infrastructure|boundary|boundaries)/.test(haystack)) return 'human-built';
      if (/(soil|geology|geologic)/.test(haystack)) return 'soil-geology';
      if (/(fire|hazard|flood|disaster|burn)/.test(haystack)) return 'hazards';
      if (/(ice|snow|glacier|cryosphere)/.test(haystack)) return 'cryosphere';
      if (/(sentinel|landsat|modis|viirs|satellite-imagery|imagery|radar|sar|orthophoto)/.test(haystack)) return 'imagery';
      return 'other';
    }
    function catalogCategoryLabel(key) {
      const zh = {
        all: '全部',
        imagery: '遥感影像',
        'climate-atmosphere': '气候与大气',
        'water-ocean': '水文与海洋',
        'vegetation-ecosystems': '植被与生态',
        'land-cover': '土地覆盖',
        terrain: '高程地形',
        'human-built': '人口与基础设施',
        'soil-geology': '土壤与地质',
        hazards: '灾害与火灾',
        cryosphere: '冰冻圈',
        other: '其他',
      };
      const en = {
        all: 'All',
        imagery: 'Remote sensing imagery',
        'climate-atmosphere': 'Climate and atmosphere',
        'water-ocean': 'Hydrology and ocean',
        'vegetation-ecosystems': 'Vegetation and ecosystems',
        'land-cover': 'Land cover',
        terrain: 'Elevation and terrain',
        'human-built': 'Population and infrastructure',
        'soil-geology': 'Soil and geology',
        hazards: 'Hazards and fire',
        cryosphere: 'Cryosphere',
        other: 'Other',
      };
      const table = currentLang === 'zh' ? zh : en;
      if (table[key]) return table[key];
      if (currentLang === 'zh') return table.other;
      return String(key || 'other').split(/[-_]/).map(part => part ? part[0].toUpperCase() + part.slice(1) : part).join(' ');
    }
    function datasetSearchText(item) {
      return `${item.id || ''} ${item.label || ''} ${item.tags || ''} ${item.description || ''} ${item.scale || ''} ${item.provider || ''} ${item.type || ''} ${item.category || ''} ${item.license || ''}`.toLowerCase();
    }
    function catalogSourceLabel(item) {
      const source = String(item.source || '').toLowerCase();
      if (source === 'community') return t('catalog.sourceCommunity');
      if (source === 'curated') return t('catalog.sourceCurated');
      return t('catalog.sourceOfficial');
    }
    function expandedDatasetTerms(query) {
      const lower = query.trim().toLowerCase();
      if (!lower) return [];
      const expanded = [lower];
      Object.entries(DATASET_QUERY_ALIASES).forEach(([term, aliases]) => {
        if (lower.includes(term)) expanded.push(aliases);
      });
      return expanded.join(' ').split(/[\s,，;；|]+/).map(term => term.trim()).filter(Boolean);
    }
    function searchMatchedCatalog() {
      const query = $('dataset-search').value.trim().toLowerCase();
      const catalog = Array.isArray(STATE.catalog) ? STATE.catalog : [];
      const terms = expandedDatasetTerms(query);
      if (!terms.length) return catalog;
      return catalog
        .map(item => {
          const haystack = datasetSearchText(item);
          const score = terms.reduce((total, term) => total + (haystack.includes(term) ? (haystack.includes(`${term}/`) || haystack.includes(`/${term}`) ? 3 : 1) : 0), 0);
          return { item, score };
        })
        .filter(record => record.score > 0)
        .sort((a, b) => b.score - a.score || String(a.item.label || a.item.id).localeCompare(String(b.item.label || b.item.id)))
        .map(record => record.item);
    }
    function filteredCatalog() {
      return searchMatchedCatalog()
        .filter(item => !catalogFavoriteFilter || isFavoriteDataset(item.id))
        .filter(item => catalogTypeFilter === 'all' || normalizeCatalogType(item) === catalogTypeFilter)
        .filter(item => catalogCategoryFilter === 'all' || catalogCategoryKey(item) === catalogCategoryFilter);
    }
    function renderCatalogFacets() {
      const searchItems = searchMatchedCatalog();
      const favoriteCount = favoriteCatalogItems(searchItems).length;
      const facetItems = catalogFavoriteFilter ? favoriteCatalogItems(searchItems) : searchItems;
      const typeCounts = facetItems.reduce((counts, item) => {
        const type = normalizeCatalogType(item);
        counts[type] = (counts[type] || 0) + 1;
        counts.all = (counts.all || 0) + 1;
        return counts;
      }, {});
      const typeOrder = ['all', 'image_collection', 'image', 'table', 'other'];
      const favoriteChip = `
            <button class="type-chip favorite-chip ${catalogFavoriteFilter ? 'active' : ''}" data-favorite-filter="true" type="button">
              ${escapeHtml(t('catalog.favoriteChip', { count: favoriteCount }))}
            </button>
          `;
      $('type-chip-list').innerHTML = favoriteChip + typeOrder
        .filter(type => type === 'all' || typeCounts[type])
        .map(type => {
          const label = type === 'all'
            ? catalogTypeLabel(type)
            : `${catalogTypeLabel(type)} (${typeCounts[type] || 0})`;
          return `
            <button class="type-chip ${catalogTypeFilter === type ? 'active' : ''}" data-type="${escapeHtml(type)}" type="button">
              ${escapeHtml(label)}
            </button>
          `;
        }).join('');
      document.querySelectorAll('.type-chip').forEach(button => {
        button.addEventListener('click', () => {
          if (button.dataset.favoriteFilter) {
            catalogFavoriteFilter = !catalogFavoriteFilter;
            renderDatasets(filteredCatalog());
            return;
          }
          catalogTypeFilter = button.dataset.type;
          renderDatasets(filteredCatalog());
        });
      });

      const categoryBase = facetItems.filter(item => catalogTypeFilter === 'all' || normalizeCatalogType(item) === catalogTypeFilter);
      const categoryCounts = categoryBase.reduce((counts, item) => {
        const category = catalogCategoryKey(item);
        counts[category] = (counts[category] || 0) + 1;
        counts.all = (counts.all || 0) + 1;
        return counts;
      }, {});
      const query = catalogCategoryQuery.trim().toLowerCase();
      const categories = Object.entries(categoryCounts)
        .filter(([category]) => category === 'all' || !query || catalogCategoryLabel(category).toLowerCase().includes(query) || category.includes(query))
        .sort((a, b) => a[0] === 'all' ? -1 : b[0] === 'all' ? 1 : b[1] - a[1] || catalogCategoryLabel(a[0]).localeCompare(catalogCategoryLabel(b[0])));
      const favoriteCategory = !query || t('catalog.favorites').toLowerCase().includes(query) || 'favorites'.includes(query)
        ? `
        <button class="category-button favorite-filter ${catalogFavoriteFilter ? 'active' : ''}" data-favorite-category="true" type="button">
          <span>${escapeHtml(t('catalog.favorites'))}</span><span class="category-count">${favoriteCount}</span>
        </button>
      `
        : '';
      $('category-list').innerHTML = favoriteCategory + categories.map(([category, count]) => `
        <button class="category-button ${!catalogFavoriteFilter && catalogCategoryFilter === category ? 'active' : ''}" data-category="${escapeHtml(category)}" type="button">
          <span>${escapeHtml(catalogCategoryLabel(category))}</span><span class="category-count">${count}</span>
        </button>
      `).join('');
      document.querySelectorAll('.category-button').forEach(button => {
        button.addEventListener('click', () => {
          if (button.dataset.favoriteCategory) {
            catalogFavoriteFilter = true;
            catalogTypeFilter = 'all';
            catalogCategoryFilter = 'all';
            renderDatasets(filteredCatalog());
            return;
          }
          catalogFavoriteFilter = false;
          catalogCategoryFilter = button.dataset.category;
          renderDatasets(filteredCatalog());
        });
      });
    }
    function datasetLayerIds(datasetId) {
      return STATE.layers.filter(layer => layer.dataset === datasetId).map(layer => layer.id);
    }
    function datasetById(datasetId) {
      return (Array.isArray(STATE.catalog) ? STATE.catalog : []).find(item => item.id === datasetId) || null;
    }
    function defaultPreviewRecipeForDataset(item) {
      const datasetId = String(item?.id || '');
      const type = normalizeCatalogType(item || {});
      let operation = type === 'image_collection' ? 'imagecollection-median' : (type === 'image' ? 'image' : 'preview');
      const recipe = {
        kind: 'preview',
        source: 'map-console-default-preview',
        datasetId,
        label: item?.label || datasetId,
        operation,
        startDate: STATE.startDate,
        endDate: STATE.endDate,
        aoi: hasAoi() ? 'currentAOI' : 'currentMapBounds',
        description: 'Default quick-preview recipe. Use an explicit recipe for analytical requests.',
      };
      if (datasetId === 'MODIS/061/MOD13Q1') {
        Object.assign(recipe, { band: 'NDVI', temporalReducer: 'median', scaleFactor: 0.0001, outputBand: 'NDVI' });
      } else if (datasetId === 'MODIS/061/MOD11A2') {
        Object.assign(recipe, { band: 'LST_Day_1km', temporalReducer: 'median', scaleFactor: 0.02, offset: -273.15, outputBand: 'LST_Day_C' });
      } else if (datasetId === 'GOOGLE/DYNAMICWORLD/V1') {
        Object.assign(recipe, { band: 'label', temporalReducer: 'mode', outputBand: 'label' });
      } else if (datasetId === 'COPERNICUS/S2_SR_HARMONIZED') {
        Object.assign(recipe, { bands: ['B4', 'B3', 'B2'], temporalReducer: 'median', output: 'rgb' });
      }
      return recipe;
    }
    function datasetContext(item) {
      if (!item) return null;
      const explicitAoi = hasAoi() ? cloneAoi(STATE.aoi) : null;
      const processingAoi = currentProcessingAoi();
      const processingBounds = processingAoi ? processingAoi.bounds : null;
      return {
        id: item.id,
        label: item.label || item.id,
        type: normalizeCatalogType(item),
        source: item.source || '',
        provider: datasetDetailValue(item.provider),
        license: datasetDetailValue(item.license),
        scale: datasetDetailValue(item.scale),
        dateRange: datasetDateText(item),
        startDate: datasetDetailValue(item.startDate),
        endDate: datasetDetailValue(item.endDate),
        tags: datasetDetailValue([item.category, item.tags].filter(Boolean).join(' · ')),
        catalogUrl: datasetDetailValue(item.url),
        sampleCode: datasetDetailValue(item.sampleCode),
        currentAoi: explicitAoi,
        currentBounds: processingBounds,
        hasExplicitAoi: Boolean(explicitAoi),
        processingAoi,
        processingBounds,
        mapDateRange: { startDate: STATE.startDate, endDate: STATE.endDate, cloudPct: STATE.cloudPct },
        defaultRecipe: defaultPreviewRecipeForDataset(item),
      };
    }
    function selectedDatasetContext() {
      return activeDatasetId ? datasetContext(datasetById(activeDatasetId)) : null;
    }
    function recipeSummary(recipe) {
      if (!recipe || typeof recipe !== 'object') return '-';
      const band = recipe.outputBand || recipe.band || recipe.output || recipe.operation || recipe.kind || 'recipe';
      const reducer = recipe.temporalReducer || recipe.operation || '';
      const period = recipe.periodLabel || (recipe.year && Array.isArray(recipe.months)
        ? `${recipe.year} months ${recipe.months.join(',')}`
        : [recipe.startDate, recipe.endDate].filter(Boolean).join('..'));
      return [band, reducer, period].filter(Boolean).join(' · ') || '-';
    }
    function datasetDetailValue(value) {
      const text = String(value || '').trim();
      if (!text || text.toLowerCase() === 'na' || text.toLowerCase() === 'none') return '';
      return text;
    }
    function datasetDateText(item) {
      const start = datasetDetailValue(item.startDate);
      const end = datasetDetailValue(item.endDate);
      if (start && end) return `${start} - ${end}`;
      return start || end || '';
    }
    function datasetDurationText(item) {
      const start = Date.parse(datasetDetailValue(item.startDate));
      const endText = datasetDetailValue(item.endDate);
      const end = endText ? Date.parse(endText) : Date.now();
      if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return '';
      const months = Math.max(1, Math.round((end - start) / (1000 * 60 * 60 * 24 * 30.4375)));
      if (months >= 24) return t('data.attrYear', { count: trimNumber((months / 12).toFixed(months >= 120 ? 0 : 1)) });
      return t('data.attrMonth', { count: months });
    }
    function datasetResolutionText(item) {
      const scale = datasetDetailValue(item.scale);
      if (!scale) return '';
      const lower = scale.toLowerCase();
      if (/^(image|image collection|table|feature|vector|catalog|ready layer|official catalog|community catalog)$/.test(lower)) return '';
      if (/\b(\d+(\.\d+)?\s*(m|meter|meters|km|kilometer|kilometers|deg|degree|degrees|arcsec|arc-second|arcseconds)|scale)\b/.test(lower)) return scale;
      return '';
    }
    function datasetAttr(labelKey, value) {
      const text = datasetDetailValue(value);
      if (!text) return '';
      return `<span class="dataset-attr"><strong>${escapeHtml(t(labelKey))}</strong> ${escapeHtml(text)}</span>`;
    }
    function datasetAttrsHtml(item, typeLabel) {
      const attrs = [
        datasetAttr('data.attrTime', datasetDateText(item)),
        datasetAttr('data.attrSpan', datasetDurationText(item)),
        datasetAttr('data.attrResolution', datasetResolutionText(item)),
        datasetAttr('data.attrType', typeLabel),
      ].filter(Boolean);
      return attrs.length ? `<div class="dataset-attrs">${attrs.join('')}</div>` : '';
    }
    function datasetDetailSection(labelKey, value) {
      const text = datasetDetailValue(value);
      if (!text) return '';
      return `
        <section class="dataset-detail-section">
          <div class="dataset-detail-label">${escapeHtml(t(labelKey))}</div>
          <div class="dataset-detail-text">${escapeHtml(text)}</div>
        </section>
      `;
    }
    function datasetDetailHtml(item) {
      const typeLabel = catalogTypeLabel(normalizeCatalogType(item));
      const sourceLabel = catalogSourceLabel(item);
      const category = catalogCategoryLabel(catalogCategoryKey(item));
      const license = datasetDetailValue(item.license);
      const provider = datasetDetailValue(item.provider);
      const dates = datasetDateText(item);
      const description = datasetDetailValue(item.description) || t('data.detailNoDescription');
      const tags = datasetDetailValue([item.category, item.tags].filter(Boolean).join(' · '));
      const thumb = datasetDetailValue(item.thumbnail);
      const catalogUrl = datasetDetailValue(item.url);
      const sampleCode = datasetDetailValue(item.sampleCode);
      const previewRecipe = recipeSummary(defaultPreviewRecipeForDataset(item));
      return `
        <div class="dataset-detail-head">
          <div>
            <div class="dataset-detail-title">${escapeHtml(item.label || item.id)}</div>
            <div class="dataset-detail-id">${escapeHtml(item.id || '')}</div>
          </div>
          <button class="dataset-detail-close" id="dataset-detail-close" title="${escapeHtml(t('tool.close'))}" aria-label="${escapeHtml(t('tool.close'))}" type="button">&times;</button>
        </div>
        <div class="dataset-detail-body">
          ${thumb ? `<img class="dataset-detail-thumb" src="${escapeHtml(thumb)}" alt="">` : ''}
          <div class="dataset-detail-badges">
            <span class="dataset-detail-badge">${escapeHtml(sourceLabel)}</span>
            <span class="dataset-detail-badge">${escapeHtml(typeLabel)}</span>
            <span class="dataset-detail-badge">${escapeHtml(category)}</span>
            ${license ? `<span class="dataset-detail-badge">${escapeHtml(license)}</span>` : ''}
          </div>
          ${datasetDetailSection('data.detailDescription', description)}
          ${datasetDetailSection('data.detailProvider', provider)}
          ${datasetDetailSection('data.detailDates', dates)}
          ${datasetDetailSection('data.detailTags', tags)}
          ${datasetDetailSection('data.previewRecipe', previewRecipe)}
          <div class="dataset-detail-actions">
            <button class="dataset-detail-command primary" id="dataset-detail-add" type="button">${escapeHtml(t('data.addFromDetail'))}</button>
            <button class="dataset-detail-command" id="dataset-detail-copy" type="button">${escapeHtml(t('data.copyId'))}</button>
            <button class="dataset-detail-command" id="dataset-detail-copy-context" type="button">${escapeHtml(t('data.copyContext'))}</button>
            ${catalogUrl ? `<a class="dataset-detail-link" href="${escapeHtml(catalogUrl)}" target="_blank" rel="noreferrer">${escapeHtml(t('data.openCatalog'))}</a>` : ''}
            ${sampleCode ? `<a class="dataset-detail-link" href="${escapeHtml(sampleCode)}" target="_blank" rel="noreferrer">${escapeHtml(t('data.openSample'))}</a>` : ''}
          </div>
        </div>
      `;
    }
    function closeDatasetDetail() {
      const detail = $('dataset-detail');
      detail.classList.remove('open');
      detail.innerHTML = '';
      document.querySelector('.data-panel').classList.remove('detail-open');
    }
    function renderDatasetDetail(datasetId) {
      const item = datasetById(datasetId);
      if (!item) {
        closeDatasetDetail();
        return;
      }
      const detail = $('dataset-detail');
      detail.innerHTML = datasetDetailHtml(item);
      detail.classList.add('open');
      document.querySelector('.data-panel').classList.add('detail-open');
      $('dataset-detail-close')?.addEventListener('click', closeDatasetDetail);
      $('dataset-detail-add')?.addEventListener('click', () => importDatasetToMap(item.id));
      $('dataset-detail-copy')?.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(item.id || '');
          showModeKey('data.detailCopied');
        } catch (error) {
          showModeKey('log.clipboardUnavailable');
        }
      });
      $('dataset-detail-copy-context')?.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(JSON.stringify(datasetContext(item), null, 2));
          showModeKey('data.contextCopied');
        } catch (error) {
          showModeKey('log.clipboardUnavailable');
        }
      });
    }
    function setActiveDataset(datasetId) {
      activeDatasetId = datasetId;
      document.querySelectorAll('.dataset-item').forEach(item => item.classList.toggle('active', item.dataset.dataset === datasetId));
      renderDatasetDetail(datasetId);
      syncSessionState('selected-dataset');
      logMsg('log.datasetSelected', { dataset: datasetId });
    }
    function setLanguage(lang) {
      currentLang = lang;
      localStorage.setItem('easygee-lang', currentLang);
      applyI18n();
      renderDatasets(filteredCatalog());
      if (activeDatasetId && $('dataset-detail')?.classList.contains('open')) {
        renderDatasetDetail(activeDatasetId);
      }
      renderLayers();
      renderTasks();
      setActiveLayer(activeLayerId, { reveal: false });
      updateScaleLine();
      syncToolState();
      logMsg('log.language');
    }
    function quotaRows() {
      return STATE.quota && Array.isArray(STATE.quota.rows) ? STATE.quota.rows : [];
    }
    function quotaWarningText() {
      const warnings = Array.isArray(STATE.quota?.warnings) ? STATE.quota.warnings.join(' ').toLowerCase() : '';
      if (!warnings) return '';
      if (warnings.includes('active account selected') || warnings.includes('gcloud auth login')) return t('quota.issueCloudLogin');
      if (warnings.includes('cloudquotas.googleapis.com') && warnings.includes('not been used')) return t('quota.issueCloudQuotasApi');
      if (warnings.includes('cloudquotas.quotas.get') || warnings.includes('permission_denied') || warnings.includes('permission denied')) return t('quota.issueQuotaPermission');
      if (warnings.includes('monitoring.timeseries.list')) return t('quota.issueMonitoringPermission');
      if (warnings.includes('command group installed') || warnings.includes('components:') || warnings.includes('sslerror')) return t('quota.issueQuotaNetwork');
      return t('quota.issueLiveUnavailable');
    }
    function quotaSummaryText() {
      if (!quotaRows().length) return t('quota.summaryEmpty');
      if (STATE.quota?.status === 'live-with-usage') return t('quota.summaryLiveUsage');
      if (STATE.quota?.status === 'live-limit-only') return t('quota.summaryLiveLimit');
      return quotaWarningText() || t('quota.summaryDefault');
    }
    function quotaValue(value) {
      const text = String(value || '').trim();
      return text && text !== 'N/A' ? text : t('quota.notAvailable');
    }
    function parseQuotaNumber(value) {
      const text = String(value || '').replace(/,/g, '').trim();
      if (!text || text === 'N/A' || text === '-' || text.toLowerCase().includes('unlimited')) return null;
      const match = text.match(/-?\d+(?:\.\d+)?(?:e[+-]?\d+)?/i);
      if (!match) return null;
      const number = Number(match[0]);
      if (number >= 9e18) return null;
      return Number.isFinite(number) ? number : null;
    }
    function trimNumber(text) {
      return String(text).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
    }
    function compactQuotaNumber(number) {
      const abs = Math.abs(number);
      if (abs >= 1e12) return number.toExponential(2).replace('e+', 'e');
      if (currentLang === 'zh') {
        if (abs >= 1e8) return `${trimNumber((number / 1e8).toFixed(abs >= 1e9 ? 1 : 2))}亿`;
        if (abs >= 1e4) return `${trimNumber((number / 1e4).toFixed(abs >= 1e5 ? 1 : 2))}万`;
      } else {
        if (abs >= 1e9) return `${trimNumber((number / 1e9).toFixed(abs >= 1e10 ? 1 : 2))}B`;
        if (abs >= 1e6) return `${trimNumber((number / 1e6).toFixed(abs >= 1e7 ? 1 : 2))}M`;
        if (abs >= 1e3) return `${trimNumber((number / 1e3).toFixed(abs >= 1e4 ? 1 : 2))}k`;
      }
      if (abs >= 100) return trimNumber(number.toFixed(0));
      if (abs >= 10) return trimNumber(number.toFixed(1));
      return trimNumber(number.toFixed(2));
    }
    function quotaUnitLabel(unit) {
      const text = String(unit || '').trim();
      if (currentLang !== 'zh') return text;
      if (text === 's{CPU}') return 'CPU秒';
      if (text === 'slot-seconds/day (350 slot-hours)') return '槽秒/日';
      if (text === 'seconds/day') return '秒/日';
      if (text === 'concurrent requests') return '并发请求';
      if (text === 'requests') return '请求';
      if (text === 'assets') return '项';
      return text;
    }
    function compactQuotaValue(value) {
      const text = String(value || '').trim();
      if (!text || text === 'N/A') return t('quota.notAvailable');
      if (text.toLowerCase().includes('unlimited') || text === '∞') return t('quota.unlimited');
      const number = parseQuotaNumber(text);
      if (number === null) return text;
      const suffix = text.replace(/^[\s,0-9.eE+\-]+/, '').trim();
      const unit = quotaUnitLabel(suffix);
      return `${compactQuotaNumber(number)}${unit ? ` ${unit}` : ''}`;
    }
    function quotaPercentText(percent) {
      if (!Number.isFinite(percent)) return t('quota.unknown');
      if (percent > 0 && percent < 0.1) return '<0.1%';
      if (percent >= 10) return `${trimNumber(percent.toFixed(0))}%`;
      return `${trimNumber(percent.toFixed(1))}%`;
    }
    function quotaName(row) {
      return currentLang === 'zh' ? (row.nameZh || row.name) : (row.nameEn || row.name);
    }
    function knownQuotaValue(value) {
      const text = String(value || '').trim();
      return Boolean(text && text !== 'N/A' && text !== '-');
    }
    function quotaTierText() {
      const tier = STATE.quota?.tier;
      if (!tier || !tier.name) return t('quota.tierUnknown');
      const name = currentLang === 'zh' ? (tier.nameZh || tier.name) : (tier.nameEn || tier.name);
      return t(tier.inferred ? 'quota.tierInferred' : 'quota.tier', { tier: name });
    }
    function quotaPercentForRow(row) {
      if (row.unlimited) return null;
      const used = parseQuotaNumber(row.used);
      const limit = parseQuotaNumber(row.limit);
      if (used !== null && limit !== null && limit > 0) return Math.max(0, (used / limit) * 100);
      const raw = row.percent;
      if (raw === null || raw === undefined || raw === '') return null;
      const percent = Number(raw);
      return Number.isFinite(percent) ? percent : null;
    }
    function renderQuota() {
      const rows = quotaRows();
      const summary = quotaSummaryText();
      const measuredRows = rows.filter(row => quotaPercentForRow(row) !== null);
      const alertCount = measuredRows.filter(row => quotaPercentForRow(row) >= 80).length;
      const maxPercent = measuredRows.length ? Math.max(...measuredRows.map(row => quotaPercentForRow(row))) : null;
      $('quota-project').textContent = t('quota.project', { project: STATE.project });
      $('quota-tier').textContent = quotaTierText();
      $('quota-count').textContent = rows.length || 0;
      $('quota-used-summary').textContent = rows.length
        ? t('quota.measuredOfTotal', { count: measuredRows.length, total: rows.length })
        : t('quota.notAvailable');
      $('quota-remaining-summary').textContent = alertCount
        ? t('quota.alertCount', { count: alertCount })
        : t('quota.noAlerts');
      $('quota-summary').textContent = maxPercent === null
        ? summary
        : `${summary} · ${t('quota.maxUsed', { percent: quotaPercentText(maxPercent) })}`;
      const indicator = document.querySelector('.quota-indicator');
      if (indicator) {
        indicator.classList.remove('ok', 'warn', 'muted');
        indicator.classList.add(STATE.quota?.indicator || (rows.length ? 'warn' : 'muted'));
      }
      const quotaTitle = `${t('tool.quota')} - ${summary}`;
      $('quota-btn').title = quotaTitle;
      $('quota-btn').setAttribute('aria-label', quotaTitle);
      const usageSourceAvailable = Boolean(STATE.quota?.usageSource);
      $('quota-list').innerHTML = rows.length ? rows.slice(0, 5).map(row => {
        const percent = quotaPercentForRow(row);
        const hasPercent = percent !== null;
        const hasUsage = knownQuotaValue(row.used) && row.usageKnown !== false;
        const name = quotaName(row);
        const safePercent = hasPercent ? Math.max(0, Math.min(100, percent)) : 0;
        const barPercent = safePercent > 0 && safePercent < 0.1 ? 0.1 : safePercent;
        const meterWidth = hasPercent && safePercent > 0 ? `max(2px, ${trimNumber(barPercent.toFixed(2))}%)` : '0';
        const rowClass = `${escapeHtml(row.status || 'unknown')} ${hasPercent ? 'measured' : 'unknown'}`;
        const usage = row.unlimited && hasUsage
          ? t('quota.usedUnlimited', { used: compactQuotaValue(row.used) })
          : hasPercent
          ? t('quota.usedOfTotal', {
              used: compactQuotaValue(row.used),
              total: compactQuotaValue(row.limit),
              percent: quotaPercentText(percent),
            })
          : t('quota.totalOnly', { total: compactQuotaValue(row.limit) });
        const remaining = row.unlimited
          ? t('quota.remainingUnlimited')
          : hasPercent
          ? t('quota.remainingValue', { remaining: compactQuotaValue(row.remaining) })
          : t(row.inferredZeroUsage ? 'quota.noUsageYet' : usageSourceAvailable ? 'quota.usageUnavailable' : 'quota.usageMissing');
        const status = row.unlimited
          ? t('quota.unlimitedState')
          : hasPercent
          ? (percent >= 80 ? t('quota.warnState') : t('quota.okState'))
          : t(row.inferredZeroUsage ? 'quota.noUsageState' : 'quota.limitOnlyState');
        return `
          <div class="quota-row ${rowClass}">
            <div class="quota-row-head">
              <div class="quota-name" title="${escapeHtml(name)}">${escapeHtml(name)}</div>
              <div class="quota-usage" title="${escapeHtml(usage)}">${escapeHtml(usage)}</div>
            </div>
            <div class="quota-meter" aria-hidden="true"><span style="width:${meterWidth}"></span></div>
            <div class="quota-row-foot"><span>${escapeHtml(remaining)}</span><span>${escapeHtml(status)}</span></div>
          </div>
        `;
      }).join('') : `<div class="quota-note">${escapeHtml(t('quota.summaryEmpty'))}</div>`;
    }

    if (!window.L) {
      document.body.innerHTML = '<main style="padding:24px;font-family:Segoe UI,Arial,sans-serif"><h1>Leaflet failed to load</h1><p>Check network access to the Leaflet CDN, then reload this local page.</p></main>';
      throw new Error('Leaflet missing');
    }

    $('quota-link').href = STATE.quota?.consoleUrl || `https://console.cloud.google.com/iam-admin/quotas?service=earthengine.googleapis.com&project=${encodeURIComponent(STATE.project)}`;
    initializePersistentState();
    if (!activeLayerId && hasMeasurements()) activeLayerId = MEASUREMENTS_LAYER_ID;
    if (!activeLayerId && hasAoi()) activeLayerId = AOI_LAYER_ID;
    if (!activeLayerId) activeLayerId = PRIMARY_BASEMAP_LAYER_ID;

    const map = L.map('map', { zoomControl: false, attributionControl: false }).setView(STATE.center, STATE.zoom);
    map.createPane(PRIMARY_BASEMAP_PANE);
    map.getPane(PRIMARY_BASEMAP_PANE).style.zIndex = '150';
    map.getPane(PRIMARY_BASEMAP_PANE).style.pointerEvents = 'none';
    const CUSTOM_BASEMAP_TYPES = new Set(['xyz', 'tms', 'arcgis', 'wms', 'wmts', 'pmtiles', 'cog']);
    const pmtilesArchives = new Map();
    const cogMetadataCache = new Map();
    const basemapPerformanceSamples = new Map();
    const seenBasemapSources = new Set();
    const lazyAssetPromises = new Map();
    let cogEnginePromise = null;
    let cogEngineStatus = 'idle';
    let cogEngineError = '';
    function basemapPerformanceSourceKey(meta) {
      return `${String(meta?.type || 'xyz').toLowerCase()}:${String(meta?.url || meta?.id || '')}`;
    }
    function basemapResourceMatcher(meta) {
      const template = String(meta?.url || '').trim();
      if (!template) return () => false;
      try {
        const replacement = '__easygee_tile__';
        const parsed = new URL(template.replace(/[{][^}]+[}]/g, replacement), window.location.href);
        const templatedHost = parsed.hostname.startsWith(`${replacement}.`);
        const hostSuffix = templatedHost ? parsed.hostname.slice(replacement.length + 1) : parsed.hostname;
        const marker = parsed.pathname.indexOf(replacement);
        const pathPrefix = marker >= 0 ? parsed.pathname.slice(0, marker) : parsed.pathname;
        return name => {
          try {
            const entry = new URL(name, window.location.href);
            const hostMatches = templatedHost ? entry.hostname.endsWith(`.${hostSuffix}`) : entry.hostname === hostSuffix;
            const pathMatches = marker >= 0 ? entry.pathname.startsWith(pathPrefix) : entry.pathname === parsed.pathname;
            return entry.protocol === parsed.protocol && hostMatches && pathMatches;
          } catch {
            return false;
          }
        };
      } catch {
        return () => false;
      }
    }
    function collectBasemapNetworkPerformance(meta, sample) {
      if (!sample || typeof performance?.getEntriesByType !== 'function') return;
      const matches = basemapResourceMatcher(meta);
      const entries = performance.getEntriesByType('resource').filter(entry => (
        Number(entry.startTime) >= sample.startedAt - 1 && matches(entry.name)
      ));
      if (!entries.length) return;
      sample.sourceRequests = entries.length;
      const transferredBytes = entries.reduce((total, entry) => total + Math.max(0, Number(entry.transferSize) || 0), 0);
      if (transferredBytes > 0) sample.transferredBytes = Math.round(transferredBytes);
    }
    function publicBasemapPerformance(meta) {
      const sample = basemapPerformanceSamples.get(meta?.id);
      if (!sample) return null;
      return {
        status: sample.status,
        cache: sample.cache,
        ...(Number.isFinite(sample.firstRenderMs) ? { firstRenderMs: Math.round(sample.firstRenderMs) } : {}),
        ...(Number.isFinite(sample.readyMs) ? { readyMs: Math.round(sample.readyMs) } : {}),
        renderedBlocks: Math.max(0, Math.round(sample.renderedBlocks || 0)),
        ...(Number.isFinite(sample.sourceRequests) ? { sourceRequests: Math.max(0, Math.round(sample.sourceRequests)) } : {}),
        ...(Number.isFinite(sample.transferredBytes) ? { transferredBytes: Math.max(0, Math.round(sample.transferredBytes)) } : {}),
      };
    }
    function updateBasemapPerformance(meta, phase) {
      const sample = basemapPerformanceSamples.get(meta?.id);
      if (!sample || sample.status === 'error' || sample.status === 'ready') return;
      const elapsed = Math.max(0, performance.now() - sample.startedAt);
      if (phase === 'tile') {
        sample.renderedBlocks += 1;
        if (!Number.isFinite(sample.firstRenderMs)) sample.firstRenderMs = elapsed;
      }
      if (phase === 'ready') {
        if (!Number.isFinite(sample.firstRenderMs)) sample.firstRenderMs = elapsed;
        sample.readyMs = elapsed;
        sample.status = 'ready';
        seenBasemapSources.add(sample.sourceKey);
        collectBasemapNetworkPerformance(meta, sample);
      }
      if (meta?.id === currentBasemap) renderBasemapSourceDetails();
    }
    function failBasemapPerformance(meta) {
      const sample = basemapPerformanceSamples.get(meta?.id);
      if (!sample) return;
      sample.status = 'error';
      collectBasemapNetworkPerformance(meta, sample);
      if (meta?.id === currentBasemap) renderBasemapSourceDetails();
    }
    function beginBasemapPerformance(meta, layer) {
      if (!meta || !layer) return;
      const sourceKey = basemapPerformanceSourceKey(meta);
      const sample = {
        status: 'loading',
        cache: seenBasemapSources.has(sourceKey) ? 'warm' : 'cold',
        sourceKey,
        startedAt: performance.now(),
        firstRenderMs: null,
        readyMs: null,
        renderedBlocks: 0,
        sourceRequests: null,
        transferredBytes: null,
      };
      basemapPerformanceSamples.set(meta.id, sample);
      if (meta.id === currentBasemap) renderBasemapSourceDetails();
      if (String(meta.type || '').toLowerCase() === 'cog') {
        window.requestAnimationFrame(() => {
          try {
            const glMap = layer._easygeeCogLayer?.getMaplibreMap?.();
            if (basemapPerformanceSamples.get(meta.id) === sample && glMap?.getSource('easygee-cog-source') && glMap.isSourceLoaded('easygee-cog-source')) {
              updateBasemapPerformance(meta, 'tile');
              updateBasemapPerformance(meta, 'ready');
            }
          } catch {}
        });
      }
    }
    function bindBasemapPerformance(meta, layer) {
      if (!layer || layer._easygeePerformanceBound) return layer;
      layer._easygeePerformanceBound = true;
      layer.on('tileload', () => updateBasemapPerformance(meta, 'tile'));
      layer.on('load', () => updateBasemapPerformance(meta, 'ready'));
      return layer;
    }
    function createRegisteredBasemapLayer(meta, opacity = 1) {
      return bindBasemapPerformance(meta, createBasemapLayer(meta, { pane: PRIMARY_BASEMAP_PANE, opacity }));
    }
    function loadLazyStyle(key, href) {
      if (document.querySelector(`link[data-easygee-engine="${key}"]`)) return Promise.resolve();
      return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.dataset.easygeeEngine = key;
        link.addEventListener('load', () => resolve(), { once: true });
        link.addEventListener('error', () => { link.remove(); reject(new Error(`Failed to load ${key}`)); }, { once: true });
        document.head.appendChild(link);
      });
    }
    function loadLazyScript(key, src, ready) {
      if (ready()) return Promise.resolve();
      if (lazyAssetPromises.has(key)) return lazyAssetPromises.get(key);
      const promise = new Promise((resolve, reject) => {
        let script = document.querySelector(`script[data-easygee-engine="${key}"]`);
        if (script && script.dataset.easygeeLoaded === 'true') script.remove();
        script = document.querySelector(`script[data-easygee-engine="${key}"]`) || document.createElement('script');
        const finish = () => {
          script.dataset.easygeeLoaded = 'true';
          if (ready()) resolve();
          else { script.remove(); reject(new Error(`Invalid ${key} asset`)); }
        };
        const fail = () => { script.remove(); reject(new Error(`Failed to load ${key}`)); };
        script.addEventListener('load', finish, { once: true });
        script.addEventListener('error', fail, { once: true });
        if (!script.isConnected) {
          script.src = src;
          script.crossOrigin = 'anonymous';
          script.dataset.easygeeEngine = key;
          document.head.appendChild(script);
        }
      });
      const tracked = promise.catch(error => { lazyAssetPromises.delete(key); throw error; });
      lazyAssetPromises.set(key, tracked);
      return tracked;
    }
    function cogEngineReady() {
      return Boolean(window.maplibregl?.Map && window.MaplibreCOGProtocol?.cogProtocol && window.MaplibreCOGProtocol?.getCogMetadata && L.maplibreGL);
    }
    async function ensureCogEngine() {
      if (cogEngineReady() && window.__easygeeCogProtocolRegistered) {
        cogEngineStatus = 'ready';
        return true;
      }
      if (cogEnginePromise) return cogEnginePromise;
      cogEngineStatus = 'loading';
      cogEngineError = '';
      cogEnginePromise = (async () => {
        await Promise.all([
          loadLazyStyle('maplibre-css', COG_ENGINE_ASSETS.maplibreCss),
          loadLazyScript('maplibre-js', COG_ENGINE_ASSETS.maplibreJs, () => Boolean(window.maplibregl?.Map)),
        ]);
        await Promise.all([
          loadLazyScript('cog-protocol', COG_ENGINE_ASSETS.cogProtocolJs, () => Boolean(window.MaplibreCOGProtocol?.cogProtocol && window.MaplibreCOGProtocol?.getCogMetadata)),
          loadLazyScript('maplibre-leaflet', COG_ENGINE_ASSETS.leafletAdapterJs, () => Boolean(L.maplibreGL)),
        ]);
        if (typeof window.maplibregl.supported === 'function' && !window.maplibregl.supported()) throw new Error('WebGL unavailable');
        if (!window.__easygeeCogProtocolRegistered) {
          window.maplibregl.addProtocol('cog', window.MaplibreCOGProtocol.cogProtocol);
          window.__easygeeCogProtocolRegistered = true;
        }
        cogEngineStatus = 'ready';
        return true;
      })().catch(error => {
        cogEnginePromise = null;
        cogEngineStatus = 'error';
        cogEngineError = String(error?.message || error || 'COG engine unavailable').slice(0, 200);
        throw error;
      });
      return cogEnginePromise;
    }
    function basemapZoom(value, fallback) {
      const number = Number(value);
      return Number.isFinite(number) ? Math.max(0, Math.min(24, Math.round(number))) : fallback;
    }
    function normalizeBasemapBounds(value) {
      if (!Array.isArray(value) || value.length !== 4) return null;
      const bounds = value.map(Number);
      if (!bounds.every(Number.isFinite)) return null;
      const [west, south, east, north] = bounds;
      if (west < -180 || east > 180 || south < -90 || north > 90 || west >= east || south >= north) return null;
      return bounds;
    }
    function customBasemapIdentifier(value, fallback = '') {
      let id = String(value || fallback || '').trim().toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/-+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80);
      if (!id.startsWith('custom-')) id = `custom-${id || Date.now().toString(36)}`;
      return id;
    }
    function normalizeCustomBasemap(raw, index = 0) {
      if (!raw || typeof raw !== 'object') return null;
      const type = String(raw.type || 'xyz').trim().toLowerCase();
      const name = String(raw.name || '').trim().slice(0, 120);
      const url = String(raw.url || '').trim().slice(0, 4096);
      const sourceUrl = String(raw.sourceUrl || '').trim().slice(0, 4096);
      if (!CUSTOM_BASEMAP_TYPES.has(type) || !name || !url || urlContainsCredentials(url) || urlContainsCredentials(sourceUrl)) return null;
      const minZoom = basemapZoom(raw.minZoom, 0);
      const maxZoom = Math.max(minZoom, basemapZoom(raw.maxZoom, 19));
      const maxNativeZoom = Math.max(minZoom, Math.min(maxZoom, basemapZoom(raw.maxNativeZoom, maxZoom)));
      const id = customBasemapIdentifier(raw.id, `custom-${index + 1}`);
      const subdomains = String(raw.subdomains || '').trim().slice(0, 120);
      const attribution = String(raw.attribution || '').trim().slice(0, 1000);
      const bounds = normalizeBasemapBounds(raw.bounds);
      const bandCount = Math.max(0, Math.min(1024, Math.round(Number(raw.bandCount) || 0)));
      const options = { minZoom, maxZoom, maxNativeZoom, attribution, tms: type === 'tms' };
      if (subdomains) options.subdomains = subdomains.split(/[\s,]+/).filter(Boolean);
      return {
        id,
        name,
        type,
        custom: true,
        thumb: `custom-${type}`,
        url,
        provider: String(raw.provider || '').trim().slice(0, 240),
        service: String(raw.service || (type === 'pmtiles'
          ? 'PMTiles raster archive · HTTP Range'
          : type === 'cog'
            ? 'Cloud Optimized GeoTIFF · HTTP Range'
            : `${type.toUpperCase()} service`)).trim().slice(0, 240),
        attribution,
        sourceUrl,
        note: String(raw.note || '').trim().slice(0, 240),
        subdomains,
        layers: String(raw.layers || '').trim().slice(0, 500),
        styles: String(raw.styles || '').trim().slice(0, 500),
        format: String(raw.format || 'image/png').trim().slice(0, 80),
        version: String(raw.version || (type === 'wmts' ? '1.0.0' : '1.3.0')).trim().slice(0, 20),
        tileMatrixSet: String(raw.tileMatrixSet || 'GoogleMapsCompatible').trim().slice(0, 160),
        matrixPrefix: String(raw.matrixPrefix || '').trim().slice(0, 160),
        minZoom,
        maxZoom,
        maxNativeZoom,
        ...(bounds ? { bounds } : {}),
        ...(type === 'cog' ? { crs: String(raw.crs || 'EPSG:3857').trim().slice(0, 80), bandCount } : {}),
        transparent: raw.transparent !== false,
        options,
      };
    }
    function normalizeCustomBasemaps(value) {
      const seen = new Set();
      return (Array.isArray(value) ? value : []).slice(0, 100).map(normalizeCustomBasemap).filter(meta => {
        if (!meta || seen.has(meta.id)) return false;
        seen.add(meta.id);
        return true;
      });
    }
    function serializableCustomBasemap(meta) {
      const fields = ['id', 'name', 'type', 'url', 'provider', 'attribution', 'sourceUrl', 'note', 'subdomains', 'layers', 'styles', 'format', 'version', 'tileMatrixSet', 'matrixPrefix', 'minZoom', 'maxZoom', 'maxNativeZoom', 'bounds', 'crs', 'bandCount', 'transparent'];
      return Object.fromEntries(fields.map(key => [key, meta?.[key]]).filter(([, value]) => value !== undefined && value !== ''));
    }
    function customBasemapSignature(meta) {
      return JSON.stringify(serializableCustomBasemap(meta));
    }
    function appendTilePath(url, path) {
      const parts = String(url || '').split('?');
      const base = parts.shift().replace(/\/+$/, '');
      const query = parts.join('?');
      return `${base}${path}${query ? `?${query}` : ''}`;
    }
    function arcgisTileUrl(meta) {
      const url = String(meta.url || '').trim();
      return /\/tile\/\{z\}\/\{y\}\/\{x\}/i.test(url) ? url : appendTilePath(url, '/tile/{z}/{y}/{x}');
    }
    function wmtsTileUrl(meta) {
      const source = String(meta.url || '').trim();
      if (/\{(?:TileMatrix|TileRow|TileCol)\}/i.test(source)) {
        return source
          .replace(/\{TileMatrix\}/gi, `${meta.matrixPrefix || ''}{z}`)
          .replace(/\{TileRow\}/gi, '{y}')
          .replace(/\{TileCol\}/gi, '{x}');
      }
      const separator = source.includes('?') ? '&' : '?';
      const params = [
        'service=WMTS',
        'request=GetTile',
        `version=${encodeURIComponent(meta.version || '1.0.0')}`,
        `layer=${encodeURIComponent(meta.layers || '')}`,
        `style=${encodeURIComponent(meta.styles || '')}`,
        `tilematrixset=${encodeURIComponent(meta.tileMatrixSet || 'GoogleMapsCompatible')}`,
        `format=${encodeURIComponent(meta.format || 'image/png')}`,
        `tilematrix=${encodeURIComponent(meta.matrixPrefix || '')}{z}`,
        'tilerow={y}',
        'tilecol={x}',
      ];
      return `${source}${separator}${params.join('&')}`;
    }
    function discardPmtilesArchive(url) {
      const key = String(url || '').trim();
      if (key) pmtilesArchives.delete(key);
    }
    function getPmtilesArchive(url, options = {}) {
      if (!window.pmtiles?.PMTiles || !window.pmtiles?.leafletRasterLayer) {
        throw new Error('PMTiles engine unavailable');
      }
      const key = String(url || '').trim();
      if (options.refresh === true) pmtilesArchives.delete(key);
      if (!pmtilesArchives.has(key)) pmtilesArchives.set(key, new window.pmtiles.PMTiles(key));
      return pmtilesArchives.get(key);
    }
    function discardCogSource(url) {
      const key = String(url || '').trim();
      if (key) cogMetadataCache.delete(key);
    }
    async function getCogSourceMetadata(url, options = {}) {
      const key = String(url || '').trim();
      if (!key) throw new Error('COG URL is required');
      await ensureCogEngine();
      if (options.refresh === true) cogMetadataCache.delete(key);
      if (!cogMetadataCache.has(key)) {
        const request = window.MaplibreCOGProtocol.getCogMetadata(key).catch(error => {
          cogMetadataCache.delete(key);
          throw error;
        });
        cogMetadataCache.set(key, request);
      }
      return cogMetadataCache.get(key);
    }
    function cogMapStyle(meta, overrideOptions = {}) {
      const sourceId = 'easygee-cog-source';
      const layerId = 'easygee-cog-raster';
      const opacity = Math.max(0, Math.min(1, Number(overrideOptions.opacity ?? 1)));
      return {
        version: 8,
        sources: {
          [sourceId]: {
            type: 'raster',
            url: `cog://${meta.url}`,
            tileSize: 256,
            ...(meta.attribution ? { attribution: meta.attribution } : {}),
          },
        },
        layers: [{
          id: layerId,
          source: sourceId,
          type: 'raster',
          paint: {
            'raster-opacity': opacity,
            'raster-fade-duration': 0,
            'raster-resampling': 'linear',
          },
        }],
      };
    }
    function bindCogLayerEvents(group, glLayer) {
      const glMap = glLayer?.getMaplibreMap?.();
      if (!glMap || glMap.__easygeeCogBound) return;
      glMap.__easygeeCogBound = true;
      let loaded = false;
      let ready = false;
      const markLoaded = event => {
        if (loaded) return;
        if (event?.sourceId && event.sourceId !== 'easygee-cog-source') return;
        if (event?.sourceDataType && event.sourceDataType !== 'content') return;
        loaded = true;
        group.fire('tileload', { source: 'cog', event });
      };
      glMap.on('sourcedata', markLoaded);
      glMap.on('idle', () => {
        try {
          if (!glMap.getSource('easygee-cog-source') || !glMap.isSourceLoaded('easygee-cog-source')) return;
          markLoaded({ sourceId: 'easygee-cog-source', sourceDataType: 'content' });
          if (!ready) {
            ready = true;
            group.fire('load', { source: 'cog' });
          }
        } catch {}
      });
      glMap.on('error', event => group.fire('tileerror', { source: 'cog', error: event?.error || event }));
    }
    function createCogBasemapLayer(meta, overrideOptions = {}) {
      const group = L.layerGroup();
      group._easygeeCogLayer = null;
      group._easygeeCogMount = null;
      group._easygeeOpacity = Math.max(0, Math.min(1, Number(overrideOptions.opacity ?? 1)));
      const mount = async () => {
        if (group._easygeeCogLayer) {
          window.requestAnimationFrame(() => bindCogLayerEvents(group, group._easygeeCogLayer));
          return group._easygeeCogLayer;
        }
        if (group._easygeeCogMount) return group._easygeeCogMount;
        group._easygeeCogMount = ensureCogEngine().then(() => {
          const glLayer = L.maplibreGL({
            style: cogMapStyle(meta, { ...overrideOptions, opacity: group._easygeeOpacity }),
            interactive: false,
            pane: overrideOptions.pane || 'tilePane',
            attributionControl: false,
            className: 'easygee-cog-canvas',
            fadeDuration: 0,
          });
          group._easygeeCogLayer = glLayer;
          group.addLayer(glLayer);
          if (map.hasLayer(group)) window.requestAnimationFrame(() => bindCogLayerEvents(group, glLayer));
          return glLayer;
        }).catch(error => {
          group._easygeeCogMount = null;
          group.fire('tileerror', { source: 'cog', error });
          if (currentBasemap === meta.id && map.hasLayer(group)) handleBasemapRuntimeFailure(meta, error);
          throw error;
        });
        return group._easygeeCogMount;
      };
      group.on('add', () => { mount().catch(() => {}); });
      group.setOpacity = value => {
        group._easygeeOpacity = Math.max(0, Math.min(1, Number(value)));
        const glMap = group._easygeeCogLayer?.getMaplibreMap?.();
        try {
          if (glMap?.getLayer('easygee-cog-raster')) glMap.setPaintProperty('easygee-cog-raster', 'raster-opacity', group._easygeeOpacity);
        } catch {}
        return group;
      };
      return group;
    }
    function tiandituWmtsUrl(layer, token) {
      return `https://t{s}.tianditu.gov.cn/${layer}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=${layer}&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${encodeURIComponent(token)}`;
    }
    function createTiandituBasemapLayer(meta, overrideOptions = {}) {
      if (!tiandituToken) throw new Error('Tianditu key required');
      const options = { ...(meta.options || {}), ...overrideOptions, subdomains: '01234567' };
      const base = L.tileLayer(tiandituWmtsUrl(meta.tiandituBase, tiandituToken), { ...options, zIndex: 0 });
      const labels = L.tileLayer(tiandituWmtsUrl(meta.tiandituLabels, tiandituToken), { ...options, zIndex: 1 });
      const group = L.layerGroup([base, labels]);
      [base, labels].forEach(layer => {
        layer.on('tileload', event => group.fire('tileload', event));
        layer.on('load', event => group.fire('load', event));
        layer.on('tileerror', event => group.fire('tileerror', event));
      });
      group.setOpacity = value => {
        const opacity = Math.max(0, Math.min(1, Number(value)));
        base.setOpacity(opacity);
        labels.setOpacity(opacity);
        return group;
      };
      return group;
    }
    function createBasemapLayer(meta, overrideOptions = {}) {
      const options = { ...(meta.options || {}), ...overrideOptions };
      if (isTiandituBasemap(meta)) return createTiandituBasemapLayer(meta, options);
      if (meta.custom && meta.type === 'pmtiles') {
        return window.pmtiles.leafletRasterLayer(getPmtilesArchive(meta.url), options);
      }
      if (meta.custom && meta.type === 'cog') return createCogBasemapLayer(meta, options);
      if (meta.custom && meta.type === 'wms') {
        return L.tileLayer.wms(meta.url, {
          ...options,
          layers: meta.layers,
          styles: meta.styles || '',
          format: meta.format || 'image/png',
          version: meta.version || '1.3.0',
          transparent: meta.transparent !== false,
        });
      }
      const tileUrl = meta.custom && meta.type === 'arcgis'
        ? arcgisTileUrl(meta)
        : meta.custom && meta.type === 'wmts'
          ? wmtsTileUrl(meta)
          : meta.url;
      return L.tileLayer(tileUrl, options);
    }
    function tryCreateBasemapLayer(meta, overrideOptions = {}) {
      try {
        return createBasemapLayer(meta, overrideOptions);
      } catch {
        return null;
      }
    }
    function setRasterLayerOpacity(layer, value) {
      const opacity = Math.max(0, Math.min(1, Number(value)));
      if (!layer || !Number.isFinite(opacity)) return false;
      if (typeof layer.setOpacity === 'function') {
        layer.setOpacity(opacity);
        return true;
      }
      if (typeof layer.eachLayer === 'function') {
        layer.eachLayer(child => {
          if (typeof child?.setOpacity === 'function') child.setOpacity(opacity);
        });
        return true;
      }
      return false;
    }

    const BUILTIN_BASEMAPS = [
      {
        id: 'OSM',
        nameKey: 'basemap.osm',
        noteKey: 'basemap.osmNote',
        thumb: 'osm',
        provider: 'OpenStreetMap contributors',
        service: 'OpenStreetMap Standard',
        sourceUrl: 'https://www.openstreetmap.org/copyright',
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        options: { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }
      },
      {
        id: 'CartoLight',
        nameKey: 'basemap.light',
        noteKey: 'basemap.lightNote',
        thumb: 'light',
        provider: 'CARTO · OpenStreetMap contributors',
        service: 'CARTO Positron',
        sourceUrl: 'https://carto.com/basemaps/',
        url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        options: { maxZoom: 20, attribution: '&copy; OpenStreetMap contributors &copy; CARTO' }
      },
      {
        id: 'CartoDark',
        nameKey: 'basemap.dark',
        noteKey: 'basemap.darkNote',
        thumb: 'dark',
        provider: 'CARTO · OpenStreetMap contributors',
        service: 'CARTO Dark Matter',
        sourceUrl: 'https://carto.com/basemaps/',
        url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        options: { maxZoom: 20, attribution: '&copy; OpenStreetMap contributors &copy; CARTO' }
      },
      {
        id: 'CartoVoyager',
        nameKey: 'basemap.voyager',
        noteKey: 'basemap.voyagerNote',
        thumb: 'voyager',
        provider: 'CARTO · OpenStreetMap contributors',
        service: 'CARTO Voyager',
        sourceUrl: 'https://carto.com/basemaps/',
        url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
        options: { maxZoom: 20, attribution: '&copy; OpenStreetMap contributors &copy; CARTO' }
      },
      {
        id: 'EsriTopo',
        nameKey: 'basemap.topo',
        noteKey: 'basemap.topoNote',
        thumb: 'topo',
        provider: 'Esri',
        serviceKey: 'basemap.topoCoverage',
        sourceUrl: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer',
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        options: { maxZoom: 19, maxNativeZoom: 13, attribution: 'Tiles &copy; Esri' }
      },
      {
        id: 'Imagery',
        nameKey: 'basemap.imagery',
        noteKey: 'basemap.imageryNote',
        thumb: 'imagery',
        provider: 'Esri',
        service: 'World Imagery',
        sourceUrl: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer',
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        options: { maxZoom: 19, attribution: 'Tiles &copy; Esri' }
      },
      {
        id: 'EsriClarity',
        nameKey: 'basemap.esriClarity',
        noteKey: 'basemap.esriClarityNote',
        thumb: 'clarity',
        provider: 'Esri',
        service: 'World Imagery Clarity',
        sourceUrl: 'https://clarity.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer',
        url: 'https://clarity.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        options: { maxZoom: 19, attribution: 'Tiles &copy; Esri (World Imagery Clarity)' }
      },
      {
        id: 'TiandituVector',
        nameKey: 'basemap.tiandituVector',
        noteKey: 'basemap.tiandituVectorNote',
        thumb: 'tianditu-vector',
        provider: '国家基础地理信息中心 · 天地图',
        service: 'WMTS vec_w + cva_w',
        sourceUrl: 'https://lbs.tianditu.gov.cn/server/MapService.html',
        tiandituBase: 'vec',
        tiandituLabels: 'cva',
        options: { maxZoom: 22, maxNativeZoom: 18, attribution: '&copy; 天地图' }
      },
      {
        id: 'TiandituImagery',
        nameKey: 'basemap.tiandituImagery',
        noteKey: 'basemap.tiandituImageryNote',
        thumb: 'tianditu-imagery',
        provider: '国家基础地理信息中心 · 天地图',
        service: 'WMTS img_w + cia_w',
        sourceUrl: 'https://lbs.tianditu.gov.cn/server/MapService.html',
        tiandituBase: 'img',
        tiandituLabels: 'cia',
        options: { maxZoom: 22, maxNativeZoom: 18, attribution: '&copy; 天地图' }
      },
      {
        id: 'TiandituTerrain',
        nameKey: 'basemap.tiandituTerrain',
        noteKey: 'basemap.tiandituTerrainNote',
        thumb: 'tianditu-terrain',
        provider: '国家基础地理信息中心 · 天地图',
        service: 'WMTS ter_w + cta_w',
        sourceUrl: 'https://lbs.tianditu.gov.cn/server/MapService.html',
        tiandituBase: 'ter',
        tiandituLabels: 'cta',
        options: { maxZoom: 22, maxNativeZoom: 18, attribution: '&copy; 天地图' }
      }
    ];
    let customBasemaps = [];
    let defaultBasemapId = 'OSM';
    let BASEMAPS = [...BUILTIN_BASEMAPS];
    let primaryBasemapShown = STATE.basemapShown !== false;
    let primaryBasemapOpacity = Number.isFinite(Number(STATE.basemapOpacity))
      ? Math.max(0, Math.min(1, Number(STATE.basemapOpacity)))
      : 1;
    const basemapLayers = new Map();
    BASEMAPS.forEach(meta => {
      const layer = tryCreateBasemapLayer(meta, { pane: PRIMARY_BASEMAP_PANE, opacity: primaryBasemapOpacity });
      if (layer) basemapLayers.set(meta.id, bindBasemapPerformance(meta, layer));
    });
    let currentBasemap = 'OSM';
    let basemapEditorId = null;
    let testedBasemapSignature = '';
    let testedCogDetails = null;
    beginBasemapPerformance(BASEMAPS.find(meta => meta.id === currentBasemap), basemapLayers.get(currentBasemap));
    if (primaryBasemapShown) basemapLayers.get(currentBasemap).addTo(map);
    function handleBasemapRuntimeFailure(meta, error) {
      if (!meta || currentBasemap !== meta.id) return false;
      failBasemapPerformance(meta);
      const failedLayer = basemapLayers.get(meta.id);
      if (failedLayer && map.hasLayer(failedLayer)) map.removeLayer(failedLayer);
      const fallbackId = defaultBasemapId !== meta.id && basemapLayers.has(defaultBasemapId) ? defaultBasemapId : 'OSM';
      const fallbackLayer = basemapLayers.get(fallbackId);
      if (!fallbackLayer) return false;
      const fallbackMeta = BASEMAPS.find(item => item.id === fallbackId);
      beginBasemapPerformance(fallbackMeta, fallbackLayer);
      setRasterLayerOpacity(fallbackLayer, primaryBasemapOpacity);
      if (primaryBasemapShown && !map.hasLayer(fallbackLayer)) fallbackLayer.addTo(map);
      currentBasemap = fallbackId;
      cogEngineError = String(error?.message || error || 'COG layer failed').slice(0, 200);
      renderBasemapChoices();
      renderLayers();
      updateInspector();
      showModeKey('basemap.testFailed', { message: t('basemap.cogUnavailable') }, true);
      syncSessionState('cog-basemap-fallback');
      return true;
    }
    function rebuildBasemapRegistry(preferredBasemap = currentBasemap) {
      const nextBasemaps = [...BUILTIN_BASEMAPS, ...customBasemaps];
      const nextLayers = new Map();
      nextBasemaps.forEach(meta => {
        const layer = tryCreateBasemapLayer(meta, { pane: PRIMARY_BASEMAP_PANE, opacity: primaryBasemapOpacity });
        bindBasemapPerformance(meta, layer);
        if (layer) nextLayers.set(meta.id, layer);
      });
      const fallback = nextLayers.has(defaultBasemapId) ? defaultBasemapId : 'OSM';
      let nextBasemap = nextLayers.has(preferredBasemap) ? preferredBasemap : fallback;
      let nextLayer = nextLayers.get(nextBasemap) || nextLayers.get('OSM');
      if (!nextLayer) return currentBasemap;
      let nextMeta = nextBasemaps.find(item => item.id === nextBasemap);
      beginBasemapPerformance(nextMeta, nextLayer);
      fitCogBasemapBounds(nextMeta);
      try {
        if (primaryBasemapShown) nextLayer.addTo(map);
      } catch {
        failBasemapPerformance(nextMeta);
        nextBasemap = 'OSM';
        nextLayer = nextLayers.get('OSM');
        if (!nextLayer) return currentBasemap;
        nextMeta = nextBasemaps.find(item => item.id === nextBasemap);
        beginBasemapPerformance(nextMeta, nextLayer);
        if (primaryBasemapShown) nextLayer.addTo(map);
      }
      basemapLayers.forEach(layer => {
        if (layer !== nextLayer && map.hasLayer(layer)) map.removeLayer(layer);
      });
      BASEMAPS = nextBasemaps;
      basemapLayers.clear();
      nextLayers.forEach((layer, id) => basemapLayers.set(id, layer));
      currentBasemap = nextBasemap;
      if ($('basemap-list')) renderBasemapChoices();
      if ($('detail-name')) updateInspector();
      return currentBasemap;
    }
    let aoiLayer = null;

    function basemapMetaById(id) {
      const sourceId = String(id || '');
      return [...BUILTIN_BASEMAPS, ...customBasemaps].find(meta => meta.id === sourceId) || null;
    }
    function isBasemapOverlayLayer(meta) {
      return String(meta?.type || '').toLowerCase() === 'basemap-overlay';
    }
    function basemapLayerDataset(meta) {
      if (!meta) return '';
      const service = meta.serviceKey ? t(meta.serviceKey) : (meta.service || basemapDisplayNote(meta));
      return [meta.provider, service].filter(Boolean).join(' · ');
    }
    function primaryBasemapLayerModel() {
      const meta = currentBasemapMeta();
      return {
        id: PRIMARY_BASEMAP_LAYER_ID,
        name: basemapDisplayName(meta),
        dataset: basemapLayerDataset(meta),
        type: 'primary-basemap',
        role: 'base',
        sourceId: meta?.id || currentBasemap,
        shown: primaryBasemapShown,
        opacity: primaryBasemapOpacity,
        styleProfile: 'basemap',
      };
    }

    function registerLayer(meta) {
      const normalized = normalizeStateLayer(meta);
      if (!normalized) return null;
      operationalMapOrderDirty = true;
      if (isBasemapOverlayLayer(normalized)) {
        const source = basemapMetaById(normalized.sourceId);
        if (!source) return null;
        const tile = tryCreateBasemapLayer(source, { opacity: normalized.opacity, pane: 'tilePane' });
        if (!tile) return null;
        layerRegistry.set(normalized.id, { meta: normalized, tile, sourceId: source.id });
        if (normalized.shown) tile.addTo(map);
        return tile;
      }
      if (normalized.type === 'ee-restore-pending') {
        const group = L.layerGroup();
        layerRegistry.set(normalized.id, { meta: normalized, tile: group });
        if (normalized.shown) group.addTo(map);
        return group;
      }
      if (isUploadPlaceholderLayer(normalized)) {
        const group = L.layerGroup();
        layerRegistry.set(normalized.id, { meta: normalized, tile: group, refresh: () => {} });
        if (normalized.shown) group.addTo(map);
        return group;
      }
      if (isLocalVectorLayer(normalized)) {
        const vector = createLocalVectorLayer(normalized);
        layerRegistry.set(normalized.id, { meta: normalized, tile: vector.layer, refresh: vector.refresh });
        if (normalized.shown) vector.layer.addTo(map);
        return vector.layer;
      }
      const tile = L.tileLayer(normalized.tileUrl, { opacity: normalized.opacity, attribution: 'Google Earth Engine' });
      layerRegistry.set(normalized.id, { meta: normalized, tile });
      if (normalized.shown) tile.addTo(map);
      return tile;
    }
    STATE.layers.forEach(meta => {
      registerLayer(meta);
    });

    function isReorderableLayer(id) {
      return Boolean(id) && id !== PRIMARY_BASEMAP_LAYER_ID
        && rawOperationalLayerModels().some(layer => String(layer.id) === String(id));
    }
    function rawOperationalLayerModels() {
      return [measurementsLayerModel(), aoiLayerModel(), ...STATE.layers].filter(Boolean);
    }
    function normalizedOperationalLayerOrder(order = operationalLayerOrder) {
      const available = rawOperationalLayerModels().map(layer => String(layer.id));
      const availableSet = new Set(available);
      const requested = Array.isArray(order) ? order.map(value => String(value)) : [];
      const known = [...new Set(requested)].filter(id => availableSet.has(id));
      return [...known, ...available.filter(id => !known.includes(id))];
    }
    function syncOperationalLayerOrder() {
      const next = normalizedOperationalLayerOrder(operationalLayerOrder);
      if (JSON.stringify(next) !== JSON.stringify(operationalLayerOrder)) operationalMapOrderDirty = true;
      operationalLayerOrder = next;
      return operationalLayerOrder;
    }
    function placeOperationalLayer(id, position = 'front') {
      const next = syncOperationalLayerOrder().filter(item => item !== String(id));
      if (position === 'front') next.unshift(String(id));
      else next.push(String(id));
      operationalLayerOrder = normalizedOperationalLayerOrder(next);
      operationalMapOrderDirty = true;
    }
    function removeOperationalLayerOrder(id) {
      operationalLayerOrder = normalizedOperationalLayerOrder(syncOperationalLayerOrder().filter(item => item !== String(id)));
      operationalMapOrderDirty = true;
    }
    function operationalMapLayer(id) {
      if (id === AOI_LAYER_ID) return aoiLayer;
      if (id === MEASUREMENTS_LAYER_ID) return measureLayer;
      return layerRegistry.get(id)?.tile || null;
    }
    function syncLayerOrderToMap() {
      const models = operationalLayerModels();
      if (!operationalMapOrderDirty) return;
      models.forEach(layer => {
        const mapLayer = operationalMapLayer(layer.id);
        if (mapLayer && map.hasLayer(mapLayer)) map.removeLayer(mapLayer);
      });
      [...models].reverse().forEach(layer => {
        const mapLayer = operationalMapLayer(layer.id);
        if (layer.shown !== false && mapLayer && !map.hasLayer(mapLayer)) mapLayer.addTo(map);
      });
      operationalMapOrderDirty = false;
    }
    function reorderLayer(sourceId, targetId) {
      if (!isReorderableLayer(sourceId) || !isReorderableLayer(targetId) || sourceId === targetId) return false;
      const order = syncOperationalLayerOrder().filter(id => id !== String(sourceId));
      const targetIndex = order.indexOf(String(targetId));
      if (targetIndex < 0) return false;
      order.splice(targetIndex, 0, String(sourceId));
      operationalLayerOrder = normalizedOperationalLayerOrder(order);
      operationalMapOrderDirty = true;
      const moved = rawOperationalLayerModels().find(layer => String(layer.id) === String(sourceId));
      syncLayerOrderToMap();
      renderLayers();
      setActiveLayer(sourceId, { reveal: false });
      showModeKey('mode.layerReordered');
      logMsg('log.layerReordered', { layer: moved?.name || sourceId });
      syncSessionState('layer-reordered');
      return true;
    }

    function addGeneratedLayer(meta, options = {}) {
      const existingIndex = STATE.layers.findIndex(layer => layer.id === meta.id);
      if (existingIndex >= 0) {
        const existing = layerRegistry.get(meta.id);
        if (existing && map.hasLayer(existing.tile)) map.removeLayer(existing.tile);
        STATE.layers.splice(existingIndex, 1);
        removeOperationalLayerOrder(meta.id);
      }
      const nextMeta = normalizeStateLayer({ ...meta, shown: options.shown === undefined ? true : options.shown !== false });
      STATE.layers.unshift(nextMeta);
      placeOperationalLayer(nextMeta.id, 'front');
      const tile = registerLayer(nextMeta);
      if (nextMeta.shown && !map.hasLayer(tile)) tile.addTo(map);
      $('layer-count').textContent = t('pill.layers', { count: layerCount() });
      renderLayers();
      renderDatasets(filteredCatalog());
      if (options.activate !== false) setActiveLayer(nextMeta.id);
      if (options.sync !== false) syncSessionState('layer-added');
      return nextMeta;
    }

    function revealLayerPanel(id) {
      document.querySelector('.data-panel').classList.remove('open');
      document.querySelector('.upload-panel').classList.remove('open');
      document.querySelector('.basemap-panel').classList.remove('open');
      document.querySelector('.right').classList.remove('open');
      document.querySelector('.bottom').classList.remove('open');
      document.querySelector('.layers-panel').classList.add('open');
      syncToolState();
      if (id) setActiveLayer(id);
    }
    function addBasemapOverlay(sourceId) {
      const meta = basemapMetaById(sourceId);
      if (!meta) return false;
      if (isTiandituBasemap(meta) && !tiandituToken) return requestTiandituToken();
      const existing = STATE.layers.find(layer => isBasemapOverlayLayer(layer) && layer.sourceId === meta.id);
      if (existing) {
        setLayerVisibility(existing.id, true, { reveal: false, reason: 'basemap-overlay-visible' });
        revealLayerPanel(existing.id);
        renderBasemapChoices();
        return existing.id;
      }
      const safeSourceId = String(meta.id || 'basemap').replace(/[^a-z0-9_-]+/gi, '-').replace(/^-+|-+$/g, '').slice(0, 48) || 'basemap';
      const nextMeta = normalizeStateLayer({
        id: `basemap-overlay-${safeSourceId}-${Date.now().toString(36)}`,
        name: basemapDisplayName(meta),
        dataset: basemapLayerDataset(meta),
        type: 'basemap-overlay',
        role: 'overlay',
        sourceId: meta.id,
        shown: true,
        opacity: 1,
        styleProfile: 'basemap',
      });
      const tile = registerLayer(nextMeta);
      if (!tile) return false;
      STATE.layers.unshift(nextMeta);
      placeOperationalLayer(nextMeta.id, 'front');
      renderLayers();
      renderBasemapChoices();
      revealLayerPanel(nextMeta.id);
      showModeKey('mode.basemapOverlayAdded', { basemap: nextMeta.name });
      logMsg('log.basemapOverlayAdded', { basemap: nextMeta.name });
      syncSessionState('basemap-overlay-added');
      return nextMeta.id;
    }
    function reloadBasemapOverlays(sourceId) {
      const overlays = STATE.layers.filter(layer => isBasemapOverlayLayer(layer) && layer.sourceId === sourceId);
      overlays.forEach(meta => {
        const record = layerRegistry.get(meta.id);
        if (record && map.hasLayer(record.tile)) map.removeLayer(record.tile);
        layerRegistry.delete(meta.id);
        registerLayer(meta);
      });
      if (overlays.length) renderLayers();
      return overlays.length;
    }

    function aoiLayerModel() {
      if (!hasAoi()) return null;
      return {
        id: AOI_LAYER_ID,
        name: 'AOI',
        dataset: STATE.aoi.type === 'polygon' ? 'Drawn polygon AOI' : 'Drawn rectangle AOI',
        type: 'aoi',
        shown: STATE.aoiShown !== false,
        opacity: STATE.aoiStyle.opacity,
        styleProfile: 'aoi',
        legend: [[STATE.aoiStyle.color, 'AOI boundary']],
      };
    }
    function hasMeasurements() {
      return measurementSummary().count > 0;
    }
    function measurementsLayerModel() {
      const summary = measurementSummary();
      if (!summary.count) return null;
      return {
        id: MEASUREMENTS_LAYER_ID,
        name: t('measurements.layerName'),
        dataset: t('measurements.layerDataset', { count: summary.count }),
        type: 'measurements',
        shown: STATE.measurementsShown !== false,
        opacity: normalizeMeasurementsOpacity(STATE.measurementsOpacity),
        styleProfile: 'measurements',
        legend: [[DEFAULT_MEASUREMENTS_STYLE.color, t('measurements.legend')]],
        summary,
      };
    }
    function operationalLayerModels() {
      const available = new Map(rawOperationalLayerModels().map(layer => [String(layer.id), layer]));
      return syncOperationalLayerOrder().map(id => available.get(id)).filter(Boolean);
    }
    function layerModels() {
      return [...operationalLayerModels(), primaryBasemapLayerModel()];
    }
    function layerCount() {
      return layerModels().length;
    }
    function renderAoiLayer() {
      if (aoiLayer && map.hasLayer(aoiLayer)) map.removeLayer(aoiLayer);
      aoiLayer = null;
      operationalMapOrderDirty = true;
      if (!hasAoi() || STATE.aoiShown === false) {
        syncLayerOrderToMap();
        return;
      }
      STATE.aoiStyle = normalizeAoiStyle(STATE.aoiStyle);
      const options = {
        color: STATE.aoiStyle.color,
        weight: STATE.aoiStyle.weight,
        opacity: STATE.aoiStyle.opacity,
        fill: true,
        fillColor: STATE.aoiStyle.fillColor,
        fillOpacity: STATE.aoiStyle.fillOpacity,
      };
      if (STATE.aoi.type === 'polygon') {
        aoiLayer = L.polygon(STATE.aoi.coordinates, options).addTo(map);
      } else {
        aoiLayer = L.rectangle(STATE.aoi.bounds, options).addTo(map);
      }
      syncLayerOrderToMap();
    }

    const measureLayer = L.layerGroup().addTo(map);
    const measureDraftLayer = L.layerGroup().addTo(map);
    const drawAoiLayer = L.layerGroup().addTo(map);
    let drawAoiMode = false;
    let drawPolygonMode = false;
    let drawAoiStart = null;
    let drawAoiPreview = null;
    let drawPolygonPoints = [];
    let polygonDoubleClickZoomWasEnabled = false;
    let measureMode = false;
    let measurementLayerNotice = false;
    let measurePoints = [];

    function chooseScaleDistance(maxMeters) {
      if (!Number.isFinite(maxMeters) || maxMeters <= 0) return 1;
      const exponent = Math.floor(Math.log10(maxMeters));
      for (let exp = exponent; exp >= -1; exp -= 1) {
        for (const base of [5, 2, 1]) {
          const candidate = base * (10 ** exp);
          if (candidate <= maxMeters) return candidate;
        }
      }
      return 1;
    }
    function updateScaleLine() {
      const size = map.getSize();
      if (!size.x || !size.y) return;
      const targetPx = 88;
      const y = Math.max(0, size.y - 20);
      const start = map.containerPointToLatLng([58, y]);
      const end = map.containerPointToLatLng([58 + targetPx, y]);
      const maxMeters = distanceMeters(start, end);
      const meters = chooseScaleDistance(maxMeters);
      const px = Math.max(34, Math.min(targetPx, Math.round((meters / maxMeters) * targetPx)));
      $('scale-track').style.width = `${px}px`;
      $('scale-label').style.width = `${px}px`;
      $('scale-label').textContent = formatScaleDistance(meters);
    }

    function datasetItemHtml(item) {
      const readyCount = datasetLayerIds(item.id).length;
      const ready = readyCount > 0;
      const pending = pendingDatasetIds.has(item.id);
      const failed = failedDatasetIds.has(item.id);
      const addTitle = pending ? t('data.processing') : t('data.addTitle');
      const provider = item.provider ? `<div class="dataset-provider">${escapeHtml(item.provider)}</div>` : '';
      const tagsText = [catalogCategoryLabel(catalogCategoryKey(item)), item.tags, item.license].filter(Boolean).join(' · ');
      const tags = tagsText ? `<div class="dataset-tags">${escapeHtml(tagsText)}</div>` : '';
      const statusKey = pending ? 'data.processing' : failed ? 'data.failed' : ready ? 'data.ready' : '';
      const statusText = ready ? t(statusKey, { count: readyCount }) : statusKey ? t(statusKey) : '';
      const statusClass = pending ? 'pending' : failed ? 'error' : ready ? '' : 'muted';
      const typeLabel = catalogTypeLabel(normalizeCatalogType(item));
      const attrs = datasetAttrsHtml(item, typeLabel);
      const favorite = isFavoriteDataset(item.id);
      const favoriteTitle = favorite ? t('data.unfavoriteTitle') : t('data.favoriteTitle');
      const sourceLabel = catalogSourceLabel(item);
      return `
        <div class="dataset-item ${activeDatasetId === item.id ? 'active' : ''}" data-dataset="${escapeHtml(item.id)}" role="button" tabindex="0">
          <div>
            <div class="dataset-name">${escapeHtml(item.label)}</div>
            <div class="dataset-meta">${escapeHtml(item.id)} | ${escapeHtml(typeLabel)} | ${escapeHtml(sourceLabel)} | ${escapeHtml(item.scale || item.category || '')}</div>
            ${attrs}
            ${tags}
            ${provider}
            ${statusText ? `<div class="dataset-status ${statusClass}">${escapeHtml(statusText)}</div>` : ''}
          </div>
          <div class="dataset-actions">
            <button class="dataset-favorite icon-btn ${favorite ? 'active' : ''}" data-action="favorite" title="${escapeHtml(favoriteTitle)}" aria-label="${escapeHtml(favoriteTitle)}" aria-pressed="${favorite ? 'true' : 'false'}" type="button">__EASYGEE_ICON_FAVORITE__</button>
            <button class="dataset-add icon-btn" data-action="add" title="${escapeHtml(addTitle)}" aria-label="${escapeHtml(addTitle)}" type="button" ${pending ? 'disabled' : ''}>__EASYGEE_ICON_ADD__</button>
          </div>
        </div>
      `;
    }

    function updateCatalogCount() {
      const total = Array.isArray(STATE.catalog) ? STATE.catalog.length : 0;
      const matches = catalogListItems.length;
      const shown = Math.min(catalogRenderedCount, matches);
      $('catalog-count').textContent = matches === total
        ? t('pill.datasetLoaded', { shown, matches })
        : t('pill.datasetLoadedFiltered', { shown, matches, total });
    }

    function bindDatasetItems(scope) {
      scope.querySelectorAll('.dataset-item:not([data-bound])').forEach(item => {
        item.dataset.bound = 'true';
        item.addEventListener('click', event => {
          if (event.target.closest('[data-action="add"], [data-action="favorite"]')) return;
          document.querySelectorAll('.dataset-item').forEach(item => item.classList.remove('active'));
          item.classList.add('active');
          setActiveDataset(item.dataset.dataset);
        });
        item.addEventListener('keydown', event => {
          if (event.key !== 'Enter' && event.key !== ' ') return;
          event.preventDefault();
          setActiveDataset(item.dataset.dataset);
        });
        item.querySelector('[data-action="add"]').addEventListener('click', event => {
          event.stopPropagation();
          importDatasetToMap(item.dataset.dataset);
        });
        item.querySelector('[data-action="favorite"]').addEventListener('click', event => {
          event.stopPropagation();
          toggleFavoriteDataset(item.dataset.dataset);
        });
      });
    }

    function appendDatasetBatch() {
      const list = $('dataset-list');
      if (!catalogListItems.length || catalogRenderedCount >= catalogListItems.length) return;
      const start = catalogRenderedCount;
      catalogRenderedCount = Math.min(catalogRenderedCount + CATALOG_RENDER_BATCH, catalogListItems.length);
      const nextItems = catalogListItems.slice(start, catalogRenderedCount);
      list.querySelector('.dataset-loading')?.remove();
      list.insertAdjacentHTML('beforeend', nextItems.map(datasetItemHtml).join(''));
      bindDatasetItems(list);
      updateCatalogCount();
      if (catalogRenderedCount < catalogListItems.length) {
        list.insertAdjacentHTML('beforeend', `<div class="dataset-loading">${escapeHtml(t('data.loadingMore'))}</div>`);
      }
    }

    function maybeLoadMoreDatasets() {
      const list = $('dataset-list');
      if (catalogRenderedCount >= catalogListItems.length) return;
      if (list.scrollTop + list.clientHeight >= list.scrollHeight - 160) {
        appendDatasetBatch();
      }
    }

    function renderDatasets(items) {
      renderCatalogFacets();
      catalogListItems = items;
      catalogRenderedCount = 0;
      const list = $('dataset-list');
      if (activeDatasetId && !datasetById(activeDatasetId)) {
        activeDatasetId = null;
        closeDatasetDetail();
        syncSessionState('selected-dataset');
      }
      if (!items.length) {
        updateCatalogCount();
        list.innerHTML = `<div class="dataset-empty">${escapeHtml(t(catalogFavoriteFilter ? 'data.noFavorites' : 'data.noResults'))}</div>`;
        return;
      }
      list.innerHTML = '';
      appendDatasetBatch();
      list.scrollTop = 0;
    }

    async function requestCatalogLayer(datasetId) {
      const item = (Array.isArray(STATE.catalog) ? STATE.catalog : []).find(entry => entry.id === datasetId) || { id: datasetId };
      pendingDatasetIds.add(datasetId);
      failedDatasetIds.delete(datasetId);
      renderDatasets(filteredCatalog());
      showModeKey('mode.datasetBuilding', { dataset: datasetId }, true);
      logMsg('log.datasetBuilding', { dataset: datasetId });
      try {
        const response = await fetch('/api/layer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project: STATE.project,
            datasetId,
            catalogItem: item,
            recipe: defaultPreviewRecipeForDataset(item),
            aoi: currentProcessingAoi(),
            bounds: currentProcessingBounds(),
            startDate: STATE.startDate,
            endDate: STATE.endDate,
            cloudPct: STATE.cloudPct,
            zoom: map.getZoom(),
            center: [map.getCenter().lat, map.getCenter().lng],
          }),
        });
        const payload = await response.json().catch(() => ({ ok: false, error: response.statusText || 'request failed' }));
        if (!response.ok || !payload.ok || !payload.layer) {
          throw new Error(payload.error || `HTTP ${response.status}`);
        }
        addGeneratedLayer(payload.layer);
        showModeKey('mode.datasetAdded', { count: 1 });
        logMsg('log.datasetAdded', { dataset: datasetId });
        return true;
      } catch (error) {
        const message = error && error.message ? error.message : String(error);
        failedDatasetIds.set(datasetId, message);
        showModeKey('mode.datasetFailed', { message: message.slice(0, 90) }, true);
        logMsg('log.datasetFailed', { dataset: datasetId });
        return false;
      } finally {
        pendingDatasetIds.delete(datasetId);
        renderDatasets(filteredCatalog());
        syncToolState();
      }
    }

    async function importDatasetToMap(datasetId) {
      setActiveDataset(datasetId);
      const ids = datasetLayerIds(datasetId);
      if (!ids.length) {
        return requestCatalogLayer(datasetId);
      }
      ids.forEach(id => {
        const record = layerRegistry.get(id);
        if (!record) return;
        record.meta.shown = true;
        if (!map.hasLayer(record.tile)) record.tile.addTo(map);
      });
      renderLayers();
      setActiveLayer(ids[0]);
      showModeKey('mode.datasetAdded', { count: ids.length });
      logMsg('log.datasetAdded', { dataset: datasetId });
      return true;
    }

    async function refreshCatalogFromApi() {
      try {
        const response = await fetch('/api/catalog');
        if (!response.ok) return false;
        const payload = await response.json();
        if (!payload || !Array.isArray(payload.catalog) || !payload.catalog.length) return false;
        STATE.catalog = payload.catalog;
        STATE.catalogSource = payload.source || STATE.catalogSource;
        renderDatasets(filteredCatalog());
        logMsg('log.catalogLoaded', { count: STATE.catalog.length });
        return true;
      } catch {
        return false;
      }
    }

    function clearAoi() {
      STATE.aoi = null;
      STATE.bounds = null;
      STATE.aoiShown = true;
      removeOperationalLayerOrder(AOI_LAYER_ID);
      STATE.aoiStyle = normalizeAoiStyle(STATE.aoiStyle);
      persistAoi();
      renderAoiLayer();
      renderLayers();
      if (activeLayerId === AOI_LAYER_ID) setActiveLayer(STATE.layers[0]?.id || PRIMARY_BASEMAP_LAYER_ID, { reveal: false });
      syncSessionState('aoi-cleared');
      logMsg('log.aoiCleared');
      return true;
    }
    function removeLayer(id) {
      if (id === PRIMARY_BASEMAP_LAYER_ID) return false;
      if (id === AOI_LAYER_ID) return clearAoi();
      if (id === MEASUREMENTS_LAYER_ID) return clearMeasurements();
      const index = STATE.layers.findIndex(layer => layer.id === id);
      if (index < 0) return false;
      const [layer] = STATE.layers.splice(index, 1);
      removeOperationalLayerOrder(id);
      const record = layerRegistry.get(id);
      if (record && map.hasLayer(record.tile)) map.removeLayer(record.tile);
      layerRegistry.delete(id);
      let nextActive = null;
      if (activeLayerId === id) {
        nextActive = measurementsLayerModel()?.id || aoiLayerModel()?.id || STATE.layers.find(item => item.shown)?.id || STATE.layers[0]?.id || PRIMARY_BASEMAP_LAYER_ID;
        activeLayerId = null;
      }
      renderLayers();
      if (nextActive) setActiveLayer(nextActive, { reveal: false });
      else updateInspector();
      renderDatasets(filteredCatalog());
      logMsg('log.layerRemoved', { layer: layer.name });
      syncSessionState('layer-removed');
      return true;
    }

    function refreshLayer(id, options = {}) {
      if (!id) return false;
      if (id === PRIMARY_BASEMAP_LAYER_ID) {
        rebuildBasemapRegistry(currentBasemap);
        renderLayers();
        if (activeLayerId === id) updateInspector();
        syncSessionState(options.reason || 'basemap-refreshed');
        return true;
      }
      if (id === AOI_LAYER_ID) {
        if (!hasAoi()) return false;
        const layer = aoiLayerModel();
        renderAoiLayer();
        renderLayers();
        if (activeLayerId === AOI_LAYER_ID) updateInspector();
        logMsg('log.layerRefreshed', { layer: layer?.name || 'AOI' });
        syncSessionState(options.reason || 'aoi-refreshed');
        return true;
      }
      if (id === MEASUREMENTS_LAYER_ID) {
        if (!hasMeasurements()) return false;
        const layer = measurementsLayerModel();
        renderMeasurements();
        renderLayers();
        if (activeLayerId === MEASUREMENTS_LAYER_ID) updateInspector();
        logMsg('log.layerRefreshed', { layer: layer?.name || 'Measurements' });
        syncSessionState(options.reason || 'measurements-refreshed');
        return true;
      }
      const index = STATE.layers.findIndex(layer => layer.id === id);
      if (index < 0) return false;
      const meta = STATE.layers[index];
      if (meta.type === 'ee-restore-pending') {
        showModeKey('mode.datasetBuilding', { dataset: meta.dataset || meta.name }, true);
        rebuildProfileLayer(meta).then(restored => {
          if (restored) {
            renderLayers();
            setActiveLayer(id, { reveal: false });
            showModeKey('mode.datasetAdded', { count: 1 });
            syncSessionState('layer-restored');
          } else {
            showModeKey('mode.datasetFailed', { message: String(meta.dataset || meta.name).slice(0, 90) }, true);
          }
        });
        return true;
      }
      const previousRecord = layerRegistry.get(id);
      const shouldShow = previousRecord ? map.hasLayer(previousRecord.tile) : meta.shown !== false;
      if (previousRecord && map.hasLayer(previousRecord.tile)) map.removeLayer(previousRecord.tile);
      layerRegistry.delete(id);
      const token = Date.now();
      layerRefreshTokens.set(id, token);
      meta.shown = shouldShow;
      const refreshMeta = meta.tileUrl
        ? { ...meta, tileUrl: appendCacheBust(meta.tileUrl, token), shown: shouldShow }
        : { ...meta, shown: shouldShow };
      const tile = registerLayer(refreshMeta);
      if (shouldShow && tile && !map.hasLayer(tile)) tile.addTo(map);
      renderLayers();
      if (activeLayerId === id) setActiveLayer(id, { reveal: false });
      else updateInspector();
      logMsg('log.layerRefreshed', { layer: meta.name });
      syncSessionState(options.reason || 'layer-refreshed');
      return true;
    }

    function setLayerVisibility(id, shown, options = {}) {
      const nextShown = shown !== false;
      if (id === PRIMARY_BASEMAP_LAYER_ID) {
        const layer = basemapLayers.get(currentBasemap);
        if (!layer) return false;
        primaryBasemapShown = nextShown;
        if (nextShown) {
          setRasterLayerOpacity(layer, primaryBasemapOpacity);
          if (!map.hasLayer(layer)) layer.addTo(map);
          logMsg('log.layerOn', { layer: basemapDisplayName(currentBasemapMeta()) });
        } else {
          if (map.hasLayer(layer)) map.removeLayer(layer);
          logMsg('log.layerOff', { layer: basemapDisplayName(currentBasemapMeta()) });
        }
        renderLayers();
        if (options.activate !== false) setActiveLayer(PRIMARY_BASEMAP_LAYER_ID, { reveal: options.reveal !== false });
        else updateInspector();
        syncSessionState(options.reason || 'basemap-visibility');
        return true;
      }
      operationalMapOrderDirty = true;
      if (id === AOI_LAYER_ID) {
        if (!hasAoi()) return false;
        STATE.aoiShown = nextShown;
        STATE.aoiStyle = normalizeAoiStyle({ ...STATE.aoiStyle, shown: nextShown });
        renderAoiLayer();
        renderLayers();
        if (nextShown && options.activate !== false) {
          setActiveLayer(AOI_LAYER_ID, { reveal: options.reveal !== false });
        } else if (!nextShown && activeLayerId === AOI_LAYER_ID) {
          setActiveLayer(STATE.layers.find(item => item.shown)?.id || STATE.layers[0]?.id || PRIMARY_BASEMAP_LAYER_ID, { reveal: false });
        } else {
          updateInspector();
        }
        syncSessionState(options.reason || 'aoi-visibility');
        return true;
      }
      if (id === MEASUREMENTS_LAYER_ID) {
        if (!hasMeasurements()) return false;
        STATE.measurementsShown = nextShown;
        renderMeasurements();
        renderLayers();
        if (nextShown && options.activate !== false) {
          setActiveLayer(MEASUREMENTS_LAYER_ID, { reveal: options.reveal !== false });
        } else if (!nextShown && activeLayerId === MEASUREMENTS_LAYER_ID) {
          setActiveLayer(aoiLayerModel()?.id || STATE.layers.find(item => item.shown)?.id || STATE.layers[0]?.id || PRIMARY_BASEMAP_LAYER_ID, { reveal: false });
        } else {
          updateInspector();
        }
        syncSessionState(options.reason || 'measurements-visibility');
        return true;
      }
      const record = layerRegistry.get(id);
      if (!record) return false;
      const stateLayer = STATE.layers.find(item => item.id === id);
      if (stateLayer) stateLayer.shown = nextShown;
      record.meta.shown = nextShown;
      if (nextShown) {
        if (!map.hasLayer(record.tile)) record.tile.addTo(map);
        logMsg('log.layerOn', { layer: record.meta.name });
      } else {
        if (map.hasLayer(record.tile)) map.removeLayer(record.tile);
        logMsg('log.layerOff', { layer: record.meta.name });
      }
      renderLayers();
      if (nextShown && options.activate !== false) {
        setActiveLayer(id, { reveal: options.reveal !== false });
      } else if (!nextShown && activeLayerId === id) {
        setActiveLayer(measurementsLayerModel()?.id || aoiLayerModel()?.id || STATE.layers.find(item => item.shown)?.id || STATE.layers[0]?.id || PRIMARY_BASEMAP_LAYER_ID, { reveal: false });
      } else {
        updateInspector();
      }
      syncSessionState(options.reason || 'layer-visibility');
      return true;
    }

    function setLayerOpacity(id, value, options = {}) {
      const opacity = Math.max(0, Math.min(1, Number(value)));
      if (!Number.isFinite(opacity)) return false;
      if (id === PRIMARY_BASEMAP_LAYER_ID) {
        const layer = basemapLayers.get(currentBasemap);
        if (!layer) return false;
        primaryBasemapOpacity = opacity;
        setRasterLayerOpacity(layer, opacity);
        if (options.render !== false) renderLayers();
        if (activeLayerId === id) updateInspector();
        syncSessionState(options.reason || 'basemap-opacity');
        return true;
      }
      if (id === AOI_LAYER_ID) {
        if (!hasAoi()) return false;
        STATE.aoiStyle = normalizeAoiStyle({ ...STATE.aoiStyle, opacity });
        renderAoiLayer();
        if (options.render !== false) renderLayers();
        if (activeLayerId === id) updateInspector();
        syncSessionState(options.reason || 'aoi-opacity');
        return true;
      }
      if (id === MEASUREMENTS_LAYER_ID) {
        if (!hasMeasurements()) return false;
        STATE.measurementsOpacity = opacity;
        renderMeasurements();
        if (options.render !== false) renderLayers();
        if (activeLayerId === id) updateInspector();
        syncSessionState(options.reason || 'measurements-opacity');
        return true;
      }
      const record = layerRegistry.get(id);
      if (!record) return false;
      const stateLayer = STATE.layers.find(item => item.id === id);
      if (stateLayer) stateLayer.opacity = opacity;
      record.meta.opacity = opacity;
      if (typeof record.tile.setOpacity === 'function') {
        record.tile.setOpacity(opacity);
      } else if (typeof record.refresh === 'function') {
        record.refresh();
      }
      if (options.render !== false) renderLayers();
      if (activeLayerId === id) updateInspector();
      syncSessionState(options.reason || 'layer-opacity');
      return true;
    }

    function usableLayerBounds(bounds) {
      try {
        return Boolean(bounds && typeof bounds.isValid === 'function' && bounds.isValid());
      } catch {
        return false;
      }
    }
    function layerBoundsFromValue(value) {
      if (usableLayerBounds(value)) return value;
      const normalized = normalizeBounds(value);
      if (normalized) return L.latLngBounds(normalized);
      if (!Array.isArray(value) || value.length !== 4) return null;
      const [west, south, east, north] = value.map(Number);
      if (![west, south, east, north].every(Number.isFinite)) return null;
      if (west >= east || south >= north || west < -180 || east > 180 || south < -90 || north > 90) return null;
      return L.latLngBounds([[south, west], [north, east]]);
    }
    function renderedVectorBounds(record) {
      const candidates = [record?.tile?.__vectorOverlay, record?.tile];
      for (const candidate of candidates) {
        if (!candidate || typeof candidate.getBounds !== 'function') continue;
        try {
          const bounds = candidate.getBounds();
          if (usableLayerBounds(bounds)) return bounds;
        } catch {}
      }
      const layers = typeof record?.tile?.getLayers === 'function' ? record.tile.getLayers() : [];
      if (!layers.length) return null;
      try {
        const bounds = L.featureGroup(layers).getBounds();
        return usableLayerBounds(bounds) ? bounds : null;
      } catch {
        return null;
      }
    }
    function measurementsLayerBounds() {
      const points = STATE.measurements.flatMap(item => [normalizeLatLngPair(item.start), normalizeLatLngPair(item.end)]).filter(Boolean);
      if (!points.length) return null;
      const bounds = L.latLngBounds(points);
      return usableLayerBounds(bounds) ? bounds : null;
    }
    function normalizedLayerZoom(value, fallback = 18) {
      const zoom = Number(value);
      return Number.isFinite(zoom) ? Math.max(0, Math.min(22, zoom)) : fallback;
    }
    function layerModelById(id) {
      if (id === PRIMARY_BASEMAP_LAYER_ID) return primaryBasemapLayerModel();
      if (id === AOI_LAYER_ID) return aoiLayerModel();
      if (id === MEASUREMENTS_LAYER_ID) return measurementsLayerModel();
      return STATE.layers.find(layer => layer.id === id) || null;
    }
    async function basemapLayerExtent(meta) {
      if (!meta) return null;
      const explicit = layerBoundsFromValue(meta.bounds) || cogBasemapBounds(meta);
      if (usableLayerBounds(explicit)) {
        return { bounds: explicit, maxZoom: Math.min(normalizedLayerZoom(meta.maxNativeZoom ?? meta.maxZoom), 18) };
      }
      if (meta.custom && meta.type === 'pmtiles') {
        const inspection = await inspectPmtilesArchive(meta, { requireVisibleTile: false });
        if (!inspection.ok) return null;
        const header = inspection.header || {};
        const values = [header.minLon, header.minLat, header.maxLon, header.maxLat].map(Number);
        const bounds = layerBoundsFromValue(values);
        if (!usableLayerBounds(bounds)) return null;
        return { bounds, maxZoom: Math.min(normalizedLayerZoom(header.maxZoom ?? meta.maxNativeZoom), 18) };
      }
      if (meta.custom && meta.type === 'cog') return null;
      return { bounds: L.latLngBounds([[-85.05112878, -180], [85.05112878, 180]]), maxZoom: 18 };
    }
    async function layerExtentById(id) {
      if (id === PRIMARY_BASEMAP_LAYER_ID) return basemapLayerExtent(currentBasemapMeta());
      if (id === AOI_LAYER_ID) {
        const bounds = layerBoundsFromValue(STATE.aoi?.bounds);
        return usableLayerBounds(bounds) ? { bounds, maxZoom: 18 } : null;
      }
      if (id === MEASUREMENTS_LAYER_ID) {
        const bounds = measurementsLayerBounds();
        return usableLayerBounds(bounds) ? { bounds, maxZoom: 18 } : null;
      }
      const layer = STATE.layers.find(item => item.id === id);
      if (!layer) return null;
      if (isBasemapOverlayLayer(layer)) return basemapLayerExtent(basemapMetaById(layer.sourceId));
      const record = layerRegistry.get(id);
      if (isLocalVectorLayer(layer) && record?.tile?.__vectorReady) await record.tile.__vectorReady;
      const rendered = renderedVectorBounds(record);
      if (usableLayerBounds(rendered)) return { bounds: rendered, maxZoom: 18 };
      const candidates = [
        layer.aoi?.bounds,
        layer.bounds,
        layer.recipe?.aoi?.bounds,
        layer.recipe?.bounds,
        layer.summary?.bounds,
      ];
      for (const candidate of candidates) {
        const bounds = layerBoundsFromValue(candidate);
        if (usableLayerBounds(bounds)) return { bounds, maxZoom: 18 };
      }
      return null;
    }
    async function zoomToLayer(id, options = {}) {
      const layerId = String(id || activeLayerId || '');
      const layer = layerModelById(layerId);
      if (!layer) return false;
      showModeKey('mode.layerZooming', { layer: layer.name }, true);
      let extent = null;
      try {
        extent = await layerExtentById(layerId);
      } catch {
        extent = null;
      }
      if (!extent || !usableLayerBounds(extent.bounds)) {
        showModeKey('mode.layerExtentUnavailable', { layer: layer.name });
        logMsg('log.layerExtentUnavailable', { layer: layer.name });
        return false;
      }
      const rawPadding = Number(options.padding ?? 36);
      const padding = Number.isFinite(rawPadding) ? Math.max(0, Math.min(120, rawPadding)) : 36;
      map.fitBounds(extent.bounds, {
        padding: [padding, padding],
        maxZoom: normalizedLayerZoom(options.maxZoom ?? extent.maxZoom),
        animate: options.animate !== false,
        duration: 0.35,
      });
      setActiveLayer(layerId, { reveal: false });
      updateScaleLine();
      showModeKey('mode.layerZoomed', { layer: layer.name });
      logMsg('log.layerZoomed', { layer: layer.name });
      return true;
    }

    function selectLayer(id, options = {}) {
      if (id === PRIMARY_BASEMAP_LAYER_ID) {
        setActiveLayer(PRIMARY_BASEMAP_LAYER_ID, { reveal: options.reveal !== false });
        syncSessionState(options.reason || 'layer-selected');
        return true;
      }
      if (id === AOI_LAYER_ID) {
        if (!hasAoi()) return false;
        setActiveLayer(AOI_LAYER_ID, { reveal: options.reveal !== false });
        syncSessionState(options.reason || 'layer-selected');
        return true;
      }
      if (id === MEASUREMENTS_LAYER_ID) {
        if (!hasMeasurements()) return false;
        setActiveLayer(MEASUREMENTS_LAYER_ID, { reveal: options.reveal !== false });
        syncSessionState(options.reason || 'layer-selected');
        return true;
      }
      if (!layerRegistry.has(id)) return false;
      setActiveLayer(id, { reveal: options.reveal !== false });
      syncSessionState(options.reason || 'layer-selected');
      return true;
    }
    async function applyLayerPreset(id, presetId) {
      const record = layerRegistry.get(id);
      if (!record) return false;
      const preset = stylePresetForLayer(record.meta, presetId);
      const profile = layerStyleProfile(record.meta);
      if (isLocalVectorLayer(record.meta)) {
        record.meta = {
          ...record.meta,
          styleProfile: profile,
          stylePreset: preset.id,
          legend: preset.legend || record.meta.legend,
        };
        const stateIndex = STATE.layers.findIndex(layer => layer.id === id);
        if (stateIndex >= 0) STATE.layers[stateIndex] = record.meta;
        if (typeof record.refresh === 'function') record.refresh();
        visualPreferences[profile] = preset.id;
        renderLayers();
        updateInspector();
        syncSessionState('layer-style');
        return true;
      }
      showModeKey('mode.styleBuilding', { layer: record.meta.name }, true);
      try {
        const response = await fetch('/api/layer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project: STATE.project,
            datasetId: record.meta.dataset,
            catalogItem: { id: record.meta.dataset, label: record.meta.name, type: record.meta.type },
            recipe: record.meta.recipe || null,
            aoi: record.meta.aoi || currentProcessingAoi(),
            bounds: record.meta.bounds || currentProcessingBounds(),
            startDate: record.meta.summary?.startDate || STATE.startDate,
            endDate: record.meta.summary?.endDate || STATE.endDate,
            cloudPct: record.meta.summary?.cloudPct ?? STATE.cloudPct,
            styleProfile: profile,
            visParams: sanitizeVisParams(preset.visParams),
            legend: preset.legend,
            stylePreset: preset.id,
          }),
        });
        const payload = await response.json().catch(() => ({ ok: false, error: response.statusText || 'request failed' }));
        if (!response.ok || !payload.ok || !payload.layer) {
          throw new Error(payload.error || `HTTP ${response.status}`);
        }
        const wasShown = map.hasLayer(record.tile);
        if (wasShown) map.removeLayer(record.tile);
        const nextMeta = {
          ...record.meta,
          ...payload.layer,
          id: record.meta.id,
          shown: record.meta.shown,
          opacity: record.meta.opacity,
          styleProfile: profile,
          stylePreset: preset.id,
          visParams: sanitizeVisParams(preset.visParams),
          legend: preset.legend || payload.layer.legend || record.meta.legend,
        };
        record.meta = nextMeta;
        const stateIndex = STATE.layers.findIndex(layer => layer.id === id);
        if (stateIndex >= 0) STATE.layers[stateIndex] = nextMeta;
        record.tile = L.tileLayer(nextMeta.tileUrl, { opacity: nextMeta.opacity, attribution: 'Google Earth Engine' });
        if (wasShown || nextMeta.shown) record.tile.addTo(map);
        visualPreferences[profile] = preset.id;
        renderLayers();
        updateInspector();
        showModeKey('mode.styleApplied', { layer: nextMeta.name });
        logMsg('log.layerStyled', { layer: nextMeta.name });
        syncSessionState('layer-style');
        return true;
      } catch (error) {
        const message = error && error.message ? error.message : String(error);
        showModeKey('mode.styleFailed', { message: message.slice(0, 90) }, true);
        logMsg('log.layerStyleFailed', { layer: record.meta.name });
        renderLayers();
        return false;
      }
    }
    function renderLayers() {
      const operationalModels = operationalLayerModels();
      const primaryModel = primaryBasemapLayerModel();
      const models = [...operationalModels, primaryModel];
      $('layer-count').textContent = t('pill.layersWithBasemap', { count: operationalModels.length });
      const layerCardHtml = layer => {
        const kind = layerKind(layer);
        const isAoi = layer.id === AOI_LAYER_ID;
        const isMeasurements = layer.id === MEASUREMENTS_LAYER_ID;
        const isPrimaryBasemap = layer.id === PRIMARY_BASEMAP_LAYER_ID;
        const isBasemapOverlay = isBasemapOverlayLayer(layer);
        const isBasemapLayer = isPrimaryBasemap || isBasemapOverlay;
        const canReorder = isReorderableLayer(layer.id);
        const dragAttrs = canReorder ? ' data-reorderable="true"' : '';
        const dragHandle = canReorder ? `<span class="layer-drag-handle" draggable="true" title="${escapeHtml(t('tool.dragLayer'))}" aria-label="${escapeHtml(t('tool.dragLayer'))}" role="img">__EASYGEE_ICON_GRIP__</span>` : '';
        const presets = isAoi || isBasemapLayer ? [] : stylePresetOptions(layer);
        let selectedPreset = layer.stylePreset || visualPreferences[layerStyleProfile(layer)] || 'default';
        const preset = isAoi || isBasemapLayer ? null : stylePresetForLayer(layer, selectedPreset);
        if (preset) selectedPreset = preset.id;
        const palette = isAoi ? [STATE.aoiStyle.color] : isMeasurements ? [DEFAULT_MEASUREMENTS_STYLE.color] : (preset?.visParams?.palette || layer.visParams?.palette || []);
        const styleControl = isBasemapLayer
          ? ''
          : isAoi
          ? `<div class="layer-style-row"><span>${escapeHtml(t('label.color'))}</span><input type="color" data-action="aoi-color" value="${escapeHtml(STATE.aoiStyle.color)}"></div>`
          : isMeasurements
            ? `<div class="layer-style-row"><span>${escapeHtml(t('measurements.count'))}</span><span>${escapeHtml(t('measurements.summary', { count: layer.summary.count, total: layer.summary.totalLabel }))}</span></div>${palettePreviewHtml(palette)}`
            : `<div class="layer-style-row"><span>${escapeHtml(t('label.palette'))}</span><select data-action="style-preset">${presets.map(item => `<option value="${escapeHtml(item.id)}" ${item.id === selectedPreset ? 'selected' : ''}>${escapeHtml(item.label)}</option>`).join('')}</select></div>${palettePreviewHtml(palette)}`;
        const removeTitle = isAoi ? t('tool.clearAoi') : isMeasurements ? t('tool.clearMeasurements') : t('tool.removeLayer');
        const refreshTitle = t('tool.refreshLayer');
        const zoomButton = `<button class="layer-action icon-btn" data-action="zoom" title="${escapeHtml(t('tool.zoomToLayer'))}" aria-label="${escapeHtml(t('tool.zoomToLayer'))}" type="button">__EASYGEE_ICON_ZOOM_LAYER__</button>`;
        const styleButton = isMeasurements || isBasemapLayer ? '' : `<button class="layer-action icon-btn" data-action="style-focus" title="${escapeHtml(t('tool.styleLayer'))}" aria-label="${escapeHtml(t('tool.styleLayer'))}" type="button">__EASYGEE_ICON_STYLE__</button>`;
        const sourceButton = isBasemapLayer ? `<button class="layer-action icon-btn" data-action="source" title="${escapeHtml(t('tool.basemapSource'))}" aria-label="${escapeHtml(t('tool.basemapSource'))}" type="button">__EASYGEE_ICON_INFO__</button>` : '';
        const refreshButton = isPrimaryBasemap ? '' : `<button class="layer-action icon-btn" data-action="refresh" title="${escapeHtml(refreshTitle)}" aria-label="${escapeHtml(refreshTitle)}" type="button">__EASYGEE_ICON_REFRESH__</button>`;
        const removeButton = isPrimaryBasemap ? '' : `<button class="layer-action icon-btn danger" data-action="remove" title="${escapeHtml(removeTitle)}" aria-label="${escapeHtml(removeTitle)}" type="button">__EASYGEE_ICON_TRASH__</button>`;
        const itemClass = isPrimaryBasemap ? ' primary-basemap' : isBasemapOverlay ? ' basemap-overlay' : '';
        return `
        <div class="layer-item${itemClass}${layer.id === activeLayerId ? ' active' : ''}" data-layer="${escapeHtml(layer.id)}"${dragAttrs}>
          <div class="layer-top">
            <input type="checkbox" data-action="toggle" ${layer.shown ? 'checked' : ''} aria-label="${escapeHtml(layer.name)}">
            <div class="layer-copy">
              <div class="layer-title-row">${dragHandle}<span class="type-dot ${kind.className}">${kind.label}</span><div class="layer-name">${escapeHtml(layer.name)}</div></div>
              <div class="layer-dataset">${escapeHtml(layer.dataset)}</div>
            </div>
            <div class="layer-actions">
              ${zoomButton}
              ${styleButton}
              ${sourceButton}
              ${refreshButton}
              ${removeButton}
            </div>
          </div>
          ${styleControl}
          <div class="opacity-row">
            <span>${escapeHtml(t('label.opacity'))}</span>
            <input type="range" min="0" max="1" step="0.01" value="${layer.opacity}" data-action="opacity">
            <span data-opacity-label>${Math.round(layer.opacity * 100)}%</span>
          </div>
        </div>
      `;
      };
      const operationalHtml = operationalModels.length
        ? operationalModels.map(layerCardHtml).join('')
        : `<div class="empty-list">${escapeHtml(t('layers.emptyOperational'))}</div>`;
      $('layer-list').innerHTML = `
        <section class="layer-stack-group">
          <div class="layer-group-heading">${escapeHtml(t('section.operationalLayers'))}<span>${escapeHtml(t('section.layerReorderHint'))} · ${escapeHtml(t('pill.layers', { count: operationalModels.length }))}</span></div>
          ${operationalHtml}
        </section>
        <section class="layer-stack-group">
          <div class="layer-group-heading">${escapeHtml(t('section.primaryBasemap'))}<span>${escapeHtml(t('section.primaryBasemapHint'))}</span></div>
          ${layerCardHtml(primaryModel)}
        </section>`;
      document.querySelectorAll('.layer-item').forEach(item => {
        const id = item.dataset.layer;
        if (item.dataset.reorderable === 'true') {
          const handle = item.querySelector('.layer-drag-handle');
          handle?.addEventListener('dragstart', event => {
            draggedLayerId = id;
            item.classList.add('dragging');
            if (event.dataTransfer) {
              event.dataTransfer.effectAllowed = 'move';
              event.dataTransfer.setData('text/plain', id);
            }
          });
          item.addEventListener('dragover', event => {
            if (!draggedLayerId || draggedLayerId === id || !isReorderableLayer(id)) return;
            event.preventDefault();
            if (event.dataTransfer) event.dataTransfer.dropEffect = 'move';
            item.classList.add('drag-over');
          });
          item.addEventListener('dragleave', () => item.classList.remove('drag-over'));
          item.addEventListener('drop', event => {
            event.preventDefault();
            const sourceId = draggedLayerId || event.dataTransfer?.getData('text/plain');
            item.classList.remove('drag-over');
            if (sourceId) reorderLayer(sourceId, id);
            draggedLayerId = null;
          });
          handle?.addEventListener('dragend', () => {
            draggedLayerId = null;
            item.classList.remove('dragging', 'drag-over');
          });
        }
        item.addEventListener('click', event => {
          if (event.target.closest('[data-action]')) return;
          setActiveLayer(id);
        });
        item.querySelector('[data-action="toggle"]').addEventListener('change', event => {
          const reason = id === PRIMARY_BASEMAP_LAYER_ID ? 'basemap-visibility' : id === AOI_LAYER_ID ? 'aoi-visibility' : id === MEASUREMENTS_LAYER_ID ? 'measurements-visibility' : 'layer-toggle';
          setLayerVisibility(id, event.target.checked, { reason });
        });
        item.querySelector('[data-action="zoom"]')?.addEventListener('click', async event => {
          event.stopPropagation();
          const button = event.currentTarget;
          button.disabled = true;
          try {
            await zoomToLayer(id);
          } finally {
            button.disabled = false;
          }
        });
        item.querySelector('[data-action="opacity"]').addEventListener('input', event => {
          const value = Number(event.target.value);
          const reason = id === PRIMARY_BASEMAP_LAYER_ID ? 'basemap-opacity' : id === AOI_LAYER_ID ? 'aoi-style' : id === MEASUREMENTS_LAYER_ID ? 'measurements-opacity' : 'layer-opacity';
          if (!setLayerOpacity(id, value, { render: false, reason })) return;
          item.querySelector('[data-opacity-label]').textContent = `${Math.round(value * 100)}%`;
        });
        item.querySelector('[data-action="remove"]')?.addEventListener('click', event => {
          event.stopPropagation();
          removeLayer(id);
        });
        item.querySelector('[data-action="refresh"]')?.addEventListener('click', event => {
          event.stopPropagation();
          refreshLayer(id);
        });
        item.querySelector('[data-action="source"]')?.addEventListener('click', event => {
          event.stopPropagation();
          const layer = models.find(model => model.id === id);
          setActiveLayer(id, { reveal: false });
          setBasemapSourceOpen(true, layer?.sourceId || currentBasemap);
        });
        item.querySelector('[data-action="style-focus"]')?.addEventListener('click', event => {
          event.stopPropagation();
          setActiveLayer(id);
          item.querySelector('[data-action="aoi-color"], [data-action="style-preset"]')?.focus();
        });
        const colorInput = item.querySelector('[data-action="aoi-color"]');
        if (colorInput) {
          colorInput.addEventListener('input', event => {
            const color = event.target.value;
            if (!isHexColor(color)) return;
            STATE.aoiStyle = normalizeAoiStyle({ ...STATE.aoiStyle, color, fillColor: color });
            renderAoiLayer();
            renderLayers();
            setActiveLayer(AOI_LAYER_ID, { reveal: false });
            syncSessionState('aoi-style');
          });
        }
        const styleSelect = item.querySelector('[data-action="style-preset"]');
        if (styleSelect) {
          styleSelect.addEventListener('change', event => {
            applyLayerPreset(id, event.target.value);
          });
        }
      });
      syncLayerOrderToMap();
    }

    function setActiveLayer(id, options = {}) {
      activeLayerId = id || null;
      document.querySelectorAll('.layer-item').forEach(item => {
        item.classList.toggle('active', item.dataset.layer === id);
      });
      updateInspector();
      if (activeLayerId && options.reveal !== false) revealActiveBadge();
    }

    function updateInspector() {
      if (activeLayerId === PRIMARY_BASEMAP_LAYER_ID) {
        const layer = primaryBasemapLayerModel();
        $('active-name').textContent = layer.name;
        $('active-dataset').textContent = layerBadgeDataset(layer.dataset);
        setActiveBadgeLabel(layerBadgeTitle(layer.name, layer.dataset));
        $('detail-name').textContent = layer.name;
        $('detail-dataset').textContent = layer.dataset;
        $('detail-type').textContent = t('basemap.primaryRole');
        $('detail-recipe').textContent = '-';
        $('detail-opacity').textContent = `${Math.round(layer.opacity * 100)}%`;
        $('legend').innerHTML = `<div class="empty-list">${escapeHtml(t('section.primaryBasemapHint'))}</div>`;
        return;
      }
      if (activeLayerId === AOI_LAYER_ID && hasAoi()) {
        const layer = aoiLayerModel();
        $('active-name').textContent = layer.name;
        $('active-dataset').textContent = layerBadgeDataset(layer.dataset);
        const badgeLabel = layerBadgeTitle(layer.name, layer.dataset);
        setActiveBadgeLabel(badgeLabel);
        $('detail-name').textContent = layer.name;
        $('detail-dataset').textContent = layer.dataset;
        $('detail-type').textContent = 'AOI';
        $('detail-recipe').textContent = '-';
        $('detail-opacity').textContent = `${Math.round(layer.opacity * 100)}%`;
        $('legend').innerHTML = `<div class="legend-row"><span class="swatch" style="background:${escapeHtml(STATE.aoiStyle.color)}"></span><span>AOI</span></div>`;
        return;
      }
      if (activeLayerId === MEASUREMENTS_LAYER_ID && hasMeasurements()) {
        const layer = measurementsLayerModel();
        const summary = layer.summary;
        $('active-name').textContent = layer.name;
        $('active-dataset').textContent = layerBadgeDataset(layer.dataset);
        const badgeLabel = layerBadgeTitle(layer.name, layer.dataset);
        setActiveBadgeLabel(badgeLabel);
        $('detail-name').textContent = layer.name;
        $('detail-dataset').textContent = t('measurements.summary', { count: summary.count, total: summary.totalLabel });
        $('detail-type').textContent = 'Measurements';
        $('detail-recipe').textContent = '-';
        $('detail-opacity').textContent = `${Math.round(layer.opacity * 100)}%`;
        $('legend').innerHTML = `<div class="legend-row"><span class="swatch" style="background:${escapeHtml(DEFAULT_MEASUREMENTS_STYLE.color)}"></span><span>${escapeHtml(t('measurements.legend'))}</span></div>`;
        return;
      }
      const record = layerRegistry.get(activeLayerId);
      if (!record) {
        const noLayer = t('layer.none');
        const basemapLabel = fullBasemapBadge();
        $('active-name').textContent = 'EasyGEE';
        $('active-dataset').textContent = basemapLabel;
        const badgeLabel = `${t('badge.noLayer')} - ${basemapLabel}`;
        setActiveBadgeLabel(badgeLabel);
        $('detail-name').textContent = noLayer;
        $('detail-dataset').textContent = displayBasemapSource();
        $('detail-type').textContent = '-';
        $('detail-recipe').textContent = '-';
        $('detail-opacity').textContent = '-';
        $('legend').innerHTML = `<div class="empty-list">${escapeHtml(noLayer)}</div>`;
        return;
      }
      const layer = record.meta;
      $('active-name').textContent = layer.name;
      $('active-dataset').textContent = layerBadgeDataset(layer.dataset);
      const badgeLabel = layerBadgeTitle(layer.name, layer.dataset);
      setActiveBadgeLabel(badgeLabel);
      $('detail-name').textContent = layer.name;
      $('detail-dataset').textContent = layer.dataset;
      $('detail-type').textContent = isBasemapOverlayLayer(layer) ? t('basemap.overlayRole') : layer.type;
      $('detail-recipe').textContent = recipeSummary(layer.recipe);
      $('detail-opacity').textContent = `${Math.round(layer.opacity * 100)}%`;
      $('legend').innerHTML = (layer.legend || []).map(([color, label]) => `
        <div class="legend-row"><span class="swatch" style="background:${escapeHtml(color)}"></span><span>${escapeHtml(label)}</span></div>
      `).join('') || (isBasemapOverlayLayer(layer) ? `<div class="empty-list">${escapeHtml(layer.dataset)}</div>` : '');
    }

    function boundsFromCorners(a, b) {
      const south = Math.min(a.lat, b.lat);
      const north = Math.max(a.lat, b.lat);
      const west = Math.min(a.lng, b.lng);
      const east = Math.max(a.lng, b.lng);
      return [[south, west], [north, east]];
    }
    function boundsTooSmall(bounds) {
      return Math.abs(bounds[1][0] - bounds[0][0]) < 0.000001 || Math.abs(bounds[1][1] - bounds[0][1]) < 0.000001;
    }
    function boundsLabel(bounds) {
      return `${fmt(bounds[0][0], 4)}, ${fmt(bounds[0][1], 4)} - ${fmt(bounds[1][0], 4)}, ${fmt(bounds[1][1], 4)}`;
    }
    function closeFloatingPanels() {
      quotaFocus = false;
      document.querySelector('.data-panel').classList.remove('open');
      document.querySelector('.upload-panel').classList.remove('open');
      document.querySelector('.layers-panel').classList.remove('open');
      document.querySelector('.right').classList.remove('open');
      document.querySelector('.bottom').classList.remove('open');
      document.querySelector('.basemap-panel').classList.remove('open');
    }
    function clearAoiPreview() {
      drawAoiLayer.clearLayers();
      drawAoiPreview = null;
      drawPolygonPoints = [];
    }
    function stopDrawAoiMode(announce = true) {
      const wasActive = drawAoiMode || drawAoiStart || drawPolygonMode || drawPolygonPoints.length;
      drawAoiMode = false;
      drawPolygonMode = false;
      drawAoiStart = null;
      if (polygonDoubleClickZoomWasEnabled) map.doubleClickZoom.enable();
      polygonDoubleClickZoomWasEnabled = false;
      clearAoiPreview();
      map.getContainer().classList.remove('draw-aoi', 'draw-polygon');
      syncToolState();
      if (announce && wasActive) {
        showModeKey('mode.aoiOff', {}, false);
        logMsg('log.aoiOff');
      }
    }
    function startRectangleAoiMode() {
      if (drawAoiMode && !drawPolygonMode) {
        stopDrawAoiMode(true);
        return;
      }
      measureMode = false;
      measurePoints = [];
      measureDraftLayer.clearLayers();
      closeFloatingPanels();
      stopDrawAoiMode(false);
      drawAoiMode = true;
      drawAoiStart = null;
      map.getContainer().classList.add('draw-aoi');
      syncToolState();
      showModeKey('mode.aoiStart', {}, true);
      logMsg('log.aoiOn');
    }
    function startPolygonAoiMode() {
      if (drawPolygonMode) {
        stopDrawAoiMode(true);
        return;
      }
      measureMode = false;
      measurePoints = [];
      measureDraftLayer.clearLayers();
      closeFloatingPanels();
      stopDrawAoiMode(false);
      drawPolygonMode = true;
      drawAoiMode = false;
      drawPolygonPoints = [];
      polygonDoubleClickZoomWasEnabled = map.doubleClickZoom.enabled();
      if (polygonDoubleClickZoomWasEnabled) map.doubleClickZoom.disable();
      map.getContainer().classList.add('draw-polygon');
      syncToolState();
      showModeKey('mode.polygonStart', {}, true);
      logMsg('log.aoiOn');
    }
    function toggleDrawAoiMode(polygon = false) {
      if (polygon) startPolygonAoiMode();
      else startRectangleAoiMode();
    }
    function updateAoi(aoi, options = { persist: true }) {
      const hadAoi = hasAoi();
      const normalized = normalizeAoi(aoi);
      if (!normalized) return false;
      STATE.aoi = normalized;
      STATE.bounds = normalized.bounds;
      STATE.aoiShown = true;
      if (!hadAoi) placeOperationalLayer(AOI_LAYER_ID, 'front');
      renderAoiLayer();
      renderLayers();
      setActiveLayer(AOI_LAYER_ID, { reveal: false });
      if (options.persist !== false) persistAoi();
      syncSessionState('aoi');
      return true;
    }
    function updateAoiBounds(bounds) {
      return updateAoi(aoiFromBounds(bounds));
    }
    function handleDrawAoiMove(event) {
      if (!drawAoiMode || !drawAoiStart) return;
      const bounds = boundsFromCorners(drawAoiStart, event.latlng);
      if (!drawAoiPreview) {
        drawAoiPreview = L.rectangle(bounds, {
          color: '#16734d',
          weight: 2,
          dashArray: '6 5',
          fill: true,
          fillColor: '#16734d',
          fillOpacity: 0.12,
          interactive: false,
        }).addTo(drawAoiLayer);
      } else {
        drawAoiPreview.setBounds(bounds);
      }
    }
    function renderPolygonPreview(nextPoint = null) {
      if (!drawPolygonMode) return;
      drawAoiLayer.clearLayers();
      drawPolygonPoints.forEach(point => {
        L.circleMarker(point, {
          radius: 4,
          color: '#16734d',
          fillColor: '#16734d',
          fillOpacity: 1,
          weight: 2,
          interactive: false,
        }).addTo(drawAoiLayer);
      });
      const previewPoints = nextPoint ? [...drawPolygonPoints, nextPoint] : drawPolygonPoints;
      if (previewPoints.length >= 2) {
        L.polyline(previewPoints, { color: '#16734d', weight: 2, dashArray: '6 5', interactive: false }).addTo(drawAoiLayer);
      }
      if (previewPoints.length >= 3) {
        L.polygon(previewPoints, {
          color: '#16734d',
          weight: 2,
          dashArray: '6 5',
          fill: true,
          fillColor: '#16734d',
          fillOpacity: 0.10,
          interactive: false,
        }).addTo(drawAoiLayer);
      }
    }
    function handleDrawPolygonMove(event) {
      if (!drawPolygonMode) return;
      renderPolygonPreview(event.latlng);
    }
    function handleDrawPolygonClick(event) {
      if (!drawPolygonMode) return false;
      drawPolygonPoints.push(event.latlng);
      renderPolygonPreview();
      showModeKey('mode.polygonVertex', { count: drawPolygonPoints.length }, true);
      return true;
    }
    function finishPolygonAoi() {
      if (!drawPolygonMode) return false;
      if (drawPolygonPoints.length < 3) {
        showModeKey('mode.polygonTooSmall', {}, true);
        return true;
      }
      const coordinates = drawPolygonPoints.map(point => [point.lat, point.lng]);
      updateAoi({ type: 'polygon', coordinates, coordinateOrder: 'latlng' });
      const bounds = STATE.aoi.bounds;
      stopDrawAoiMode(false);
      showModeKey('mode.aoiDone', {}, false);
      logMsg('log.aoiDrawn', { bounds: boundsLabel(bounds) });
      return true;
    }
    function handleDrawAoiClick(event) {
      if (!drawAoiMode) return false;
      if (!drawAoiStart) {
        drawAoiStart = event.latlng;
        L.circleMarker(drawAoiStart, {
          radius: 4,
          color: '#16734d',
          fillColor: '#16734d',
          fillOpacity: 1,
          weight: 2,
          interactive: false,
        }).addTo(drawAoiLayer);
        showModeKey('mode.aoiCorner', {}, true);
        return true;
      }
      const bounds = boundsFromCorners(drawAoiStart, event.latlng);
      if (boundsTooSmall(bounds)) {
        showModeKey('mode.aoiTooSmall', {}, true);
        return true;
      }
      updateAoiBounds(bounds);
      stopDrawAoiMode(false);
      showModeKey('mode.aoiDone', {}, false);
      logMsg('log.aoiDrawn', { bounds: boundsLabel(bounds) });
      return true;
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }
    function installPanelResizers() {
      const configs = [
        { selector: '.data-panel', anchor: 'left', minWidth: 360, minHeight: 220, handles: ['e', 's', 'se'] },
        { selector: '.layers-panel', anchor: 'left', minWidth: 260, minHeight: 220, handles: ['e', 's', 'se'] },
        { selector: '.right', anchor: 'right', minWidth: 260, minHeight: 220, handles: ['w', 's', 'sw'] },
        { selector: '.bottom', anchor: 'right', minWidth: 300, minHeight: 260, handles: ['w', 's', 'sw'] },
        { selector: '.basemap-panel', anchor: 'left', minWidth: 220, minHeight: 132, handles: ['e', 's', 'se'] },
        { selector: '.upload-panel', anchor: 'left', minWidth: 320, minHeight: 230, handles: ['e', 's', 'se'] },
      ];
      configs.forEach(config => {
        const panel = document.querySelector(config.selector);
        if (!panel || panel.dataset.resizableReady) return;
        panel.dataset.resizableReady = 'true';
        panel.classList.add('resizable-panel');
        config.handles.forEach(edge => {
          const handle = document.createElement('span');
          handle.className = `panel-resize-handle ${edge.length === 1 ? `edge-${edge}` : `corner-${edge}`}`;
          handle.setAttribute('aria-hidden', 'true');
          handle.addEventListener('pointerdown', event => startPanelResize(event, panel, config, edge));
          panel.appendChild(handle);
        });
      });
    }
    function startPanelResize(event, panel, config, edge) {
      event.preventDefault();
      event.stopPropagation();
      const rect = panel.getBoundingClientRect();
      const startX = event.clientX;
      const startY = event.clientY;
      const startWidth = rect.width;
      const startHeight = rect.height;
      const rightGap = Math.max(0, window.innerWidth - rect.right);
      const leftGap = Math.max(0, rect.left);
      const maxWidth = config.anchor === 'right'
        ? Math.max(config.minWidth, rect.right - 8)
        : Math.max(config.minWidth, window.innerWidth - rect.left - 8);
      const maxHeight = Math.max(config.minHeight, window.innerHeight - rect.top - 8);
      panel.setPointerCapture?.(event.pointerId);
      function move(moveEvent) {
        const dx = moveEvent.clientX - startX;
        const dy = moveEvent.clientY - startY;
        if (edge.includes('e') || edge.includes('w')) {
          const rawWidth = edge.includes('w') ? startWidth - dx : startWidth + dx;
          panel.style.width = `${Math.round(clamp(rawWidth, config.minWidth, maxWidth))}px`;
          panel.style.maxWidth = 'none';
          if (config.anchor === 'right') {
            panel.style.right = `${rightGap}px`;
            panel.style.left = 'auto';
          } else {
            panel.style.left = `${leftGap}px`;
          }
        }
        if (edge.includes('s')) {
          const rawHeight = startHeight + dy;
          panel.style.height = `${Math.round(clamp(rawHeight, config.minHeight, maxHeight))}px`;
          panel.style.maxHeight = 'none';
          panel.style.bottom = 'auto';
        }
      }
      function up(upEvent) {
        panel.releasePointerCapture?.(upEvent.pointerId);
        window.removeEventListener('pointermove', move);
        window.removeEventListener('pointerup', up);
      }
      window.addEventListener('pointermove', move);
      window.addEventListener('pointerup', up, { once: true });
    }

    function renderMeasurements() {
      measureLayer.clearLayers();
      if (STATE.measurementsShown === false) {
        syncLayerOrderToMap();
        return;
      }
      const opacity = normalizeMeasurementsOpacity(STATE.measurementsOpacity);
      (STATE.measurements || []).forEach(item => {
        const start = L.latLng(item.start[0], item.start[1]);
        const end = L.latLng(item.end[0], item.end[1]);
        L.polyline([start, end], { color: DEFAULT_MEASUREMENTS_STYLE.color, weight: DEFAULT_MEASUREMENTS_STYLE.weight, opacity, dashArray: '6 5' })
          .bindTooltip(item.lengthLabel || formatDistance(item.lengthMeters), {
            permanent: true,
            direction: 'center',
            className: 'measure-label',
            opacity,
          })
          .addTo(measureLayer);
        [start, end].forEach(point => {
          L.circleMarker(point, {
            radius: 3,
            color: DEFAULT_MEASUREMENTS_STYLE.color,
            fillColor: DEFAULT_MEASUREMENTS_STYLE.color,
            fillOpacity: opacity,
            opacity,
            weight: 1.5,
            interactive: false,
          }).addTo(measureLayer);
        });
      });
      syncLayerOrderToMap();
    }
    function renderMeasureDraft() {
      measureDraftLayer.clearLayers();
      measurePoints.forEach(point => L.circleMarker(point, {
        radius: 4,
        color: '#16734d',
        fillColor: '#16734d',
        fillOpacity: 1,
        weight: 2,
      }).addTo(measureDraftLayer));
    }
    function saveMeasurement(start, end) {
      const hadMeasurements = hasMeasurements();
      const meters = distanceMeters(start, end);
      const row = {
        id: `measure-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`,
        start: [start.lat, start.lng],
        end: [end.lat, end.lng],
        lengthMeters: meters,
        lengthLabel: formatDistance(meters),
        createdAt: new Date().toISOString(),
      };
      STATE.measurements.push(row);
      STATE.measurementsShown = true;
      measurementLayerNotice = true;
      if (!hadMeasurements) placeOperationalLayer(MEASUREMENTS_LAYER_ID, 'front');
      persistMeasurements();
      renderMeasurements();
      const summary = measurementSummary();
      renderLayers();
      setActiveLayer(MEASUREMENTS_LAYER_ID, { reveal: false });
      revealActiveBadge(4200);
      syncToolState();
      showModeKey('mode.measureSaved', { distance: row.lengthLabel, count: summary.count, mean: summary.meanLabel }, true);
      logMsg('log.measureSummary', { count: summary.count, mean: summary.meanLabel });
      syncSessionState('measurement');
      return row;
    }
    function undoLastMeasurement() {
      if (measurePoints.length) {
        measurePoints.pop();
        renderMeasureDraft();
        showModeKey('mode.measureUndoDraft', {}, true);
        syncToolState();
        return true;
      }
      if (!Array.isArray(STATE.measurements) || !STATE.measurements.length) {
        showModeKey('mode.measureUndoEmpty', {}, true);
        syncToolState();
        return false;
      }
      const row = STATE.measurements.pop();
      persistMeasurements();
      renderMeasurements();
      measurementLayerNotice = STATE.measurements.length > 0;
      renderLayers();
      if (STATE.measurements.length) {
        setActiveLayer(MEASUREMENTS_LAYER_ID, { reveal: false });
      } else if (activeLayerId === MEASUREMENTS_LAYER_ID) {
        setActiveLayer(aoiLayerModel()?.id || STATE.layers.find(item => item.shown)?.id || STATE.layers[0]?.id || PRIMARY_BASEMAP_LAYER_ID, { reveal: false });
      }
      const distance = row?.lengthLabel || formatDistance(row?.lengthMeters || 0);
      showModeKey('mode.measureUndoSaved', { distance }, true);
      logMsg('log.measureUndo', { distance });
      syncToolState();
      syncSessionState('measurement-undo');
      return true;
    }
    function clearMeasurements() {
      const count = Array.isArray(STATE.measurements) ? STATE.measurements.length : 0;
      STATE.measurements = [];
      removeOperationalLayerOrder(MEASUREMENTS_LAYER_ID);
      persistMeasurements();
      measureLayer.clearLayers();
      measureDraftLayer.clearLayers();
      measurePoints = [];
      measureMode = false;
      measurementLayerNotice = false;
      syncToolState();
      renderLayers();
      if (activeLayerId === MEASUREMENTS_LAYER_ID) setActiveLayer(aoiLayerModel()?.id || STATE.layers.find(item => item.shown)?.id || STATE.layers[0]?.id || PRIMARY_BASEMAP_LAYER_ID, { reveal: false });
      showModeKey('mode.measureCleared', {}, false);
      logMsg('log.measureCleared', { count });
      syncSessionState('measurements-cleared');
      return measurementSummary();
    }
    async function extractNdviForCurrentAoi(options = {}) {
      if (!hasAoi()) {
        showModeKey('mode.ndviNoAoi', {}, true);
        return { ok: false, error: 'AOI is required' };
      }
      showModeKey('mode.ndviBuilding', {}, true);
      logMsg('log.ndviStarted');
      try {
        const response = await fetch('/api/analysis/ndvi', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project: STATE.project,
            aoi: cloneAoi(STATE.aoi),
            bounds: STATE.aoi.bounds,
            startDate: options.startDate || STATE.startDate,
            endDate: options.endDate || STATE.endDate,
            cloudPct: options.cloudPct ?? STATE.cloudPct,
            scale: options.scale || 10,
          }),
        });
        const payload = await response.json().catch(() => ({ ok: false, error: response.statusText || 'request failed' }));
        if (!response.ok || !payload.ok || !payload.layer) {
          throw new Error(payload.error || `HTTP ${response.status}`);
        }
        addGeneratedLayer(payload.layer);
        const mean = Number(payload.summary?.mean);
        const count = Number(payload.summary?.count || 0);
        const meanText = Number.isFinite(mean) ? mean.toFixed(3) : '-';
        showModeKey('mode.ndviDone', { mean: meanText, count });
        logMsg('log.ndviDone', { mean: meanText });
        return payload;
      } catch (error) {
        const message = error && error.message ? error.message : String(error);
        showModeKey('mode.ndviFailed', { message: message.slice(0, 90) }, true);
        logMsg('log.ndviFailed');
        return { ok: false, error: message };
      } finally {
        syncToolState();
      }
    }
    async function exportNdviToDrive(options = {}) {
      if (!hasAoi()) {
        showModeKey('mode.ndviNoAoi', {}, true);
        return { ok: false, error: 'AOI is required' };
      }
      showModeKey('mode.driveExportBuilding', {}, true);
      logMsg('log.driveExportStarted');
      try {
        const response = await fetch('/api/export/ndvi-drive', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project: STATE.project,
            aoi: cloneAoi(STATE.aoi),
            bounds: STATE.aoi.bounds,
            startDate: options.startDate || STATE.startDate,
            endDate: options.endDate || STATE.endDate,
            cloudPct: options.cloudPct ?? STATE.cloudPct,
            scale: options.scale || 10,
            folder: options.folder || 'EasyGEE',
            fileNamePrefix: options.fileNamePrefix,
            description: options.description,
            fileFormat: options.fileFormat || 'GeoTIFF',
            cloudOptimized: options.cloudOptimized !== false,
            maxPixels: options.maxPixels || 1000000000,
            start: options.start !== false,
          }),
        });
        const payload = await response.json().catch(() => ({ ok: false, error: response.statusText || 'request failed' }));
        if (!response.ok || !payload.ok || !(payload.task || payload.export)) {
          throw new Error(payload.error || `HTTP ${response.status}`);
        }
        const task = payload.task || payload.export;
        addTask(task, { logKey: 'log.driveExportDone', reason: 'drive-export' });
        showModeKey('mode.driveExportDone', { task: task.fileNamePrefix || task.taskId || task.title || 'Drive' });
        return payload;
      } catch (error) {
        const message = error && error.message ? error.message : String(error);
        showModeKey('mode.driveExportFailed', { message: message.slice(0, 90) }, true);
        logMsg('log.driveExportFailed');
        return { ok: false, error: message };
      } finally {
        syncToolState();
      }
    }

    function currentPerformanceEngine() {
      const meta = currentBasemapMeta();
      const type = String(meta?.type || 'xyz').toLowerCase();
      const diagnostics = publicBasemapPerformance(meta);
      if (meta?.custom && type === 'cog') return {
        id: 'maplibre-cog',
        renderer: `MapLibre __EASYGEE_MAPLIBRE_VERSION__`,
        protocol: `COG __EASYGEE_COG_PROTOCOL_VERSION__`,
        access: 'HTTP Range',
        status: cogEngineStatus,
        lazy: true,
        crs: meta.crs || 'EPSG:3857',
        ...(diagnostics ? { diagnostics } : {}),
      };
      if (meta?.custom && type === 'pmtiles') return {
        id: 'leaflet-pmtiles',
        renderer: 'Leaflet',
        protocol: `PMTiles __EASYGEE_PMTILES_VERSION__`,
        access: 'HTTP Range',
        status: window.pmtiles?.PMTiles ? 'ready' : 'unavailable',
        lazy: false,
        ...(diagnostics ? { diagnostics } : {}),
      };
      return {
        id: 'leaflet-tiles',
        renderer: 'Leaflet',
        protocol: type.toUpperCase(),
        access: 'XYZ tiles',
        status: 'ready',
        lazy: false,
        ...(diagnostics ? { diagnostics } : {}),
      };
    }
    function buildProjectState() {
      const explicitAoi = hasAoi() ? cloneAoi(STATE.aoi) : null;
      const processingAoi = currentProcessingAoi();
      const processingBounds = processingAoi ? processingAoi.bounds : null;
      return {
        title: STATE.title,
        project: STATE.project,
        projectSource: STATE.projectSource || 'unknown',
        agentProtocolVersion: AGENT_PROTOCOL_VERSION,
        startDate: STATE.startDate,
        endDate: STATE.endDate,
        cloudPct: STATE.cloudPct,
        center: [map.getCenter().lat, map.getCenter().lng],
        zoom: map.getZoom(),
        basemap: currentBasemap,
        basemapShown: primaryBasemapShown,
        basemapOpacity: primaryBasemapOpacity,
        defaultBasemap: defaultBasemapId,
        customBasemaps: customBasemaps.map(serializableCustomBasemap),
        performanceEngine: currentPerformanceEngine(),
        activeLayerId,
        bounds: processingBounds,
        aoiBounds: explicitAoi ? explicitAoi.bounds : null,
        aoi: explicitAoi,
        hasExplicitAoi: Boolean(explicitAoi),
        processingAoi,
        processingBounds,
        aoiShown: STATE.aoiShown !== false,
        aoiStyle: normalizeAoiStyle(STATE.aoiStyle),
        measurements: STATE.measurements.map(item => ({ ...item })),
        measurementsShown: STATE.measurementsShown !== false,
        measurementsOpacity: normalizeMeasurementsOpacity(STATE.measurementsOpacity),
        measurementSummary: measurementSummary(),
        language: currentLang,
        selectedDataset: selectedDatasetContext(),
        favoriteDatasets: [...favoriteDatasetIds].sort(),
        visualPreferences: { ...visualPreferences },
        uploadCapabilities: { ...UPLOAD_CAPABILITIES },
        uploads: (STATE.uploads || []).map(item => normalizeUploadRecord(item)).filter(Boolean),
        quota: STATE.quota,
        tasks: STATE.tasks.map(item => ({ ...item })),
        layerOrder: [...normalizedOperationalLayerOrder(operationalLayerOrder)],
        layers: STATE.layers.map(layer => ({
          id: layer.id,
          name: layer.name,
          dataset: layer.dataset,
          type: layer.type,
          ...(layer.role ? { role: layer.role } : {}),
          ...(layer.sourceId ? { sourceId: layer.sourceId } : {}),
          shown: layerRegistry.has(layer.id) ? map.hasLayer(layerRegistry.get(layer.id).tile) : Boolean(layer.shown),
          opacity: layer.opacity,
          styleProfile: layer.styleProfile || layerStyleProfile(layer),
          stylePreset: layer.stylePreset || 'default',
          ...(layer.visParams ? { visParams: layer.visParams } : {}),
          ...(layer.legend ? { legend: layer.legend } : {}),
          ...(layer.recipe ? { recipe: layer.recipe } : {}),
          ...(layer.summary ? { summary: layer.summary } : {}),
          ...(layer.aoi ? { aoi: layer.aoi } : {}),
        }))
      };
    }

    async function syncSessionState(reason = 'update') {
      if (sessionSyncBusy) return false;
      let state;
      try {
        state = buildProjectState();
      } catch {
        return false;
      }
      const text = JSON.stringify(state);
      if (text === lastSessionStateText) return true;
      lastSessionStateText = text;
      state.sessionReason = reason;
      state.sessionUpdatedAt = new Date().toISOString();
      sessionSyncBusy = true;
      try {
        const response = await fetch('/api/session/state', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ state }),
        });
        return response.ok;
      } catch {
        return false;
      } finally {
        sessionSyncBusy = false;
      }
    }
    async function executeSessionAction(action) {
      const type = String(action?.type || action?.action || '').toLowerCase();
      if (type === 'setbasemap' || type === 'set-basemap') {
        return setBasemap(String(action.basemapId || action.id || action.basemap || ''));
      }
      if (type === 'addbasemapoverlay' || type === 'add-basemap-overlay') {
        return addBasemapOverlay(String(action.basemapId || action.sourceId || action.id || action.basemap || ''));
      }
      if (type === 'setdefaultbasemap' || type === 'set-default-basemap') {
        return setDefaultBasemap(String(action.basemapId || action.id || action.basemap || ''));
      }
      if (type === 'addcustombasemap' || type === 'add-custom-basemap' || type === 'updatecustombasemap' || type === 'update-custom-basemap') {
        const raw = action.basemap && typeof action.basemap === 'object' ? action.basemap : action;
        const requestedId = String(raw.id || action.basemapId || '').trim();
        const editing = type.startsWith('update');
        let meta = normalizeCustomBasemap({ ...raw, id: requestedId || createCustomBasemapId(raw.name) }, customBasemaps.length);
        if (!meta || !validHttpTemplate(meta.url)) return false;
        const index = customBasemaps.findIndex(item => item.id === meta.id);
        if (editing && index < 0) return false;
        const previous = index >= 0 ? customBasemaps[index] : null;
        const willActivate = action.activate !== false || currentBasemap === meta.id;
        if (meta.type === 'pmtiles') {
          const inspection = await inspectPmtilesArchive(meta, { refresh: true, requireVisibleTile: willActivate });
          if (!inspection.ok) return false;
          meta = normalizeCustomBasemap({
            ...meta,
            minZoom: inspection.header?.minZoom,
            maxZoom: inspection.header?.maxZoom,
            maxNativeZoom: inspection.header?.maxZoom,
          }, customBasemaps.length);
          if (!meta) return false;
        }
        if (meta.type === 'cog') {
          const inspection = await inspectCogSource(meta, { refresh: true, requireVisibleTile: willActivate, fitBounds: willActivate });
          if (!inspection.ok) return false;
          meta = inspection.meta;
          if (!meta) return false;
        }
        if (previous?.type === 'pmtiles' && (meta.type !== 'pmtiles' || previous.url !== meta.url)) {
          discardPmtilesArchive(previous.url);
        }
        if (previous?.type === 'cog' && (meta.type !== 'cog' || previous.url !== meta.url)) discardCogSource(previous.url);
        if (index >= 0) customBasemaps.splice(index, 1, meta);
        else customBasemaps.push(meta);
        customBasemaps = normalizeCustomBasemaps(customBasemaps);
        rebuildBasemapRegistry(action.activate === false ? currentBasemap : meta.id);
        syncSessionState(editing ? 'custom-basemap-updated' : 'custom-basemap-added');
        return true;
      }
      if (type === 'removecustombasemap' || type === 'remove-custom-basemap') {
        return removeCustomBasemap(String(action.basemapId || action.id || ''), { confirm: false });
      }
      if (type === 'addlayer' || type === 'add-layer') {
        if (action.layer) {
          addGeneratedLayer(action.layer);
          showModeKey('mode.datasetAdded', { count: 1 });
          return true;
        }
        return false;
      }
      if (type === 'selectdataset' || type === 'select-dataset') {
        const datasetId = String(action.datasetId || action.id || '');
        if (datasetId && datasetById(datasetId)) {
          setActiveDataset(datasetId);
          return true;
        }
        return false;
      }
      if (type === 'setaoi' || type === 'set-aoi') {
        if (action.aoi && updateAoi(action.aoi)) {
          resetHomeView();
          return true;
        }
        return false;
      }
      if (type === 'clearaoi' || type === 'clear-aoi') {
        clearAoi();
        return true;
      }
      if (type === 'removelayer' || type === 'remove-layer') {
        if (action.layerId || action.id) return removeLayer(String(action.layerId || action.id));
        return false;
      }
      if (type === 'removeupload' || type === 'remove-upload') {
        if (action.uploadId || action.id) return removeUpload(String(action.uploadId || action.id));
        return false;
      }
      if (type === 'selectlayer' || type === 'select-layer') {
        const layerId = String(action.layerId || action.id || activeLayerId || '');
        if (!layerId) return false;
        return selectLayer(layerId, { reveal: action.reveal !== false });
      }
      if (type === 'zoomtolayer' || type === 'zoom-to-layer' || type === 'zoomlayer' || type === 'zoom-layer') {
        const layerId = String(action.layerId || action.id || activeLayerId || '');
        if (!layerId) return false;
        return zoomToLayer(layerId, action.options || action);
      }
      if (type === 'refreshlayer' || type === 'refresh-layer' || type === 'reloadlayer' || type === 'reload-layer') {
        const layerId = String(action.layerId || action.id || activeLayerId || '');
        if (!layerId) return false;
        return refreshLayer(layerId, { reason: 'layer-refresh-action' });
      }
      if (type === 'showlayer' || type === 'show-layer' || type === 'hidelayer' || type === 'hide-layer' || type === 'setlayervisibility' || type === 'set-layer-visibility') {
        const layerId = String(action.layerId || action.id || activeLayerId || '');
        if (!layerId) return false;
        const shown = type === 'showlayer' || type === 'show-layer'
          ? true
          : type === 'hidelayer' || type === 'hide-layer'
            ? false
            : action.shown !== false;
        return setLayerVisibility(layerId, shown, { activate: action.activate !== false, reveal: action.reveal !== false });
      }
      if (type === 'setlayeropacity' || type === 'set-layer-opacity' || type === 'setopacity' || type === 'set-opacity') {
        const layerId = String(action.layerId || action.id || activeLayerId || '');
        if (!layerId) return false;
        return setLayerOpacity(layerId, action.opacity ?? action.value, { render: true });
      }
      if (type === 'setaoistyle' || type === 'set-aoi-style') {
        STATE.aoiStyle = normalizeAoiStyle({ ...STATE.aoiStyle, ...(action.style || action) });
        if (typeof action.shown === 'boolean') STATE.aoiShown = action.shown;
        renderAoiLayer();
        renderLayers();
        syncSessionState('aoi-style');
        return true;
      }
      if (type === 'updatelayerstyle' || type === 'update-layer-style') {
        const layerId = String(action.layerId || action.id || activeLayerId || '');
        if (!layerId) return false;
        if (layerId === AOI_LAYER_ID) {
          STATE.aoiStyle = normalizeAoiStyle({ ...STATE.aoiStyle, ...(action.style || action) });
          renderAoiLayer();
          renderLayers();
          syncSessionState('aoi-style');
          return true;
        }
        if (action.preset || action.stylePreset) {
          return applyLayerPreset(layerId, String(action.preset || action.stylePreset));
        }
        return true;
      }
      if (type === 'clearmeasurements' || type === 'clear-measurements') {
        clearMeasurements();
        return true;
      }
      if (type === 'addtask' || type === 'add-task') {
        return addTask(action.task || action.export || action, { reason: 'task-action' });
      }
      if (type === 'extractndvi' || type === 'extract-ndvi') {
        await extractNdviForCurrentAoi(action.options || action);
        return true;
      }
      if (type === 'exportndvidrive' || type === 'export-ndvi-drive' || type === 'drivendviexport' || type === 'drive-ndvi-export') {
        await exportNdviToDrive(action.options || action);
        return true;
      }
      return false;
    }
    async function pollSessionActions() {
      if (sessionActionBusy) return false;
      sessionActionBusy = true;
      try {
        const response = await fetch(`/api/session/actions?since=${encodeURIComponent(lastSessionActionId)}`);
        if (!response.ok) return false;
        const payload = await response.json();
        const actions = Array.isArray(payload.actions) ? payload.actions : [];
        for (const action of actions) {
          const id = Number(action.id || 0);
          if (id > lastSessionActionId) lastSessionActionId = id;
          await executeSessionAction(action);
        }
        const latest = Number(payload.latestActionId || 0);
        if (latest > lastSessionActionId) lastSessionActionId = latest;
        return true;
      } catch {
        return false;
      } finally {
        sessionActionBusy = false;
      }
    }

    $('dataset-search').addEventListener('input', event => {
      renderDatasets(filteredCatalog());
    });
    $('dataset-list').addEventListener('scroll', maybeLoadMoreDatasets);
    $('category-search').addEventListener('input', event => {
      catalogCategoryQuery = event.target.value || '';
      renderCatalogFacets();
    });
    $('home-btn').addEventListener('click', () => {
      resetHomeView();
      updateScaleLine();
      logMsg('log.home');
    });
    function setBasemap(nextBasemap) {
      const nextMeta = BASEMAPS.find(item => item.id === nextBasemap);
      if (!nextMeta) return false;
      if (isTiandituBasemap(nextMeta) && !tiandituToken) return requestTiandituToken();
      const nextLayer = basemapLayers.get(nextBasemap);
      if (!nextLayer) return false;
      if (nextBasemap === currentBasemap) {
        primaryBasemapShown = true;
        setRasterLayerOpacity(nextLayer, primaryBasemapOpacity);
        if (!map.hasLayer(nextLayer)) nextLayer.addTo(map);
        fitCogBasemapBounds(nextMeta);
        renderBasemapChoices();
        renderLayers();
        updateInspector();
        syncSessionState('basemap-visible');
        return true;
      }
      beginBasemapPerformance(nextMeta, nextLayer);
      fitCogBasemapBounds(nextMeta);
      const currentLayer = basemapLayers.get(currentBasemap);
      if (currentLayer && map.hasLayer(currentLayer)) map.removeLayer(currentLayer);
      primaryBasemapShown = true;
      setRasterLayerOpacity(nextLayer, primaryBasemapOpacity);
      if (!map.hasLayer(nextLayer)) nextLayer.addTo(map);
      currentBasemap = nextBasemap;
      renderBasemapChoices();
      renderLayers();
      updateInspector();
      showModeKey('mode.basemap', { basemap: displayBasemapName() });
      logMsg('log.basemap', { basemap: displayBasemapName() });
      syncSessionState('basemap-changed');
      return true;
    }
    function toggleBasemapPanel() {
      const panel = document.querySelector('.basemap-panel');
      const shouldOpen = !panel.classList.contains('open');
      quotaFocus = false;
      document.querySelector('.data-panel').classList.remove('open');
      document.querySelector('.upload-panel').classList.remove('open');
      document.querySelector('.layers-panel').classList.remove('open');
      document.querySelector('.right').classList.remove('open');
      document.querySelector('.bottom').classList.remove('open');
      panel.classList.toggle('open', shouldOpen);
      renderBasemapChoices();
      syncToolState();
    }
    $('basemap-btn').addEventListener('click', toggleBasemapPanel);
    $('basemap-close-btn').addEventListener('click', () => {
      document.querySelector('.basemap-panel').classList.remove('open');
      syncToolState();
    });
    $('basemap-add-btn').addEventListener('click', () => openBasemapEditor());
    $('tianditu-auth-toggle').addEventListener('click', () => {
      const opening = !$('tianditu-auth').classList.contains('open');
      if (opening && tiandituToken) tiandituKeyEditing = false;
      renderTiandituAuth();
      setTiandituAuthOpen(opening);
    });
    $('tianditu-token-change').addEventListener('click', editTiandituToken);
    $('tianditu-token-persistence').addEventListener('click', toggleTiandituPersistence);
    $('tianditu-token-apply').addEventListener('click', applyTiandituToken);
    $('tianditu-token').addEventListener('keydown', event => {
      if (event.key !== 'Enter') return;
      event.preventDefault();
      applyTiandituToken();
    });
    $('basemap-editor-close').addEventListener('click', closeBasemapEditor);
    $('basemap-form-type').addEventListener('change', updateBasemapTypeFields);
    $('basemap-editor').querySelectorAll('input, select').forEach(field => {
      field.addEventListener('input', invalidateBasemapTest);
      field.addEventListener('change', invalidateBasemapTest);
    });
    $('basemap-test-btn').addEventListener('click', () => testBasemapForm());
    $('basemap-editor').addEventListener('submit', event => {
      event.preventDefault();
      saveBasemapForm();
    });
    function toggleMeasureMode() {
      measureMode = !measureMode;
      measurePoints = [];
      measureDraftLayer.clearLayers();
      if (measureMode) {
        stopDrawAoiMode(false);
        document.querySelector('.data-panel').classList.remove('open');
        document.querySelector('.upload-panel').classList.remove('open');
        document.querySelector('.layers-panel').classList.remove('open');
        document.querySelector('.right').classList.remove('open');
        document.querySelector('.bottom').classList.remove('open');
        document.querySelector('.basemap-panel').classList.remove('open');
      }
      syncToolState();
      showModeKey(measureMode ? 'mode.measureStart' : 'mode.measureOff', {}, measureMode);
      logMsg(measureMode ? 'log.measureOn' : 'log.measureOff');
    }
    function handleMeasureClick(event) {
      measurePoints.push(event.latlng);
      renderMeasureDraft();
      if (measurePoints.length === 1) {
        showModeKey('mode.measureEndpoint', {}, true);
        syncToolState();
        return true;
      }
      const [start, end] = measurePoints;
      const row = saveMeasurement(start, end);
      measureDraftLayer.clearLayers();
      logMsg('log.measured', { distance: row.lengthLabel });
      measurePoints = [];
      syncToolState();
      return true;
    }
    $('draw-aoi-btn').addEventListener('click', event => toggleDrawAoiMode(event.shiftKey));
    $('measure-btn').addEventListener('click', toggleMeasureMode);
    $('measure-undo-btn').addEventListener('click', undoLastMeasurement);
    async function copyProjectState() {
      const text = JSON.stringify(buildProjectState(), null, 2);
      try {
        await navigator.clipboard.writeText(text);
        logMsg('log.copied');
      } catch {
        logMsg('log.clipboardUnavailable');
      }
    }
    function downloadProjectState() {
      const blob = new Blob([JSON.stringify(buildProjectState(), null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'easygee-project.json';
      a.click();
      URL.revokeObjectURL(url);
      logMsg('log.downloaded');
    }
    $('copy-btn').addEventListener('click', copyProjectState);
    $('download-btn').addEventListener('click', downloadProjectState);
    function togglePanel(which) {
      const data = document.querySelector('.data-panel');
      const upload = document.querySelector('.upload-panel');
      const layers = document.querySelector('.layers-panel');
      const right = document.querySelector('.right');
      const bottom = document.querySelector('.bottom');
      const basemap = document.querySelector('.basemap-panel');
      quotaFocus = false;
      basemap.classList.remove('open');
      if (which === 'data') {
        data.classList.toggle('open');
        upload.classList.remove('open');
        layers.classList.remove('open');
        right.classList.remove('open');
        bottom.classList.remove('open');
      } else if (which === 'upload') {
        upload.classList.toggle('open');
        data.classList.remove('open');
        layers.classList.remove('open');
        right.classList.remove('open');
        bottom.classList.remove('open');
        renderUploads();
      } else if (which === 'layers') {
        const opening = !layers.classList.contains('open');
        layers.classList.toggle('open', opening);
        if (opening) measurementLayerNotice = false;
        data.classList.remove('open');
        upload.classList.remove('open');
        right.classList.remove('open');
        bottom.classList.remove('open');
      } else if (which === 'right') {
        right.classList.toggle('open');
        data.classList.remove('open');
        upload.classList.remove('open');
        layers.classList.remove('open');
        bottom.classList.remove('open');
      }
      syncToolState();
    }
    function showQuotaStatus() {
      const bottom = document.querySelector('.bottom');
      if (quotaFocus && bottom.classList.contains('open')) {
        quotaFocus = false;
        bottom.classList.remove('open');
        $('mode-chip').classList.remove('show');
        syncToolState();
        return;
      }
      quotaFocus = true;
      document.querySelector('.data-panel').classList.remove('open');
      document.querySelector('.upload-panel').classList.remove('open');
      document.querySelector('.layers-panel').classList.remove('open');
      document.querySelector('.right').classList.remove('open');
      document.querySelector('.basemap-panel').classList.remove('open');
      bottom.classList.add('open');
      $('mode-chip').classList.remove('show');
      syncToolState();
      logMsg('log.quotaOpened');
    }
    $('data-btn').addEventListener('click', () => togglePanel('data'));
    $('upload-btn').addEventListener('click', () => togglePanel('upload'));
    $('upload-close-btn').addEventListener('click', () => {
      document.querySelector('.upload-panel').classList.remove('open');
      syncToolState();
    });
    $('upload-file-input').addEventListener('change', () => {
      $('upload-status').textContent = '';
      $('upload-status').classList.remove('error');
      renderUploads();
    });
    $('upload-submit-btn').addEventListener('click', uploadSelectedFiles);
    $('layers-btn').addEventListener('click', () => togglePanel('layers'));
    $('inspector-btn').addEventListener('click', () => togglePanel('right'));
    $('quota-btn').addEventListener('click', showQuotaStatus);
    $('drive-btn').addEventListener('click', openDriveTarget);
    $('lang-btn').addEventListener('click', () => setLanguage(currentLang === 'zh' ? 'en' : 'zh'));
    $('active-layer-badge').addEventListener('click', () => {
      setBasemapSourceOpen(!basemapSourceOpen, currentBasemap);
    });
    $('basemap-source-close').addEventListener('click', () => setBasemapSourceOpen(false));
    document.addEventListener('pointerdown', event => {
      if (!basemapSourceOpen) return;
      if ($('active-layer-badge').contains(event.target) || $('basemap-source-card').contains(event.target)) return;
      setBasemapSourceOpen(false);
    });
    document.querySelectorAll('[data-close-panel]').forEach(button => {
      button.addEventListener('click', () => {
        document.querySelector(`.${button.dataset.closePanel}`).classList.remove('open');
        syncToolState();
      });
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Enter' && drawPolygonMode) {
        event.preventDefault();
        finishPolygonAoi();
        return;
      }
      if (event.key !== 'Escape') return;
      if (basemapSourceOpen) {
        setBasemapSourceOpen(false);
        return;
      }
      if (drawAoiMode || drawPolygonMode) {
        stopDrawAoiMode(true);
        return;
      }
      quotaFocus = false;
      document.querySelector('.data-panel').classList.remove('open');
      document.querySelector('.upload-panel').classList.remove('open');
      document.querySelector('.layers-panel').classList.remove('open');
      document.querySelector('.right').classList.remove('open');
      document.querySelector('.bottom').classList.remove('open');
      document.querySelector('.basemap-panel').classList.remove('open');
      syncToolState();
    });

    map.on('mousemove', event => {
      handleDrawAoiMove(event);
      handleDrawPolygonMove(event);
    });
    map.on('click', event => {
      if (drawPolygonMode && handleDrawPolygonClick(event)) return;
      if (drawAoiMode && handleDrawAoiClick(event)) return;
      if (measureMode && handleMeasureClick(event)) return;
      $('lat-value').textContent = fmt(event.latlng.lat, 6);
      $('lon-value').textContent = fmt(event.latlng.lng, 6);
      $('zoom-value').textContent = map.getZoom();
      setClickState('state.clicked');
      logMsg('log.clicked', { lat: fmt(event.latlng.lat, 4), lon: fmt(event.latlng.lng, 4) });
    });
    map.on('dblclick', event => {
      if (!drawPolygonMode) return;
      L.DomEvent.stop(event);
      finishPolygonAoi();
    });
    map.on('zoomend moveend', () => {
      $('zoom-value').textContent = map.getZoom();
      updateScaleLine();
      renderBasemapSourceDetails();
    });
    window.EasyGEE = {
      getProjectState: () => buildProjectState(),
      getAoi: () => hasAoi() ? cloneAoi(STATE.aoi) : null,
      setAoi: aoi => updateAoi(aoi),
      clearAoi: () => {
        return clearAoi();
      },
      startRectangleAoi: () => startRectangleAoiMode(),
      startPolygonAoi: () => startPolygonAoiMode(),
      getMeasurements: () => STATE.measurements.map(item => ({ ...item })),
      getMeasurementSummary: () => measurementSummary(),
      clearMeasurements: () => clearMeasurements(),
      getTasks: () => STATE.tasks.map(item => ({ ...item })),
      addTask: task => addTask(task),
      getUploads: () => (STATE.uploads || []).map(item => normalizeUploadRecord(item)).filter(Boolean),
      getUploadCapabilities: () => ({ ...UPLOAD_CAPABILITIES }),
      openUploadPanel: () => togglePanel('upload'),
      removeUpload: id => removeUpload(id),
      getDriveUrl: () => driveTargetUrl(),
      openDrive: () => openDriveTarget(),
      getSelectedDataset: () => selectedDatasetContext(),
      getBasemaps: () => BASEMAPS.map(meta => meta.custom
        ? serializableCustomBasemap(meta)
        : { id: meta.id, name: basemapDisplayName(meta), provider: meta.provider, service: meta.service || meta.serviceKey, minZoom: meta.options?.minZoom ?? 0, maxZoom: meta.options?.maxZoom, maxNativeZoom: meta.options?.maxNativeZoom ?? meta.options?.maxZoom, builtIn: true }),
      getCurrentBasemap: () => currentBasemap,
      getDefaultBasemap: () => defaultBasemapId,
      getPerformanceEngine: () => currentPerformanceEngine(),
      setBasemap: id => setBasemap(String(id || '')),
      addBasemapOverlay: id => addBasemapOverlay(String(id || currentBasemap || '')),
      setDefaultBasemap: id => setDefaultBasemap(String(id || '')),
      addCustomBasemap: basemap => executeSessionAction({ type: 'addCustomBasemap', basemap }),
      updateCustomBasemap: basemap => executeSessionAction({ type: 'updateCustomBasemap', basemap }),
      removeCustomBasemap: id => removeCustomBasemap(String(id || ''), { confirm: false }),
      openBasemapEditor: id => openBasemapEditor(id || null),
      extractNdvi: options => extractNdviForCurrentAoi(options || {}),
      exportNdviToDrive: options => exportNdviToDrive(options || {}),
      addGeneratedLayer: meta => addGeneratedLayer(meta),
      showLayer: id => setLayerVisibility(String(id || activeLayerId || ''), true),
      hideLayer: id => setLayerVisibility(String(id || activeLayerId || ''), false),
      setLayerVisibility: (id, shown) => setLayerVisibility(String(id || activeLayerId || ''), shown !== false),
      setLayerOpacity: (id, opacity) => setLayerOpacity(String(id || activeLayerId || ''), opacity),
      zoomToLayer: (id, options) => zoomToLayer(String(id || activeLayerId || ''), options || {}),
      refreshLayer: id => refreshLayer(String(id || activeLayerId || '')),
      selectLayer: id => selectLayer(String(id || activeLayerId || '')),
      syncState: reason => syncSessionState(reason || 'manual'),
      pollActions: () => pollSessionActions(),
    };
    renderAoiLayer();
    renderMeasurements();
    renderTasks();
    applyI18n();
    renderDatasets(filteredCatalog());
    renderLayers();
    setActiveLayer(activeLayerId, { reveal: false });
    installPanelResizers();
    syncToolState();
    map.whenReady(() => {
      setTimeout(() => {
        map.invalidateSize(true);
        if (!restoreProfileMapView()) resetHomeView();
        updateScaleLine();
      }, 180);
    });
    window.addEventListener('resize', () => {
      map.invalidateSize(true);
      updateScaleLine();
    });
    logMsg('log.loaded');
    function startSessionProtocol() {
      syncSessionState('loaded');
      window.setInterval(() => syncSessionState('interval'), SESSION_SYNC_INTERVAL_MS);
      window.setInterval(pollSessionActions, SESSION_ACTION_POLL_MS);
      pollSessionActions();
    }
    restoreProfileFromServer().finally(startSessionProtocol);
    refreshCatalogFromApi();
