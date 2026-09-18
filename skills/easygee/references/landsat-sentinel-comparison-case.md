# Landsat 8 与 Sentinel-2 同日对比案例

## 教学目标

让读者在同一个 AOI、同一天的观测中直观看到：

- Sentinel-2 的 10 m 与 Landsat 8 的 30 m 空间细节差异；
- Sentinel-2 Cloud Score+ 与 Landsat Collection 2 `QA_PIXEL` 的去云结果差异；
- 两个传感器使用不同红光/近红外波段后，NDVI 空间纹理和 AOI 均值可能不同；
- 场景云量元数据不是像元级云掩膜精度。

## 固定案例

- AOI：Portland 附近点缓冲 5 km；
- 日期：2020-06-04；
- Sentinel-2：`COPERNICUS/S2_SR_HARMONIZED`，索引 `20200604T190919_20200604T191606_T10TER`；
- Landsat 8：`LANDSAT/LC08/C02/T1_L2`，索引 `LC08_046028_20200604`；
- Sentinel-2 去云：Cloud Score+ `cs_cdf >= 0.60`；
- Landsat 去云：`QA_PIXEL` 位元掩膜，并应用 Collection 2 Level 2 缩放因子；
- Sentinel-2 NDVI：`(B8-B4)/(B8+B4)`；
- Landsat 8 NDVI：`(SR_B5-SR_B4)/(SR_B5+SR_B4)`。

## 运行

```powershell
python skills/easygee/scripts/landsat_sentinel_comparison.py
python skills/easygee/scripts/serve_map_preview.py <EASYGEE_WORKSPACE>/easygee-cloud-mask-comparison/landsat-sentinel-comparison.html
```

页面包含六个图层面板：

1. Sentinel-2 原始 RGB；
2. Sentinel-2 去云 RGB；
3. Sentinel-2 去云 NDVI；
4. Landsat 8 原始 RGB；
5. Landsat 8 去云 RGB；
6. Landsat 8 去云 NDVI。

## 讲解顺序

先让读者比较两幅原始 RGB，再比较各自的去云结果，最后看 NDVI。重点强调：

1. Sentinel-2 更适合观察田块、道路和细碎地物；
2. Landsat 8 的 30 m 像元会平滑小地物和边界；
3. QA_PIXEL 与 Cloud Score+ 不是同一种算法，不能只看保留像元多少判断优劣；
4. NDVI 均值可用于同一 AOI 的辅助诊断，但跨传感器比较还要考虑波段响应、空间尺度、观测时间和大气处理差异。

## 不应过度解读

同日不等于同一时刻，也不等于两个传感器观测到完全相同的云形态。场景云量字段是整景/颗粒级元数据，不能替代像元级精度验证。若要做严格的传感器一致性研究，应进行空间配准、统一投影与尺度、波段响应 harmonization，并使用同一组参考样本。
