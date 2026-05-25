<template>
  <div class="overview-page" v-loading="loading">
    <!-- 顶部 scope 切换 -->
    <div class="overview-scope-bar">
      <div
        class="overview-scope-switch"
        role="tablist"
        :data-scope="overviewScope"
      >
        <span class="overview-scope-indicator" aria-hidden="true"></span>
        <button
          type="button"
          class="overview-scope-btn"
          :class="{ active: overviewScope === 'asset' }"
          role="tab"
          :aria-selected="overviewScope === 'asset'"
          @click="switchScope('asset')"
        >资产总览</button>
        <button
          type="button"
          class="overview-scope-btn"
          :class="{ active: overviewScope === 'supply' }"
          role="tab"
          :aria-selected="overviewScope === 'supply'"
          @click="switchScope('supply')"
        >物资总览</button>
      </div>
    </div>

    <!-- ========== 资产总览 ========== -->
    <template v-if="overviewScope === 'asset'">
      <section class="overview-showcase" aria-label="资产总览">
        <div class="gauge-panel">
          <div class="gauge-wrap" aria-label="资产总数">
            <svg class="gauge-svg" viewBox="0 0 360 230" role="img" aria-hidden="true">
              <path
                v-for="segment in gaugeSegments"
                :key="segment.key"
                class="gauge-segment"
                d="M 46 184 A 134 134 0 0 1 314 184"
                pathLength="100"
                :style="{
                  stroke: segment.color,
                  strokeDasharray: `${segment.length} 100`,
                  strokeDashoffset: -segment.start,
                }"
              />
            </svg>
            <div class="gauge-center">
              <strong>{{ formatNumber(totalAssets) }}</strong>
              <span>资产总数</span>
            </div>
          </div>
        </div>

        <div class="kpi-panel" aria-label="资产关键指标">
          <div v-for="item in kpiCards" :key="item.label" class="kpi-item">
            <div class="kpi-label">
              <span class="kpi-dot" :style="{ background: item.color }"></span>
              <span>{{ item.label }}</span>
              <i>i</i>
            </div>
            <strong>{{ item.value }}</strong>
          </div>
        </div>

        <div class="asset-trend-panel" aria-label="资产指标率趋势">
          <div class="asset-trend-legend">
            <span
              v-for="series in assetTrendSeries"
              :key="series.label"
              class="asset-trend-legend-item"
            >
              <i :style="{ background: series.color }"></i>
              {{ series.label }}
            </span>
          </div>

          <svg
            class="asset-trend-chart"
            :viewBox="`0 0 ${ASSET_TREND_WIDTH} ${ASSET_TREND_HEIGHT}`"
            role="img"
          >
            <defs>
              <linearGradient id="assetTrendPrimaryArea" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="palette.areaFrom" stop-opacity="0.28" />
                <stop offset="100%" :stop-color="palette.areaFrom" stop-opacity="0.04" />
              </linearGradient>
            </defs>

            <g class="asset-trend-grid">
              <g v-for="row in assetTrendGridRows" :key="row.value">
                <line
                  :x1="ASSET_TREND_LEFT"
                  :x2="ASSET_TREND_RIGHT"
                  :y1="row.y"
                  :y2="row.y"
                />
                <text :x="ASSET_TREND_LEFT - 12" :y="row.y + 4" text-anchor="end">
                  {{ row.value }}
                </text>
              </g>
            </g>

            <path
              v-if="assetTrendSeries[0]?.areaPath"
              class="asset-trend-area"
              :d="assetTrendSeries[0].areaPath"
            />

            <g class="asset-trend-lines">
              <g v-for="series in assetTrendSeries" :key="series.label">
                <path
                  :d="series.path"
                  :stroke="series.color"
                  :stroke-dasharray="series.dash"
                />
                <circle
                  v-for="point in series.points"
                  :key="`${series.label}-${point.key}`"
                  :cx="point.x"
                  :cy="point.y"
                  r="3"
                  :fill="series.color"
                />
              </g>
            </g>

            <g class="asset-trend-x-axis">
              <text
                v-for="label in assetTrendXAxisLabels"
                :key="label.key"
                :x="label.x"
                :y="ASSET_TREND_HEIGHT - 10"
                text-anchor="middle"
              >
                {{ label.text }}
              </text>
            </g>
          </svg>
        </div>
      </section>

      <section class="trend-panel" aria-label="资产趋势坐标图">
        <div class="trend-toolbar" aria-label="趋势图图例">
          <div class="trend-legend">
            <span class="trend-legend-item">
              <i class="legend-bar" :style="{ background: `linear-gradient(180deg, ${palette.bar} 0%, ${palette.barLight} 100%)` }"></i>
              每日新增资产
            </span>
            <span class="trend-legend-item">
              <i class="legend-line" :style="{ background: palette.line }"></i>
              累计资产总数
            </span>
          </div>
        </div>

        <div class="trend-chart-wrap" @pointerleave="clearActiveChartPoint">
          <svg class="trend-chart" :viewBox="`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`" role="img">
            <defs>
              <linearGradient id="trendLineArea" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="palette.line" stop-opacity="0.2" />
                <stop offset="100%" :stop-color="palette.line" stop-opacity="0.02" />
              </linearGradient>
              <linearGradient id="trendBarFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="palette.bar" stop-opacity="0.92" />
                <stop offset="100%" :stop-color="palette.barLight" stop-opacity="0.74" />
              </linearGradient>
            </defs>

            <g class="trend-grid">
              <g v-for="row in chartGridRows" :key="row.value">
                <line :x1="CHART_LEFT" :x2="CHART_RIGHT" :y1="row.y" :y2="row.y" />
                <text :x="CHART_LEFT - 18" :y="row.y + 4" text-anchor="end">
                  {{ row.value }}
                </text>
                <text :x="CHART_RIGHT + 18" :y="row.y + 4" text-anchor="start" class="right-axis">
                  {{ row.rightValue }}
                </text>
              </g>
            </g>

            <path class="trend-area" :d="chartAreaPath" />

            <g class="trend-bars">
              <rect
                v-for="bar in chartBars"
                :key="bar.key"
                :x="bar.x"
                :y="bar.y"
                :width="bar.width"
                :height="bar.height"
                rx="4"
              />
            </g>

            <path class="trend-line" :d="chartLinePath" />

            <g class="trend-points">
              <circle
                v-for="point in chartInteractivePoints"
                :key="point.key"
                :cx="point.x"
                :cy="point.y"
                r="3.2"
              />
            </g>

            <g class="trend-x-axis">
              <text
                v-for="label in chartXAxisLabels"
                :key="label.key"
                :x="label.x"
                :y="CHART_HEIGHT - 12"
                text-anchor="middle"
              >
                {{ label.text }}
              </text>
            </g>

            <g class="trend-hit-layer">
              <rect
                v-for="point in chartInteractivePoints"
                :key="`hit-${point.key}`"
                :x="point.hitX"
                :y="CHART_TOP"
                :width="point.hitWidth"
                :height="CHART_INNER_HEIGHT"
                tabindex="0"
                @focus="setActiveChartPoint(point)"
                @pointerenter="setActiveChartPoint(point)"
                @pointermove="setActiveChartPoint(point)"
                @touchstart.prevent="setActiveChartPoint(point)"
              />
            </g>
          </svg>

          <div
            v-if="activeChartPoint"
            class="trend-tooltip"
            :style="activeChartTooltipStyle"
          >
            <strong>{{ activeChartPoint.fullDateText }}</strong>
            <span>
              <i class="tooltip-bar" :style="{ background: `linear-gradient(180deg, ${palette.bar} 0%, ${palette.barLight} 100%)` }"></i>
              每日新增资产：{{ formatNumber(activeChartPoint.barValue) }}
            </span>
            <span>
              <i class="tooltip-line" :style="{ background: palette.line }"></i>
              累计资产总数：{{ formatNumber(activeChartPoint.lineValue) }}
            </span>
          </div>
        </div>
      </section>
    </template>

    <!-- ========== 物资总览 ========== -->
    <template v-if="overviewScope === 'supply'">
      <section class="overview-showcase" aria-label="物资总览">
        <div class="gauge-panel">
          <div class="gauge-wrap" aria-label="物资总记录">
            <svg class="gauge-svg" viewBox="0 0 360 230" role="img" aria-hidden="true">
              <path
                v-for="segment in supplyGaugeSegments"
                :key="segment.key"
                class="gauge-segment"
                d="M 46 184 A 134 134 0 0 1 314 184"
                pathLength="100"
                :style="{
                  stroke: segment.color,
                  strokeDasharray: `${segment.length} 100`,
                  strokeDashoffset: -segment.start,
                }"
              />
            </svg>
            <div class="gauge-center">
              <strong>{{ formatNumber(totalSupplies) }}</strong>
              <span>物资总记录</span>
            </div>
          </div>
        </div>

        <div class="kpi-panel" aria-label="物资关键指标">
          <div v-for="item in supplyKpiCards" :key="item.label" class="kpi-item">
            <div class="kpi-label">
              <span class="kpi-dot" :style="{ background: item.color }"></span>
              <span>{{ item.label }}</span>
              <i>i</i>
            </div>
            <strong>{{ item.value }}</strong>
          </div>
        </div>

        <div class="asset-trend-panel" aria-label="物资发放趋势">
          <div class="asset-trend-legend">
            <span
              v-for="series in supplyTrendSeries"
              :key="series.label"
              class="asset-trend-legend-item"
            >
              <i :style="{ background: series.color }"></i>
              {{ series.label }}
            </span>
          </div>

          <svg
            class="asset-trend-chart"
            :viewBox="`0 0 ${ASSET_TREND_WIDTH} ${ASSET_TREND_HEIGHT}`"
            role="img"
          >
            <defs>
              <linearGradient id="supplyTrendPrimaryArea" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="palette.areaFrom" stop-opacity="0.28" />
                <stop offset="100%" :stop-color="palette.areaFrom" stop-opacity="0.04" />
              </linearGradient>
            </defs>

            <g class="asset-trend-grid">
              <g v-for="row in supplyTrendGridRows" :key="row.value">
                <line
                  :x1="ASSET_TREND_LEFT"
                  :x2="ASSET_TREND_RIGHT"
                  :y1="row.y"
                  :y2="row.y"
                />
                <text :x="ASSET_TREND_LEFT - 12" :y="row.y + 4" text-anchor="end">
                  {{ row.value }}
                </text>
              </g>
            </g>

            <path
              v-if="supplyTrendSeries[0]?.areaPath"
              class="asset-trend-area"
              :d="supplyTrendSeries[0].areaPath"
              style="fill: url(#supplyTrendPrimaryArea)"
            />

            <g class="asset-trend-lines">
              <g v-for="series in supplyTrendSeries" :key="series.label">
                <path
                  :d="series.path"
                  :stroke="series.color"
                  :stroke-dasharray="series.dash"
                />
                <circle
                  v-for="point in series.points"
                  :key="`${series.label}-${point.key}`"
                  :cx="point.x"
                  :cy="point.y"
                  r="3"
                  :fill="series.color"
                />
              </g>
            </g>

            <g class="asset-trend-x-axis">
              <text
                v-for="label in supplyTrendXAxisLabels"
                :key="label.key"
                :x="label.x"
                :y="ASSET_TREND_HEIGHT - 10"
                text-anchor="middle"
              >
                {{ label.text }}
              </text>
            </g>
          </svg>
        </div>
      </section>

      <section class="trend-panel" aria-label="物资趋势坐标图">
        <div class="trend-toolbar" aria-label="趋势图图例">
          <div class="trend-legend">
            <span class="trend-legend-item">
              <i class="legend-bar" :style="{ background: `linear-gradient(180deg, ${palette.bar} 0%, ${palette.barLight} 100%)` }"></i>
              每日新增物资
            </span>
            <span class="trend-legend-item">
              <i class="legend-line" :style="{ background: palette.line }"></i>
              累计物资总数
            </span>
          </div>
        </div>

        <div class="trend-chart-wrap" @pointerleave="clearSupplyChartPoint">
          <svg class="trend-chart" :viewBox="`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`" role="img">
            <defs>
              <linearGradient id="supplyTrendLineArea" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="palette.line" stop-opacity="0.2" />
                <stop offset="100%" :stop-color="palette.line" stop-opacity="0.02" />
              </linearGradient>
              <linearGradient id="supplyTrendBarFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="palette.bar" stop-opacity="0.92" />
                <stop offset="100%" :stop-color="palette.barLight" stop-opacity="0.74" />
              </linearGradient>
            </defs>

            <g class="trend-grid">
              <g v-for="row in supplyChartGridRows" :key="row.value">
                <line :x1="CHART_LEFT" :x2="CHART_RIGHT" :y1="row.y" :y2="row.y" />
                <text :x="CHART_LEFT - 18" :y="row.y + 4" text-anchor="end">
                  {{ row.value }}
                </text>
                <text :x="CHART_RIGHT + 18" :y="row.y + 4" text-anchor="start" class="right-axis">
                  {{ row.rightValue }}
                </text>
              </g>
            </g>

            <path class="trend-area" :d="supplyChartAreaPath" style="fill: url(#supplyTrendLineArea)" />

            <g class="trend-bars">
              <rect
                v-for="bar in supplyChartBars"
                :key="bar.key"
                :x="bar.x"
                :y="bar.y"
                :width="bar.width"
                :height="bar.height"
                rx="4"
                style="fill: url(#supplyTrendBarFill)"
              />
            </g>

            <path class="trend-line" :d="supplyChartLinePath" />

            <g class="trend-points">
              <circle
                v-for="point in supplyChartInteractivePoints"
                :key="point.key"
                :cx="point.x"
                :cy="point.y"
                r="3.2"
              />
            </g>

            <g class="trend-x-axis">
              <text
                v-for="label in supplyChartXAxisLabels"
                :key="label.key"
                :x="label.x"
                :y="CHART_HEIGHT - 12"
                text-anchor="middle"
              >
                {{ label.text }}
              </text>
            </g>

            <g class="trend-hit-layer">
              <rect
                v-for="point in supplyChartInteractivePoints"
                :key="`hit-${point.key}`"
                :x="point.hitX"
                :y="CHART_TOP"
                :width="point.hitWidth"
                :height="CHART_INNER_HEIGHT"
                tabindex="0"
                @focus="setSupplyChartPoint(point)"
                @pointerenter="setSupplyChartPoint(point)"
                @pointermove="setSupplyChartPoint(point)"
                @touchstart.prevent="setSupplyChartPoint(point)"
              />
            </g>
          </svg>

          <div
            v-if="activeSupplyChartPoint"
            class="trend-tooltip"
            :style="activeSupplyChartTooltipStyle"
          >
            <strong>{{ activeSupplyChartPoint.fullDateText }}</strong>
            <span>
              <i class="tooltip-bar" :style="{ background: `linear-gradient(180deg, ${palette.bar} 0%, ${palette.barLight} 100%)` }"></i>
              每日新增物资：{{ formatNumber(activeSupplyChartPoint.barValue) }}
            </span>
            <span>
              <i class="tooltip-line" :style="{ background: palette.line }"></i>
              累计物资总数：{{ formatNumber(activeSupplyChartPoint.lineValue) }}
            </span>
          </div>
        </div>
      </section>
    </template>

    <div v-if="loadError" class="overview-error">
      {{ loadError }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { listAssets } from '../api/assets'
import { listSupplies } from '../api/supplies'
import { listLogs } from '../api/logs'
import { getStoredTheme } from '../utils/theme'

const PAGE_SIZE = 200
const LOG_PAGE_SIZE = 100
const CHART_WIDTH = 1500
const CHART_HEIGHT = 360
const CHART_LEFT = 68
const CHART_RIGHT = 1426
const CHART_TOP = 24
const CHART_BOTTOM = 312
const CHART_DAYS = 44
const CHART_INNER_WIDTH = CHART_RIGHT - CHART_LEFT
const CHART_INNER_HEIGHT = CHART_BOTTOM - CHART_TOP
const ASSET_TREND_WIDTH = 620
const ASSET_TREND_HEIGHT = 250
const ASSET_TREND_LEFT = 38
const ASSET_TREND_RIGHT = 602
const ASSET_TREND_TOP = 18
const ASSET_TREND_BOTTOM = 218
const ASSET_TREND_DAYS = 7
const ASSET_TREND_INNER_WIDTH = ASSET_TREND_RIGHT - ASSET_TREND_LEFT
const ASSET_TREND_INNER_HEIGHT = ASSET_TREND_BOTTOM - ASSET_TREND_TOP
const GAUGE_GAP = 7

const THEME_PALETTES = {
  gold: {
    active:  '#c5a47e',
    warranty:'#5b9bd5',
    idle:    '#a3b8cc',
    scrap:   '#d4645c',
    line:    '#c5a47e',
    lineLight: '#e6d5b8',
    bar:     '#5b9bd5',
    barLight:'#d0e2f4',
    areaFrom:'#c5a47e',
  },
  blue: {
    active:  '#4f8fd8',
    warranty:'#78b8f7',
    idle:    '#a8d1fa',
    scrap:   '#ef4e5a',
    line:    '#4f8fd8',
    lineLight: '#a8d1fa',
    bar:     '#78b8f7',
    barLight:'#d8ebff',
    areaFrom:'#5aaef6',
  },
  green: {
    active:  '#16be91',
    warranty:'#5aaef6',
    idle:    '#8ec8fb',
    scrap:   '#ef4e5a',
    line:    '#18c79a',
    lineLight: '#82e0c0',
    bar:     '#78b8f7',
    barLight:'#d8ebff',
    areaFrom:'#18c79a',
  },
  black: {
    active:  '#111111',
    warranty:'#4b5563',
    idle:    '#9ca3af',
    scrap:   '#d4645c',
    line:    '#111111',
    lineLight: '#6b7280',
    bar:     '#4b5563',
    barLight:'#d1d5db',
    areaFrom:'#111111',
  },
  white: {
    active:  '#f5f7fb',
    warranty:'#cfd6e1',
    idle:    '#9ca3af',
    scrap:   '#ff7b72',
    line:    '#ffffff',
    lineLight: '#d9dee8',
    bar:     '#d9dee8',
    barLight:'#ffffff',
    areaFrom:'#ffffff',
  },
}

const currentTheme = ref(getStoredTheme())
let themeObserver = null

function watchTheme() {
  currentTheme.value = document.documentElement.dataset.theme || getStoredTheme()
  themeObserver = new MutationObserver(() => {
    currentTheme.value = document.documentElement.dataset.theme || 'gold'
  })
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  })
}

const palette = computed(() => THEME_PALETTES[currentTheme.value] || THEME_PALETTES.gold)

const overviewColors = computed(() => ({
  active:  palette.value.active,
  warranty: palette.value.warranty,
  idle:    palette.value.idle,
  scrap:   palette.value.scrap,
}))

const assetTrendPalette = computed(() => [
  { color: overviewColors.value.active, dash: '' },
  { color: overviewColors.value.warranty, dash: '8 5' },
  { color: overviewColors.value.scrap, dash: '' },
  { color: overviewColors.value.idle, dash: '' },
])

/* ===== Scope 切换 ===== */
const overviewScope = ref('asset')

function switchScope(s) {
  if (overviewScope.value === s) return
  overviewScope.value = s
  if (s === 'supply' && supplies.value.length === 0 && !supplyLoaded.value) {
    loadSupplyOverview()
  }
}

/* ===== 资产数据 ===== */
const assets = ref([])
const assetHistoryLogs = ref([])
const loading = ref(false)
const loadError = ref('')
const activeChartPoint = ref(null)

const totalAssets = computed(() => assets.value.length)

const activeCount = computed(() => countStatus(['在用']))
const activeRatio = computed(() => ratio(activeCount.value, totalAssets.value))
const idleCount = computed(() => countStatus(['闲置']))
const idleRatio = computed(() => ratio(idleCount.value, totalAssets.value))
const scrapCount = computed(() => countStatus(['报废', '废弃', '已报废']))
const scrapRatio = computed(() => ratio(scrapCount.value, totalAssets.value))

const warrantyCount = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return assets.value.filter((asset) => {
    if (!asset.warranty_until) return false
    const date = new Date(asset.warranty_until)
    return !Number.isNaN(date.getTime()) && date >= today
  }).length
})
const warrantyRatio = computed(() => ratio(warrantyCount.value, totalAssets.value))

const gaugeSegments = computed(() => {
  if (!totalAssets.value) return []
  const segments = [
    { key: 'active', value: activeRatio.value, color: overviewColors.value.active },
    { key: 'warranty', value: warrantyRatio.value, color: overviewColors.value.warranty },
    { key: 'idle', value: idleRatio.value, color: overviewColors.value.idle },
    { key: 'scrap', value: scrapRatio.value, color: overviewColors.value.scrap },
  ].filter((segment) => segment.value > 0)
  const totalValue = segments.reduce((sum, segment) => sum + segment.value, 0)
  const valueScale = totalValue > 100 ? 100 / totalValue : 1
  const totalGap = Math.max(0, (segments.length - 1) * GAUGE_GAP)
  const availableLength = Math.max(0, 100 - totalGap)
  let cursor = 0
  return segments.map((segment) => {
    const length = Math.max(3, ((segment.value * valueScale) / 100) * availableLength)
    const item = { ...segment, start: Number(cursor.toFixed(2)), length: Number(length.toFixed(2)) }
    cursor += length + GAUGE_GAP
    return item
  })
})

const kpiCards = computed(() => [
  { label: '在用率', value: formatPercent(activeRatio.value), color: overviewColors.value.active },
  { label: '在保率', value: formatPercent(warrantyRatio.value), color: overviewColors.value.warranty },
  { label: '废弃率', value: formatPercent(scrapRatio.value), color: overviewColors.value.scrap },
  { label: '闲置率', value: formatPercent(idleRatio.value), color: overviewColors.value.idle },
])

const assetTrendRange = computed(() => {
  const datedAssets = assets.value.map((a) => parseDate(a.purchase_date)).filter(Boolean)
  const endDate = getTrendEndDate(datedAssets.map((date) => ({ date })))
  const dates = Array.from({ length: ASSET_TREND_DAYS }, (_, i) => addDays(endDate, i - (ASSET_TREND_DAYS - 1)))
  return { endDate, dates }
})

const assetTrendSeries = computed(() => {
  const { dates } = assetTrendRange.value
  const metricDefs = [
    { key: 'active', label: '在用率', getValue: (rows) => ratio(countStatusInRows(rows, ['在用']), rows.length) },
    { key: 'warranty', label: '在保率', getValue: (rows, date) => ratio(countWarrantyInRows(rows, date), rows.length) },
    { key: 'scrap', label: '废弃率', getValue: (rows) => ratio(countStatusInRows(rows, ['报废', '废弃', '已报废']), rows.length) },
    { key: 'idle', label: '闲置率', getValue: (rows) => ratio(countStatusInRows(rows, ['闲置']), rows.length) },
  ]
  return metricDefs.map((metric, si) => {
    const style = assetTrendPalette.value[si % assetTrendPalette.value.length]
    const points = dates.map((date, i) => {
      const rows = assets.value.filter((a) => { const d = parseDate(a.purchase_date); return !d || d <= date })
      const value = metric.getValue(rows, date)
      const x = ASSET_TREND_LEFT + (ASSET_TREND_INNER_WIDTH / (ASSET_TREND_DAYS - 1)) * i
      const y = ASSET_TREND_BOTTOM - (value / 100) * ASSET_TREND_INNER_HEIGHT
      return { key: toDateKey(date), date, value, x, y }
    })
    return { label: metric.label, color: style.color, dash: style.dash, points, path: smoothPath(points), areaPath: si === 0 ? buildAreaPath(points, ASSET_TREND_BOTTOM) : '' }
  })
})

const assetTrendGridRows = computed(() => (
  [100, 75, 50, 25, 0].map((v) => ({ value: v, y: ASSET_TREND_BOTTOM - (v / 100) * ASSET_TREND_INNER_HEIGHT }))
))

const assetTrendXAxisLabels = computed(() => {
  const { dates } = assetTrendRange.value
  return dates.map((date, i) => ({ key: toDateKey(date), text: formatMonthDay(date), x: ASSET_TREND_LEFT + (ASSET_TREND_INNER_WIDTH / (ASSET_TREND_DAYS - 1)) * i }))
})

const trendRows = computed(() => buildTrendRows())

const chartMaxValue = computed(() => { const m = Math.max(...trendRows.value.map((r) => r.barValue), 0); return getNiceMax(m) })
const chartLineMaxValue = computed(() => { const m = Math.max(...trendRows.value.map((r) => r.lineValue), 0); return getNiceMax(m) })

const chartGridRows = computed(() => (
  Array.from({ length: 6 }, (_, i) => {
    const stepRatio = i / 5
    const y = CHART_TOP + CHART_INNER_HEIGHT * stepRatio
    return { y, value: Math.round(chartMaxValue.value * (1 - stepRatio)), rightValue: Math.round(chartLineMaxValue.value * (1 - stepRatio)) }
  })
))

const chartBars = computed(() => {
  const rows = trendRows.value
  if (!rows.length) return []
  const slot = CHART_INNER_WIDTH / rows.length
  const width = Math.max(5, Math.min(12, slot * 0.42))
  return rows.map((row, i) => {
    const h = row.barValue > 0 ? Math.max(2, (row.barValue / chartMaxValue.value) * CHART_INNER_HEIGHT) : 0
    return { key: row.key, x: CHART_LEFT + i * slot + (slot - width) / 2, y: CHART_BOTTOM - h, width, height: h }
  })
})

const chartLinePoints = computed(() => {
  const rows = trendRows.value
  if (!rows.length) return []
  const slot = rows.length > 1 ? CHART_INNER_WIDTH / (rows.length - 1) : 0
  return rows.map((row, i) => ({ x: CHART_LEFT + i * slot, y: CHART_BOTTOM - (row.lineValue / chartLineMaxValue.value) * CHART_INNER_HEIGHT }))
})

const chartInteractivePoints = computed(() => {
  const rows = trendRows.value
  const points = chartLinePoints.value
  if (!rows.length || !points.length) return []
  const slot = rows.length > 1 ? CHART_INNER_WIDTH / (rows.length - 1) : CHART_INNER_WIDTH
  const hitWidth = Math.max(18, Math.min(42, slot * 0.88))
  return rows.map((row, i) => {
    const p = points[i]
    return { ...row, x: p.x, y: p.y, hitX: p.x - hitWidth / 2, hitWidth, fullDateText: toDateKey(row.date) }
  })
})

const activeChartTooltipStyle = computed(() => {
  if (!activeChartPoint.value) return {}
  return { left: `clamp(108px, ${(activeChartPoint.value.x / CHART_WIDTH) * 100}%, calc(100% - 108px))`, top: `${(activeChartPoint.value.y / CHART_HEIGHT) * 100}%` }
})

const chartLinePath = computed(() => pointsToPath(chartLinePoints.value))
const chartAreaPath = computed(() => {
  const p = chartLinePoints.value
  if (!p.length) return ''
  return `${pointsToPath(p)} L ${p.at(-1).x} ${CHART_BOTTOM} L ${p[0].x} ${CHART_BOTTOM} Z`
})

const chartXAxisLabels = computed(() => {
  const rows = trendRows.value
  if (!rows.length) return []
  const slot = rows.length > 1 ? CHART_INNER_WIDTH / (rows.length - 1) : 0
  const labelEvery = rows.length > 36 ? 4 : 3
  return rows.map((row, i) => ({ row, index: i })).filter(({ index }) => index % labelEvery === 0 || index === rows.length - 1).map(({ row, index }) => ({ key: row.key, x: CHART_LEFT + index * slot, text: formatMonthDay(row.date) }))
})

/* ===== 物资数据 ===== */
const supplies = ref([])
const supplyHistoryLogs = ref([])
const supplyLoaded = ref(false)
const activeSupplyChartPoint = ref(null)

const totalSupplies = computed(() => supplies.value.length)
const totalSupplyQuantity = computed(() => supplies.value.reduce((s, r) => s + (Number(r.quantity) || 0), 0))
const uniqueReceivers = computed(() => new Set(supplies.value.map((r) => String(r.receiver || '').trim()).filter(Boolean)).size)
const uniqueItems = computed(() => new Set(supplies.value.map((r) => String(r.item_name || '').trim()).filter(Boolean)).size)

const topReceiverSegments = computed(() => {
  const counts = new Map()
  supplies.value.forEach((r) => {
    const name = String(r.receiver || '').trim()
    if (!name) return
    counts.set(name, (counts.get(name) || 0) + 1)
  })
  const sorted = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 4)
  const colors = [overviewColors.value.active, overviewColors.value.warranty, overviewColors.value.idle, overviewColors.value.scrap]
  return sorted.map(([, count], i) => ({ key: `r${i}`, value: ratio(count, totalSupplies.value), color: colors[i % colors.length] }))
})

const supplyGaugeSegments = computed(() => {
  const segments = topReceiverSegments.value.filter((s) => s.value > 0)
  if (!segments.length && totalSupplies.value > 0) {
    return [{ key: 'all', start: 0, length: 100, color: overviewColors.value.active }]
  }
  const totalValue = segments.reduce((sum, s) => sum + s.value, 0)
  const valueScale = totalValue > 100 ? 100 / totalValue : 1
  const totalGap = Math.max(0, (segments.length - 1) * GAUGE_GAP)
  const availableLength = Math.max(0, 100 - totalGap)
  let cursor = 0
  return segments.map((s) => {
    const length = Math.max(3, ((s.value * valueScale) / 100) * availableLength)
    const item = { ...s, start: Number(cursor.toFixed(2)), length: Number(length.toFixed(2)) }
    cursor += length + GAUGE_GAP
    return item
  })
})

const supplyKpiCards = computed(() => [
  { label: '总发放量', value: formatNumber(totalSupplyQuantity.value), color: overviewColors.value.active },
  { label: '领取人数', value: formatNumber(uniqueReceivers.value), color: overviewColors.value.warranty },
  { label: '物品种类', value: formatNumber(uniqueItems.value), color: overviewColors.value.idle },
  { label: '记录总数', value: formatNumber(totalSupplies.value), color: overviewColors.value.scrap },
])

/* ===== 物资 7 日趋势 ===== */
const supplyTrendRange = computed(() => {
  const datedSupplies = supplies.value.map((r) => parseDate(r.created_at)).filter(Boolean)
  const endDate = getTrendEndDate(datedSupplies.map((date) => ({ date })))
  const dates = Array.from({ length: ASSET_TREND_DAYS }, (_, i) => addDays(endDate, i - (ASSET_TREND_DAYS - 1)))
  return { endDate, dates }
})

const supplyTrendSeries = computed(() => {
  const { dates } = supplyTrendRange.value
  const metricDefs = [
    { key: 'dailyRecords', label: '每日记录数', getValue: (rows) => rows.length },
    { key: 'dailyQty', label: '每日发放量', getValue: (rows) => rows.reduce((s, r) => s + (Number(r.quantity) || 0), 0) },
  ]
  const seriesColors = [
    { color: overviewColors.value.active, dash: '' },
    { color: overviewColors.value.warranty, dash: '8 5' },
  ]
  const allValues = []
  const seriesData = metricDefs.map((metric, si) => {
    const style = seriesColors[si % seriesColors.length]
    const points = dates.map((date, i) => {
      const dayKey = toDateKey(date)
      const rows = supplies.value.filter((r) => { const d = parseDate(r.created_at); return d && toDateKey(d) === dayKey })
      const value = metric.getValue(rows)
      allValues.push(value)
      return { key: dayKey, date, value, x: 0, y: 0 }
    })
    return { label: metric.label, color: style.color, dash: style.dash, points }
  })
  const maxVal = Math.max(...allValues, 1)
  seriesData.forEach((series, si) => {
    series.points.forEach((pt, i) => {
      pt.x = ASSET_TREND_LEFT + (ASSET_TREND_INNER_WIDTH / (ASSET_TREND_DAYS - 1)) * i
      pt.y = ASSET_TREND_BOTTOM - (pt.value / maxVal) * ASSET_TREND_INNER_HEIGHT
    })
    series.path = smoothPath(series.points)
    series.areaPath = si === 0 ? buildAreaPath(series.points, ASSET_TREND_BOTTOM) : ''
  })
  return seriesData
})

const supplyTrendGridRows = computed(() => {
  const allVals = supplyTrendSeries.value.flatMap((s) => s.points.map((p) => p.value))
  const maxVal = Math.max(...allVals, 1)
  const niceMax = getNiceMax(maxVal)
  return [niceMax, Math.round(niceMax * 0.75), Math.round(niceMax * 0.5), Math.round(niceMax * 0.25), 0].map((v) => ({
    value: v,
    y: ASSET_TREND_BOTTOM - (v / niceMax) * ASSET_TREND_INNER_HEIGHT,
  }))
})

const supplyTrendXAxisLabels = computed(() => {
  const { dates } = supplyTrendRange.value
  return dates.map((date, i) => ({ key: toDateKey(date), text: formatMonthDay(date), x: ASSET_TREND_LEFT + (ASSET_TREND_INNER_WIDTH / (ASSET_TREND_DAYS - 1)) * i }))
})

/* ===== 物资 44 日柱线图 ===== */
const supplyTrendRows = computed(() => buildSupplyTrendRows())

function buildSupplyTrendRows() {
  const logRows = buildSupplyTrendRowsFromLogs()
  if (logRows) return logRows
  return buildSupplyTrendRowsFromData()
}

function buildSupplyTrendRowsFromData() {
  const datedSupplies = supplies.value.map((r) => ({ r, date: parseDate(r.created_at) })).filter((item) => item.date)
  const endDate = getTrendEndDate(datedSupplies)
  const startDate = addDays(endDate, -(CHART_DAYS - 1))
  const dayMap = new Map()
  datedSupplies.forEach(({ date }) => {
    if (date < startDate || date > endDate) return
    const key = toDateKey(date)
    dayMap.set(key, (dayMap.get(key) || 0) + 1)
  })
  return Array.from({ length: CHART_DAYS }, (_, i) => {
    const date = addDays(startDate, i)
    const key = toDateKey(date)
    const count = dayMap.get(key) || 0
    const cumulative = datedSupplies.filter((item) => item.date <= date).length
    return { key, date, barValue: count, lineValue: cumulative }
  })
}

function buildSupplyTrendRowsFromLogs() {
  const events = buildSupplyHistoryEvents()
  if (!events.length) return null
  const endDate = getTrendEndDate(events)
  const startDate = addDays(endDate, -(CHART_DAYS - 1))
  const eventsByDay = new Map()
  events.forEach((ev) => {
    if (ev.date > endDate) return
    const key = toDateKey(ev.date)
    const cur = eventsByDay.get(key) || { additions: 0, delta: 0 }
    cur.additions += ev.additions
    cur.delta += ev.delta
    eventsByDay.set(key, cur)
  })
  const netDelta = events.reduce((sum, ev) => (ev.date <= endDate ? sum + ev.delta : sum), 0)
  let cumulative = Math.max(0, totalSupplies.value - netDelta)
  events.forEach((ev) => { if (ev.date < startDate) cumulative = Math.max(0, cumulative + ev.delta) })
  return Array.from({ length: CHART_DAYS }, (_, i) => {
    const date = addDays(startDate, i)
    const key = toDateKey(date)
    const day = eventsByDay.get(key) || { additions: 0, delta: 0 }
    cumulative = Math.max(0, cumulative + day.delta)
    return { key, date, barValue: day.additions, lineValue: cumulative }
  })
}

function buildSupplyHistoryEvents() {
  const events = []
  supplyHistoryLogs.value.forEach((log) => {
    if (log.action === 'supply.create') {
      const date = parseDate(log.created_at)
      if (date) events.push({ date, additions: 1, delta: 1 })
    } else if (log.action === 'supply.delete') {
      const date = parseDate(log.created_at)
      if (date) events.push({ date, additions: 0, delta: -1 })
    }
  })
  return events.sort((a, b) => a.date - b.date)
}

const supplyChartMaxValue = computed(() => getNiceMax(Math.max(...supplyTrendRows.value.map((r) => r.barValue), 0)))
const supplyChartLineMaxValue = computed(() => getNiceMax(Math.max(...supplyTrendRows.value.map((r) => r.lineValue), 0)))

const supplyChartGridRows = computed(() => (
  Array.from({ length: 6 }, (_, i) => {
    const stepRatio = i / 5
    const y = CHART_TOP + CHART_INNER_HEIGHT * stepRatio
    return { y, value: Math.round(supplyChartMaxValue.value * (1 - stepRatio)), rightValue: Math.round(supplyChartLineMaxValue.value * (1 - stepRatio)) }
  })
))

const supplyChartBars = computed(() => {
  const rows = supplyTrendRows.value
  if (!rows.length) return []
  const slot = CHART_INNER_WIDTH / rows.length
  const width = Math.max(5, Math.min(12, slot * 0.42))
  return rows.map((row, i) => {
    const h = row.barValue > 0 ? Math.max(2, (row.barValue / supplyChartMaxValue.value) * CHART_INNER_HEIGHT) : 0
    return { key: row.key, x: CHART_LEFT + i * slot + (slot - width) / 2, y: CHART_BOTTOM - h, width, height: h }
  })
})

const supplyChartLinePoints = computed(() => {
  const rows = supplyTrendRows.value
  if (!rows.length) return []
  const slot = rows.length > 1 ? CHART_INNER_WIDTH / (rows.length - 1) : 0
  return rows.map((row, i) => ({ x: CHART_LEFT + i * slot, y: CHART_BOTTOM - (row.lineValue / supplyChartLineMaxValue.value) * CHART_INNER_HEIGHT }))
})

const supplyChartInteractivePoints = computed(() => {
  const rows = supplyTrendRows.value
  const points = supplyChartLinePoints.value
  if (!rows.length || !points.length) return []
  const slot = rows.length > 1 ? CHART_INNER_WIDTH / (rows.length - 1) : CHART_INNER_WIDTH
  const hitWidth = Math.max(18, Math.min(42, slot * 0.88))
  return rows.map((row, i) => {
    const p = points[i]
    return { ...row, x: p.x, y: p.y, hitX: p.x - hitWidth / 2, hitWidth, fullDateText: toDateKey(row.date) }
  })
})

const activeSupplyChartTooltipStyle = computed(() => {
  if (!activeSupplyChartPoint.value) return {}
  return { left: `clamp(108px, ${(activeSupplyChartPoint.value.x / CHART_WIDTH) * 100}%, calc(100% - 108px))`, top: `${(activeSupplyChartPoint.value.y / CHART_HEIGHT) * 100}%` }
})

const supplyChartLinePath = computed(() => pointsToPath(supplyChartLinePoints.value))
const supplyChartAreaPath = computed(() => {
  const p = supplyChartLinePoints.value
  if (!p.length) return ''
  return `${pointsToPath(p)} L ${p.at(-1).x} ${CHART_BOTTOM} L ${p[0].x} ${CHART_BOTTOM} Z`
})

const supplyChartXAxisLabels = computed(() => {
  const rows = supplyTrendRows.value
  if (!rows.length) return []
  const slot = rows.length > 1 ? CHART_INNER_WIDTH / (rows.length - 1) : 0
  const labelEvery = rows.length > 36 ? 4 : 3
  return rows.map((row, i) => ({ row, index: i })).filter(({ index }) => index % labelEvery === 0 || index === rows.length - 1).map(({ row, index }) => ({ key: row.key, x: CHART_LEFT + index * slot, text: formatMonthDay(row.date) }))
})

function setSupplyChartPoint(p) { activeSupplyChartPoint.value = p }
function clearSupplyChartPoint() { activeSupplyChartPoint.value = null }

/* ===== 资产趋势构建 ===== */
function buildTrendRows() {
  const fromLogs = buildTrendRowsFromLogs()
  if (fromLogs) return fromLogs
  return buildTrendRowsFromAssets()
}

function buildTrendRowsFromAssets() {
  const datedAssets = assets.value.map((a) => ({ asset: a, date: parseDate(a.purchase_date) })).filter((item) => item.date)
  const undatedCount = Math.max(0, assets.value.length - datedAssets.length)
  const endDate = getTrendEndDate(datedAssets)
  const startDate = addDays(endDate, -(CHART_DAYS - 1))
  const dayMap = new Map()
  datedAssets.forEach(({ asset, date }) => {
    if (date < startDate || date > endDate) return
    const key = toDateKey(date)
    const cur = dayMap.get(key) || { count: 0, active: 0 }
    cur.count += 1
    if (String(asset.status || '').trim() === '在用') cur.active += 1
    dayMap.set(key, cur)
  })
  if (!dayMap.size) return buildFlatTrendRows(endDate, undatedCount)
  return Array.from({ length: CHART_DAYS }, (_, i) => {
    const date = addDays(startDate, i)
    const key = toDateKey(date)
    const day = dayMap.get(key) || { count: 0, active: 0 }
    const cumulative = undatedCount + datedAssets.filter((item) => item.date <= date).length
    return { key, date, barValue: day.count, lineValue: cumulative }
  })
}

function buildTrendRowsFromLogs() {
  const events = buildHistoryEvents()
  if (!events.length) return null
  const endDate = getTrendEndDate(events)
  const startDate = addDays(endDate, -(CHART_DAYS - 1))
  const eventsByDay = new Map()
  events.forEach((ev) => {
    if (ev.date > endDate) return
    const key = toDateKey(ev.date)
    const cur = eventsByDay.get(key) || { additions: 0, delta: 0 }
    cur.additions += ev.additions
    cur.delta += ev.delta
    eventsByDay.set(key, cur)
  })
  const netDelta = events.reduce((sum, ev) => (ev.date <= endDate ? sum + ev.delta : sum), 0)
  let cumulative = Math.max(0, totalAssets.value - netDelta)
  events.forEach((ev) => { if (ev.date < startDate) cumulative = Math.max(0, cumulative + ev.delta) })
  return Array.from({ length: CHART_DAYS }, (_, i) => {
    const date = addDays(startDate, i)
    const key = toDateKey(date)
    const day = eventsByDay.get(key) || { additions: 0, delta: 0 }
    cumulative = Math.max(0, cumulative + day.delta)
    return { key, date, barValue: day.additions, lineValue: cumulative }
  })
}

function buildHistoryEvents() {
  const events = []
  assetHistoryLogs.value.forEach((log) => {
    if (log.action === 'asset.create') {
      const date = parseDate(changeAfter(log, 'purchase_date') || log.created_at)
      if (date) events.push({ date, additions: 1, delta: 1 })
      return
    }
    if (log.action === 'asset.import') {
      const dailyCounts = log.extra?.daily_counts
      if (dailyCounts && typeof dailyCounts === 'object') {
        Object.entries(dailyCounts).forEach(([dateText, count]) => {
          const date = parseDate(dateText)
          const value = Math.max(0, Number(count) || 0)
          if (date && value > 0) events.push({ date, additions: value, delta: value })
        })
      }
      const undatedSuccess = Math.max(0, Number(log.extra?.undated_success) || 0)
      const fallbackSuccess = dailyCounts ? 0 : parseImportSuccess(log)
      const fallbackCount = undatedSuccess || fallbackSuccess
      if (fallbackCount > 0) {
        const date = parseDate(log.created_at)
        if (date) events.push({ date, additions: fallbackCount, delta: fallbackCount })
      }
      return
    }
    if (log.action === 'asset.delete') {
      const date = parseDate(log.created_at)
      if (date) events.push({ date, additions: 0, delta: -1 })
    }
  })
  return events.sort((a, b) => a.date - b.date)
}

function changeAfter(log, field) {
  const change = (log.changes || []).find((item) => item.field === field)
  return change?.after || null
}

function parseImportSuccess(log) {
  const extraSuccess = Number(log.extra?.success)
  if (Number.isFinite(extraSuccess) && extraSuccess > 0) return extraSuccess
  const match = String(log.summary || '').match(/成功\s*(\d+)/)
  return match ? Number(match[1]) : 0
}

function buildFlatTrendRows(endDate, cumulativeValue = 0) {
  const startDate = addDays(endDate, -(CHART_DAYS - 1))
  return Array.from({ length: CHART_DAYS }, (_, i) => {
    const date = addDays(startDate, i)
    return { key: toDateKey(date), date, barValue: 0, lineValue: Math.max(0, cumulativeValue) }
  })
}

/* ===== 通用工具 ===== */
function parseDate(v) { if (!v) return null; const d = new Date(v); if (Number.isNaN(d.getTime())) return null; d.setHours(0, 0, 0, 0); return d }
function getTrendEndDate(datedItems) { const latest = datedItems.reduce((r, item) => (!r || item.date > r ? item.date : r), null); const d = latest ? new Date(latest) : new Date(); d.setHours(0, 0, 0, 0); return d }
function addDays(d, n) { const r = new Date(d); r.setDate(r.getDate() + n); return r }
function toDateKey(d) { return `${d.getFullYear()}-${`${d.getMonth() + 1}`.padStart(2, '0')}-${`${d.getDate()}`.padStart(2, '0')}` }
function formatMonthDay(d) { return `${d.getMonth() + 1}/${d.getDate()}` }
function pointsToPath(pts) { if (!pts.length) return ''; return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' ') }

function smoothPath(points) {
  if (points.length < 3) return pointsToPath(points)
  const cp = (cur, prev, next, rev = false) => {
    const p = prev || cur; const n = next || cur; const sm = 0.18
    const angle = Math.atan2(n.y - p.y, n.x - p.x) + (rev ? Math.PI : 0)
    const len = Math.hypot(n.x - p.x, n.y - p.y) * sm
    return { x: cur.x + Math.cos(angle) * len, y: cur.y + Math.sin(angle) * len }
  }
  return points.reduce((path, pt, i, all) => {
    if (i === 0) return `M ${pt.x.toFixed(2)} ${pt.y.toFixed(2)}`
    const sc = cp(all[i - 1], all[i - 2], pt)
    const ec = cp(pt, all[i - 1], all[i + 1], true)
    return `${path} C ${sc.x.toFixed(2)} ${sc.y.toFixed(2)}, ${ec.x.toFixed(2)} ${ec.y.toFixed(2)}, ${pt.x.toFixed(2)} ${pt.y.toFixed(2)}`
  }, '')
}

function buildAreaPath(points, baselineY) { if (!points.length) return ''; const line = smoothPath(points); return `${line} L ${points.at(-1).x.toFixed(2)} ${baselineY} L ${points[0].x.toFixed(2)} ${baselineY} Z` }
function getNiceMax(v) { const r = Math.max(v, 5); if (r <= 25) return Math.ceil(r / 5) * 5; if (r <= 100) return Math.ceil(r / 20) * 20; if (r <= 250) return Math.ceil(r / 50) * 50; return Math.ceil(r / 100) * 100 }
function setActiveChartPoint(p) { activeChartPoint.value = p }
function clearActiveChartPoint() { activeChartPoint.value = null }
function countStatus(aliases) { return assets.value.filter((a) => aliases.includes(String(a.status || '').trim())).length }
function countStatusInRows(rows, aliases) { return rows.filter((a) => aliases.includes(String(a.status || '').trim())).length }
function countWarrantyInRows(rows, date) { return rows.filter((a) => { if (!a.warranty_until) return false; const d = new Date(a.warranty_until); return !Number.isNaN(d.getTime()) && d >= date }).length }
function ratio(v, t) { if (!t) return 0; return Number(((v / t) * 100).toFixed(1)) }
function formatNumber(v) { return new Intl.NumberFormat('zh-CN').format(Number(v) || 0) }
function formatPercent(v) { return `${(Number(v) || 0).toFixed(1)}%` }

/* ===== 数据加载 ===== */
async function loadOverview() {
  loading.value = true
  loadError.value = ''
  try {
    const [rows, logs] = await Promise.all([loadAllAssets(), loadAssetHistoryLogs()])
    assets.value = rows
    assetHistoryLogs.value = logs
  } catch {
    loadError.value = '总览数据加载失败'
  } finally {
    loading.value = false
  }
}

async function loadSupplyOverview() {
  loading.value = true
  loadError.value = ''
  try {
    const [rows, logs] = await Promise.all([loadAllSupplies(), loadSupplyHistoryLogs()])
    supplies.value = rows
    supplyHistoryLogs.value = logs
    supplyLoaded.value = true
  } catch {
    loadError.value = '物资总览数据加载失败'
  } finally {
    loading.value = false
  }
}

async function loadAllAssets() {
  const first = await listAssets({ page: 1, page_size: PAGE_SIZE })
  const total = Number(first?.total || 0)
  const rows = Array.isArray(first?.items) ? [...first.items] : []
  const pageCount = Math.ceil(total / PAGE_SIZE)
  for (let p = 2; p <= pageCount; p += 1) {
    const data = await listAssets({ page: p, page_size: PAGE_SIZE })
    if (Array.isArray(data?.items)) rows.push(...data.items)
  }
  return rows
}

async function loadAllSupplies() {
  const first = await listSupplies({ page: 1, page_size: PAGE_SIZE })
  const total = Number(first?.total || 0)
  const rows = Array.isArray(first?.items) ? [...first.items] : []
  const pageCount = Math.ceil(total / PAGE_SIZE)
  for (let p = 2; p <= pageCount; p += 1) {
    const data = await listSupplies({ page: p, page_size: PAGE_SIZE })
    if (Array.isArray(data?.items)) rows.push(...data.items)
  }
  return rows
}

async function loadAssetHistoryLogs() {
  const actions = ['asset.create', 'asset.import', 'asset.delete']
  const groups = await Promise.all(actions.map((a) => loadLogsByAction(a)))
  return groups.flat()
}

async function loadSupplyHistoryLogs() {
  const actions = ['supply.create', 'supply.delete']
  const groups = await Promise.all(actions.map((a) => loadLogsByAction(a)))
  return groups.flat()
}

async function loadLogsByAction(action) {
  const first = await listLogs({ page: 1, page_size: LOG_PAGE_SIZE, scope: 'all', action })
  const total = Number(first?.total || 0)
  const rows = Array.isArray(first?.items) ? [...first.items] : []
  const pageCount = Math.ceil(total / LOG_PAGE_SIZE)
  for (let p = 2; p <= pageCount; p += 1) {
    const data = await listLogs({ page: p, page_size: LOG_PAGE_SIZE, scope: 'all', action })
    if (Array.isArray(data?.items)) rows.push(...data.items)
  }
  return rows
}

onMounted(() => {
  watchTheme()
  loadOverview()
})

onUnmounted(() => {
  if (themeObserver) { themeObserver.disconnect(); themeObserver = null }
})
</script>

<style scoped>
.overview-page {
  --overview-page-pad-x: 32px;
  min-height: calc(100% + 40px);
  margin: -20px -24px;
  padding: 28px var(--overview-page-pad-x);
  background: var(--bg-page);
  color: var(--text-primary);
  font-family: 'HarmonyOS Sans SC', 'Noto Sans SC', 'PingFang SC',
    'Microsoft YaHei UI', 'Microsoft YaHei', -apple-system,
    BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
}

/* ===== Scope 切换条 ===== */
.overview-scope-bar {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
  animation: overview-fade-up 0.42s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.overview-scope-switch {
  position: relative;
  display: inline-flex;
  gap: 0;
  background: transparent;
  border-radius: 8px;
  padding: 3px;
  isolation: isolate;
}

.overview-scope-indicator {
  position: absolute;
  top: 3px;
  bottom: 3px;
  width: calc(50% - 3px);
  background: rgba(var(--theme-primary-rgb), 0.22);
  border-radius: 6px;
  z-index: 0;
  transition: left 0.34s cubic-bezier(0.22, 1, 0.36, 1),
    background-color 0.2s ease;
  pointer-events: none;
}

.overview-scope-switch[data-scope="asset"] .overview-scope-indicator {
  left: 3px;
}

.overview-scope-switch[data-scope="supply"] .overview-scope-indicator {
  left: calc(50%);
}

.overview-scope-btn {
  position: relative;
  z-index: 1;
  appearance: none;
  border: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--theme-primary-deep, #8a7355);
  background: transparent;
  padding: 7px 28px;
  border-radius: 6px;
  cursor: pointer;
  user-select: none;
  transition: color 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  letter-spacing: 1px;
}

.overview-scope-btn:hover:not(.active) {
  color: var(--theme-text-hover, #5e4a2e);
}

.overview-scope-btn.active {
  color: var(--text-primary, #2f2f33);
  font-weight: 700;
}

/* ===== 展示区 ===== */
.overview-showcase {
  --overview-text: #0c1429;
  --overview-label: #6e7d96;
  --overview-muted: rgba(105, 118, 148, 0.13);
  --overview-separator: rgba(118, 135, 162, 0.14);
  display: grid;
  grid-template-columns: minmax(360px, 410px) minmax(320px, 360px) minmax(560px, 620px);
  column-gap: 24px;
  align-items: stretch;
  justify-content: center;
  width: 100%;
  max-width: 1480px;
  min-height: 238px;
  margin: 0 auto;
  overflow: visible;
  background: transparent;
  animation: overview-fade-up 0.52s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.gauge-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  padding: 20px 22px 12px;
  animation: overview-fade-up 0.56s cubic-bezier(0.22, 1, 0.36, 1) 0.06s both;
}

.gauge-wrap {
  position: relative;
  width: min(100%, 360px);
  aspect-ratio: 360 / 230;
}

.gauge-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.gauge-svg path { fill: none; }

.gauge-segment {
  stroke-width: 22;
  stroke-linecap: round;
  filter:
    drop-shadow(0 9px 16px rgba(var(--theme-primary-rgb), 0.18))
    drop-shadow(0 2px 4px rgba(var(--theme-primary-rgb), 0.10));
  transform-box: fill-box;
  transform-origin: center bottom;
  animation: overview-scale-in 0.56s cubic-bezier(0.22, 1, 0.36, 1) 0.16s both;
}

.gauge-center {
  position: absolute;
  inset: 76px 0 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.gauge-center strong {
  color: var(--overview-text);
  font-size: clamp(42px, 4vw, 58px);
  font-weight: 750;
  line-height: 1;
}

.gauge-center span {
  margin-top: 13px;
  color: var(--overview-label);
  font-size: 16px;
  font-weight: 600;
}

.kpi-panel {
  display: grid;
  grid-template-columns: repeat(2, minmax(150px, 1fr));
  align-content: center;
  row-gap: 22px;
  column-gap: 34px;
  min-width: 0;
  padding: 30px 28px;
  animation: overview-fade-up 0.56s cubic-bezier(0.22, 1, 0.36, 1) 0.12s both;
}

.kpi-item { min-width: 0; animation: overview-fade-up 0.48s cubic-bezier(0.22, 1, 0.36, 1) both; }
.kpi-item:nth-child(1) { animation-delay: 0.16s; }
.kpi-item:nth-child(2) { animation-delay: 0.2s; }
.kpi-item:nth-child(3) { animation-delay: 0.24s; }
.kpi-item:nth-child(4) { animation-delay: 0.28s; }

.kpi-label {
  display: flex;
  align-items: center;
  gap: 7px;
  min-height: 22px;
  color: var(--overview-label);
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.kpi-dot { flex: 0 0 auto; width: 7px; height: 7px; border-radius: 50%; }

.kpi-label i {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  color: color-mix(in srgb, var(--overview-label) 72%, #ffffff);
  font-size: 10px;
  font-style: normal;
  font-weight: 700;
  border: 1px solid currentColor;
  border-radius: 50%;
}

.kpi-item strong {
  display: block;
  margin-top: 10px;
  color: var(--overview-text);
  font-size: 32px;
  font-weight: 760;
  line-height: 1;
}

.asset-trend-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  padding: 18px 14px 14px 18px;
  animation: overview-fade-up 0.56s cubic-bezier(0.22, 1, 0.36, 1) 0.18s both;
}

.asset-trend-legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
  min-height: 24px;
  color: var(--overview-label);
  font-size: 12px;
  font-weight: 650;
  white-space: nowrap;
}

.asset-trend-legend-item { display: inline-flex; align-items: center; gap: 6px; min-width: 0; }
.asset-trend-legend-item i { flex: 0 0 auto; width: 8px; height: 8px; border-radius: 50%; }

.asset-trend-chart {
  display: block;
  width: 100%;
  height: 210px;
  margin-top: 2px;
  overflow: visible;
  animation: overview-fade-in 0.58s ease 0.28s both;
}

.asset-trend-grid line { stroke: rgba(128, 146, 174, 0.16); stroke-width: 1; }
.asset-trend-grid text,
.asset-trend-x-axis text { fill: #8fa0bc; font-size: 12px; font-weight: 650; }
.asset-trend-area { fill: url(#assetTrendPrimaryArea); }
.asset-trend-lines path { fill: none; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; animation: overview-fade-in 0.5s ease 0.34s both; }
.asset-trend-lines circle { stroke: var(--bg-page); stroke-width: 2; animation: overview-scale-in 0.42s cubic-bezier(0.22, 1, 0.36, 1) 0.38s both; }

.trend-panel {
  --trend-grid: rgba(128, 146, 174, 0.18);
  --trend-axis: #91a3bd;
  --trend-line: var(--theme-primary, #c5a47e);
  --trend-right-axis: var(--theme-primary-light-3, #d4b89a);
  width: 100vw;
  margin-top: 14px;
  margin-left: calc(50% - 50vw);
  padding: 0 48px;
  box-sizing: border-box;
  min-height: 360px;
  background: transparent;
  animation: overview-fade-up 0.58s cubic-bezier(0.22, 1, 0.36, 1) 0.28s both;
}

.trend-toolbar {
  display: flex;
  justify-content: flex-end;
  min-height: 24px;
  margin-bottom: 8px;
  padding-right: 90px;
}

.trend-legend { display: flex; align-items: center; gap: 24px; color: var(--trend-axis); font-size: 13px; font-weight: 650; white-space: nowrap; }
.trend-legend-item { display: inline-flex; align-items: center; gap: 8px; }
.legend-bar { width: 18px; height: 10px; border-radius: 3px; }
.legend-line { position: relative; width: 22px; height: 2px; border-radius: 999px; }
.legend-line::after { content: ''; position: absolute; top: 50%; left: 50%; width: 7px; height: 7px; border-radius: 50%; background: inherit; transform: translate(-50%, -50%); }

.trend-chart { display: block; width: 100%; height: 360px; overflow: visible; }
.trend-chart-wrap { position: relative; width: 100%; min-height: 360px; overflow: visible; }
.trend-grid line { stroke: var(--trend-grid); stroke-dasharray: 3 8; stroke-width: 1; }
.trend-grid text,
.trend-x-axis text { fill: var(--trend-axis); font-size: 12px; font-weight: 650; }
.trend-grid .right-axis { fill: var(--trend-right-axis); }
.trend-area { fill: url(#trendLineArea); }
.trend-bars rect { fill: url(#trendBarFill); transform-box: fill-box; transform-origin: center bottom; animation: overview-bar-grow 0.64s cubic-bezier(0.22, 1, 0.36, 1) 0.42s both; }
.trend-line { fill: none; stroke: var(--trend-line); stroke-width: 2.2; stroke-linejoin: round; stroke-linecap: round; animation: overview-fade-in 0.52s ease 0.48s both; }
.trend-points circle { fill: var(--trend-line); opacity: 0.72; stroke: var(--bg-page); stroke-width: 2; animation: overview-scale-in 0.42s cubic-bezier(0.22, 1, 0.36, 1) 0.56s both; }
.trend-hit-layer rect { cursor: crosshair; fill: transparent; outline: none; pointer-events: all; }
.trend-hit-layer rect:focus { outline: none; }

.trend-tooltip {
  position: absolute;
  z-index: 3;
  min-width: 180px;
  padding: 10px 12px;
  color: #0c1429;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(126, 145, 174, 0.2);
  border-radius: 8px;
  box-shadow: 0 12px 28px rgba(28, 40, 70, 0.13);
  pointer-events: none;
  transform: translate(-50%, calc(-100% - 14px));
}
.trend-tooltip::after { content: ''; position: absolute; bottom: -6px; left: 50%; width: 10px; height: 10px; background: inherit; border-right: 1px solid rgba(126, 145, 174, 0.2); border-bottom: 1px solid rgba(126, 145, 174, 0.2); transform: translateX(-50%) rotate(45deg); }
.trend-tooltip strong, .trend-tooltip span { position: relative; z-index: 1; }
.trend-tooltip strong { display: block; margin-bottom: 8px; font-size: 13px; font-weight: 760; }
.trend-tooltip span { display: flex; align-items: center; gap: 8px; margin-top: 5px; color: #697894; font-size: 12px; font-weight: 650; white-space: nowrap; }
.trend-tooltip i { flex: 0 0 auto; }
.tooltip-bar { width: 14px; height: 8px; border-radius: 3px; }
.tooltip-line { width: 14px; height: 3px; border-radius: 999px; }

.overview-error { margin-top: 18px; color: #c44545; font-size: 14px; }

/* ===== Dark mode ===== */
:global(html.dark .overview-showcase) {
  --overview-text: var(--text-primary);
  --overview-label: rgba(236, 237, 241, 0.7);
  --overview-muted: rgba(255, 255, 255, 0.08);
  --overview-separator: rgba(255, 255, 255, 0.08);
}
:global(html.dark .overview-page) {
  --overview-text: #f5f7fb;
  --overview-label: rgba(231, 237, 247, 0.78);
  --trend-axis: rgba(231, 237, 247, 0.72);
  color: var(--text-primary);
}
:global(html.dark .overview-page .gauge-center strong),
:global(html.dark .overview-page .kpi-item strong) { color: #f5f7fb !important; -webkit-text-fill-color: #f5f7fb; text-shadow: 0 0 16px rgba(120, 184, 247, 0.08); }
:global(html.dark .overview-page .gauge-center span),
:global(html.dark .overview-page .kpi-label),
:global(html.dark .overview-page .asset-trend-legend),
:global(html.dark .overview-page .trend-legend) { color: rgba(231, 237, 247, 0.78) !important; }
:global(html.dark .overview-page .kpi-label i) { color: rgba(231, 237, 247, 0.64) !important; border-color: rgba(231, 237, 247, 0.5); }
:global(html.dark .overview-page .asset-trend-grid line) { stroke: rgba(255, 255, 255, 0.08); }
:global(html.dark .overview-page .asset-trend-grid text),
:global(html.dark .overview-page .asset-trend-x-axis text),
:global(html.dark .overview-page .trend-grid text),
:global(html.dark .overview-page .trend-x-axis text) { fill: rgba(231, 237, 247, 0.72) !important; }
:global(html.dark .overview-page .trend-grid .right-axis) { fill: var(--theme-primary-light-3) !important; }
:global(html.dark .trend-panel) { --trend-grid: rgba(255, 255, 255, 0.08); --trend-axis: rgba(236, 237, 241, 0.64); --trend-line: var(--theme-primary, #c5a47e); --trend-right-axis: var(--theme-primary-light-3, #d4b89a); }
:global(html.dark .trend-tooltip) { color: var(--text-primary); background: rgba(29, 29, 36, 0.96); border-color: rgba(255, 255, 255, 0.08); box-shadow: 0 14px 30px rgba(0, 0, 0, 0.26); }
:global(html.dark .trend-tooltip span) { color: var(--text-secondary); }
:global(html.dark .trend-tooltip strong) { color: var(--text-primary); }
:global(html.dark .overview-scope-switch) { background: transparent; }
:global(html.dark .overview-scope-indicator) { background: rgba(255, 255, 255, 0.12); }
:global(html.dark .overview-scope-btn) { color: rgba(231, 237, 247, 0.64); }
:global(html.dark .overview-scope-btn.active) { color: #f5f7fb; }

/* ===== Animations ===== */
@keyframes overview-fade-up { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
@keyframes overview-fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes overview-scale-in { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }
@keyframes overview-bar-grow { from { opacity: 0; transform: scaleY(0.18); } to { opacity: 1; transform: scaleY(1); } }

@media (prefers-reduced-motion: reduce) {
  .overview-showcase, .gauge-panel, .gauge-segment, .kpi-panel, .kpi-item,
  .asset-trend-panel, .asset-trend-chart, .asset-trend-lines path, .asset-trend-lines circle,
  .trend-panel, .trend-bars rect, .trend-line, .trend-points circle, .overview-scope-bar { animation: none !important; }
}

@media (max-width: 1360px) {
  .overview-showcase { grid-template-columns: minmax(340px, 0.95fr) minmax(340px, 1fr); }
  .asset-trend-panel { grid-column: 1 / -1; }
}

@media (max-width: 860px) {
  .overview-page { --overview-page-pad-x: 16px; padding: 22px var(--overview-page-pad-x); }
  .overview-showcase { grid-template-columns: 1fr; }
  .gauge-panel { padding-top: 28px; }
  .kpi-panel { padding: 12px 28px 30px; }
  .asset-trend-panel { padding: 24px 20px; }
  .trend-panel, .trend-chart-wrap, .trend-chart { min-height: 300px; height: 300px; }
  .trend-panel { padding: 0 22px; }
  .trend-toolbar { justify-content: flex-start; margin-bottom: 4px; }
  .trend-legend { gap: 18px; font-size: 12px; }
}

@media (max-width: 520px) {
  .kpi-panel { grid-template-columns: 1fr; row-gap: 22px; }
  .asset-trend-legend { justify-content: flex-start; flex-wrap: wrap; }
}
</style>
