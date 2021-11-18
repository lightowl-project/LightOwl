<template>
  <div style="padding: 0 5px;">
    <el-tabs v-model="selectedTab">
      <el-tab-pane v-for="input in inputs" :key="input._id" :name="input._id">
        <span slot="label">
          {{ input.plugin.title }}
        </span>
        <component :is="dashboards[input.plugin_name.toLowerCase()]" :ref="input._id" :agent_id="agent_id" :date-range="dateRange" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import renderMixin from "@/mixins/renderMixin"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  components: {},
  mixins: [renderMixin, statsMixin],
  props: {
    agent_id: {
      type: String,
      required: true
    },
    dateRange: {
      type: Object,
      required: true
    },
    selectedDate: {
      type: String,
      required: true
    },
    interval: {
      type: String,
      required: true
    }
  },

  data: () => ({
    agent: null,
    dash_interval: null,
    selectedTab: null,
    system_plugin_id: null,
    inputs: [],
    dashboards: {
      "redis": () => import("./tabs/Redis.vue"),
      "apache": () => import("./tabs/Apache.vue"),
      "docker": () => import("./tabs/Docker.vue"),
      "system": () => import("./tabs/System.vue"),
      "fail2ban": () => import("./tabs/Fail2ban.vue"),
      "haproxy": () => import("./tabs/Haproxy.vue"),
      "influxdb": () => import("./tabs/InfluxDB.vue"),
      "rabbitmq": () => import("./tabs/RabbitMQ.vue"),
      "mongodb": () => import("./tabs/MongoDB.vue"),
      "postgresql": () => import("./tabs/PostgreSQL.vue"),
      "elasticsearch": () => import("./tabs/Elasticsearch.vue")
    }
  }),

  watch: {
    selectedTab(val) {
      let component = this.$refs[val]
      if (!component) return

      component = component[0]
      component.resize()
      component.load()
      this.fetchData()
    },

    dateRange() {
      this.fetchData()
    },

    interval() {
      this.fetchData()
    },

    selectedDate() {
      this.fetchData()
    }
  },

  beforeMount() {
    this.getAgent()
  },

  beforeDestroy() {
    if (this.dash_interval) clearInterval(this.dash_interval)
  },

  methods: {
    resize() {
      for (const ref of Object.values(this.$refs)) {
        ref[0].resize()
      }
    },

    async getAgent() {
      let response = await request.get(`/api/v1/agents/${this.agent_id}`)
      this.agent = response.data

      response = await request.get(`/api/v1/agents/inputs/${this.agent_id}`)
      const inputs = response.data
      for (const input of inputs) {
        if (input.plugin_name === "system") {
          this.system_plugin_id = input._id
        }

        this.inputs.push(input)
      }

      this.selectedTab = this.inputs[0]._id
      this.$forceUpdate()

      this.$nextTick(() => {
        setTimeout(() => {
          this.fetchData()
        }, 1000)

        this.dash_interval = setInterval(() => {
          this.fetchData()
        }, 10000)
      })
    },

    async fetchData() {
      for (const input of this.inputs) {
        if (input._id !== this.selectedTab) continue

        let component = this.$refs[input._id]
        if (!component) continue

        component = component[0]
        if (!component) return

        const params = {
          last: [],
          max: [],
          time: []
        }

        let startDate = moment.utc(this.dateRange.startDate)
        let endDate = moment.utc(this.dateRange.endDate)
        if (this.selectedDate !== "custom") {
          const dates = this.getRelativeDate(this.selectedDate)
          startDate = dates.startDate
          endDate = dates.endDate
        }

        let interval = this.interval
        if (interval === "auto") {
          interval = this.calculateInterval({
            startDate: startDate,
            endDate: endDate
          })
        }

        for (const graph_type of ["last", "max"]) {
          const graphs = component[graph_type]
          if (!graphs) continue

          for (const [measurement, graph_param] of Object.entries(graphs)) {
            for (const field of graph_param.fields) {
              const tmp = {
                measurement: measurement,
                where: graph_param.where,
                graph_type: graph_type,
                agent_id: this.agent_id,
                agg: graph_type,
                interval: interval,
                field: field
              }

              params[graph_type].push(tmp)
            }
          }
        }

        for (const element of component.time) {
          for (const field of element.fields) {
            const agg = element.agg ? element.agg : "mean"
            const tmp = {
              date_start: startDate.format("YYYY-MM-DD HH:mm:ss"),
              date_end: endDate.format("YYYY-MM-DD HH:mm:ss"),
              measurement: element.measurement,
              group_by: element.group_by,
              agent_id: this.agent_id,
              where: element.where,
              graph_type: "time",
              interval: interval,
              agg: agg,
              field: field
            }

            params.time.push(tmp)
          }
        }

        for (const [graph_type, param] of Object.entries(params)) {
          if (!param.length) continue

          const response = await request.post("/api/v1/dashboard/query", param)
          const data = {}

          for (const [graph_name, values] of Object.entries(response.data)) {
            const keys = graph_name.split(".")
            const measurement = keys[1]

            keys.shift()
            keys.shift()
            const field = keys.join(".")

            if (graph_type === "time") {
              data[`${measurement}.${field}`] = values
            } else {
              try {
                data[`${measurement}.${field}`] = values.series[0].values[0][1]
              } catch (err) {
                data[`${measurement}.${field}`] = 0
              }
            }
          }

          component.updateData(graph_type, data)
        }
      }
    }
  }
})
</script>
