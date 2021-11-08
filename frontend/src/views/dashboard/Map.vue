<template>
  <div class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#304156"
      text-color="#fff"
      active-text-color="#F58320"
      router
    />

    <div id="map" style="width: 100%; height: 1000px" />
  </div>
</template>

<script>
import * as echarts from "echarts"
import request from "@/utils/request"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  data: () => ({
    agents: [],
    options: {
      series: [
        {
          label: {
            position: "insideTopLeft",
            formatter: (params) => {
              // console.log(params.data)
            }
          },
          type: "treemap",
          levels: [{
            colors: ["#c23531", "#314656", "#61a0a8", "#dd8668", "#91c7ae", "#6e7074", "#61a0a8", "#bda29a", "#44525d", "#c4ccd3"]
          }],
          data: []
        }
      ]
    }
  }),

  async beforeMount() {
    let response = await request.get("/api/v1/agents/", { params: { all: true }})
    this.agents = response.data

    for (const agent of this.agents) {
      response = await request.get(`/api/v1/agents/inputs/${agent._id}`)
      const childrens = []
      for (const input of response.data) {
        childrens.push({
          name: input.plugin_name,
          value: 1
        })
      }

      const tmp = {
        name: `${agent.ip_address} - ${agent.hostname}`,
        value: response.data.length,
        childrens: childrens,
        agent: agent
      }

      this.options.series[0].data.push(tmp)
    }

    this.initChart()

    // request
    //   .get("/api/v1/agents/", { params: { all: true }})
    //   .then((response) => {
    //     this.agents = response.data

    //     for (const agent of this.agents) {
    //       console.log(agent)
    //       const tmp = {
    //         name: `${agent.ip_address} - ${agent.hostname}`,
    //         value: 1,
    //         agent: agent
    //       }

    //       this.options.series[0].data.push(tmp)
    //     }
    //     this.initChart()
    //   })
  },

  mounted() {
  },

  methods: {
    initChart() {
      this.chart = echarts.init(document.getElementById("map"))
      this.chart.setOption(this.options)
    }
  }
})
</script>
