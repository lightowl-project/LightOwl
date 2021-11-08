<template>
  <div class="chart-container">
    <div id="chart" class="chart" :style="{ height: '100%', width: '100%' }" />
    <el-card
      class="create-dashboard-card text-center"
      :style="{ width: '500px' }"
    >
      <h2>{{ $t("Create a widget") }}</h2>

      <el-button type="primary" @click="$emit('newWidget')">
        <i class="fa fa-plus mr-2" />{{ $t("Create") }}
      </el-button>
    </el-card>
  </div>
</template>

<script>
import * as echarts from "echarts"
import resize from "@/mixins/resize"

export default {
  mixins: [resize],
  props: {},

  data() {
    return {
      chart: null
    }
  },

  mounted() {
    setTimeout(() => {
      this.initChart()
    }, 200)
  },

  beforeDestroy() {
    if (!this.chart) return
    this.chart.dispose()
    this.chart = null
  },

  methods: {
    initChart() {
      this.chart = echarts.init(document.getElementById("chart"))
      const xAxisData = []
      const data = []
      const data2 = []

      for (let i = 0; i < 50; i++) {
        xAxisData.push(i)
        data.push((Math.sin(i / 5) * (i / 5 - 10) + i / 6) * 5)
        data2.push((Math.sin(i / 5) * (i / 5 + 10) + i / 6) * 3)
      }

      this.chart.setOption({
        backgroundColor: "#08263a",
        grid: {
          left: "5%",
          right: "5%"
        },
        xAxis: [
          {
            show: false,
            data: xAxisData
          },
          {
            show: false,
            data: xAxisData
          }
        ],
        visualMap: {
          show: false,
          min: 0,
          max: 50,
          dimension: 0,
          inRange: {
            color: [
              "#4a657a",
              "#308e92",
              "#b1cfa5",
              "#f5d69f",
              "#f5898b",
              "#ef5055"
            ]
          }
        },
        yAxis: {
          axisLine: {
            show: false
          },
          axisLabel: {
            color: "#4a657a"
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: "#08263f"
            }
          },
          axisTick: {
            show: false
          }
        },
        series: [
          {
            name: "back",
            type: "bar",
            data: data2,
            z: 1,
            itemStyle: {
              opacity: 0.4,
              borderRadius: 5,
              shadowBlur: 3,
              shadowColor: "#111"
            }
          },
          {
            name: "Simulate Shadow",
            type: "line",
            data,
            z: 2,
            showSymbol: false,
            animationDelay: 0,
            animationEasing: "linear",
            animationDuration: 1200,
            lineStyle: {
              color: "transparent"
            },
            areaStyle: {
              color: "#08263a",
              shadowBlur: 50,
              shadowColor: "#000"
            }
          },
          {
            name: "front",
            type: "bar",
            data,
            xAxisIndex: 1,
            z: 3,
            itemStyle: {
              borderRadius: 5
            }
          }
        ],
        animationEasing: "elasticOut",
        animationEasingUpdate: "elasticOut",
        animationDelay(idx) {
          return idx * 20
        },
        animationDelayUpdate(idx) {
          return idx * 20
        }
      })
    }
  }
}
</script>

<style scoped>
.create-dashboard-card {
  position: absolute;
  top: 30%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>
