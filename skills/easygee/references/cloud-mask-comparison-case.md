# Sentinel-2 去云算法直观对比案例

这个案例的教学目标不是证明某个算法永远最好，而是让读者在相同输入下观察四件事：

1. QA60 只依据不透明云和卷云位元；
2. SCL 依靠 Sen2Cor 场景分类，同时处理云影、卷云和雪/冰；
3. s2cloudless 输出连续的云概率，需要选择阈值；
4. Cloud Score+ 输出连续的清晰度评分，更接近“这个像元有多可用”的质量评价。

## 固定实验条件

- 数据：`COPERNICUS/S2_SR_HARMONIZED`
- 场景：`20200601T185919_20200601T190551_T10TER`
- 日期窗口：`2020-06-01` 至 `2020-06-02`
- AOI：官方 s2cloudless 教程附近的 Portland 点，缓冲 5 km
- 真彩色：`B4/B3/B2`，统一显示范围 `0–3000`
- s2cloudless：`probability < 40`，并按官方教程用暗 NIR 像元和太阳方位角投影云影；云影距离 1 km，缓冲 50 m
- Cloud Score+：`cs_cdf >= 0.60`
- 控制变量：同一景、同一 5 km AOI、同一 B4/B3/B2 显示范围、同一 10 m 统计尺度
- 输出：原始真彩色、四种掩膜真彩色、可切换的红/绿掩膜层、四法共识图、保留像元比例

固定单景而不是直接做多时相合成，是为了避免把“日期不同、云况不同、合成策略不同”误认为算法差异。

## 运行

```powershell
python skills/easygee/scripts/cloud_mask_comparison.py
python skills/easygee/scripts/serve_map_preview.py <EASYGEE_WORKSPACE>/easygee-cloud-mask-comparison/cloud-mask-comparison.html
```

脚本会生成：

- `cloud-mask-comparison.html`：六宫格地图、掩膜切换器和指标卡片；
- `cloud-mask-comparison.json`：场景元数据、实验设计、保留像元比例和一致率。

HTML 是临时预览产物，Earth Engine 瓦片 URL 会过期，不应提交到仓库。需要更换 AOI 或日期时，优先重新选择一个有明显云/云影的单景，并同步更新场景索引；不要只换日期而保留旧的教学结论。

统计分母使用源影像的有效像元，而不是把 AOI 边缘的 no-data 直接算成云；四法共识图不指定单一真值，1–3 个方法保留表示方法之间存在空间分歧；“一致率”明确只表示与 Cloud Score+ 的空间决策一致，不表示精度。

## 引导读者观察

建议按以下顺序讲解：

1. 先看原始真彩色，圈出云、云影、亮地物和水面；
2. 看 QA60：它通常保留更多像元，因为没有单独的云影判定；
3. 看 SCL：重点观察云影、水面和暗色地物是否被一起剔除；
4. 看 s2cloudless：它先用概率识别云，再用暗 NIR 像元与太阳方位角投影云影；可以调整概率阈值，说明阈值越严格，漏云风险越低但有效像元越少；
5. 看 Cloud Score+：观察连续清晰度阈值对薄云、雾霾和边缘像元的影响；
6. 最后看四法共识图：颜色表示 0–4 个方法保留该像元；再对照“保留清晰像元”和“与 Cloud Score+ 参考一致率”。

## 科学解释边界

“保留像元比例”是掩膜行为的诊断量，不是准确率。若要评价算法精度，应增加人工标注或独立高分辨率参考数据，并报告 cloud/shadow 的 precision、recall、F1 或 commission/omission error。Cloud Score+ 也不能自动被当作真值；它是质量评分数据集。

此外，QA60 在 2022-01-25 至 2024-02-28 之间存在历史缺口，跨多年分析不应单独依赖 QA60。这个案例使用它是为了教学对照，而不是作为推荐的长期生产方案。
