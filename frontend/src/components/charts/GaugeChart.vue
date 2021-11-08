<template>
  <div :id="renderId()" :style="{width: '100%', height: height}" />
</template>

<script>
import * as echarts from "echarts"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  props: {
    agent_id: {
      type: String,
      required: true
    },
    graph_name: {
      type: String,
      required: true
    },
    height: {
      type: String,
      default: "200px"
    }
  },

  data: () => ({
    options: {
      series: [{
        type: "gauge",
        center: ["50%", "70%"],
        radius: "110%",
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        splitNumber: 5,
        itemStyle: {
          color: "#F49B51"
        },
        progress: {
          show: true,
          roundCap: true,
          width: 25
        },
        pointer: {
          length: "80%",
          width: 5,
          offsetCenter: [0, "5%"]
        },
        axisLine: {
          roundCap: false,
          lineStyle: {
            width: 25
          }
        },
        axisTick: {
          splitNumber: 2,
          lineStyle: {
            width: 2,
            color: "#999"
          }
        },
        splitLine: {
          length: 0,
          lineStyle: {
            width: 1,
            color: "#999"
          }
        },
        axisLabel: {
          distance: 40,
          color: "#999",
          fontSize: 20
        },
        title: {
          show: false
        },
        detail: {
          backgroundColor: "#fff",
          borderColor: "#999",
          borderWidth: 2,
          width: "20%",
          lineHeight: 20,
          height: 20,
          borderRadius: 8,
          offsetCenter: [0, "30%"],
          valueAnimation: true,
          formatter: function(value) {
            return "{value|" + value.toFixed(0) + "}{unit|%}"
          },
          rich: {
            value: {
              fontSize: 20,
              fontWeight: "bolder",
              color: "#777"
            },
            unit: {
              fontSize: 10,
              color: "#999",
              padding: [0, 0, 0, 5]
            }
          }
        },
        data: [
          {
            value: 0
          }
        ]
      }
      ] }
  }),

  mounted() {
    setTimeout(() => {
      this.initChart()
    }, 100)
  },

  methods: {
    resize() {
      this.chart.resize()
    },

    renderId() {
      return `graph_${this.agent_id}_${this.graph_name}`
    },

    updateData(val) {
      this.options.series[0].data[0].value = val
      this.chart.setOption(this.options)
    },

    initChart() {
      this.chart = echarts.init(document.getElementById(this.renderId()))
      this.chart.setOption(this.options)
      this.resize()
    }
  }
})
</script>
