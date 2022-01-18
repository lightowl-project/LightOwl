<template>
  <div class="dashboard-container">
    <el-card :body-style="{margin: 0, padding: 0}">
      <el-table ref="table" stripe :loading="is_loading" :data="agents" style="width: 100%" highlight-current-row :default-sort="defaultSort" row-key="_id" @row-click="showDetail">
        <el-table-column type="expand">
          <template slot-scope="{ row }">
            <agent :prop-agent="row._id" />
          </template>
        </el-table-column>

        <el-table-column :label="$t('Agent')" prop="ip_address" sortable>
          <div slot-scope="{ row }">
            <i :class="renderOSIcon(row.os)" />
            {{ row.ip_address }} - {{ row.hostname }}

            <span style="float: right">
              <el-tag
                v-for="tag in row.tags"
                :key="tag"
                type="primary"
                size="mini"
                effect="dark"
                v-html="tag"
              />
            </span>
          </div>
        </el-table-column>
        <el-table-column :label="$t('CPU')">
          <div slot-scope="{ row }">
            <el-progress :stroke-width="24" text-inside stroke-linecap="square" :color="customColors" :percentage="row.cpu" />
          </div>
        </el-table-column>
        <el-table-column :label="$t('RAM')">
          <div slot-scope="{ row }">
            <el-progress :stroke-width="24" text-inside stroke-linecap="square" :color="customColors" :percentage="row.mem" />
          </div>
        </el-table-column>
        <el-table-column :label="$t('Load')" width="60">
          <div slot-scope="{ row }">
            <el-tag type="info" effect="dark">{{ row.load }}</el-tag>
          </div>
        </el-table-column>
        <el-table-column :label="$t('Last seen')" prop="last_seen" width="150" sortable>
          <div slot-scope="{ row }">
            <el-tag :class="tableRowClassName(row)" effect="dark">
              {{ renderLastSeen(row.last_seen) }}
            </el-tag>
          </div>
        </el-table-column>
        <el-table-column :label="$t('Alerts')" prop="alerts" sortable>
          <div slot-scope="{ row }">
            <alert-info :alerts="row.alerts" :agent_id="row._id" />
          </div>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import moment from "moment"
import EventBus from "@/event-bus"
import request from "@/utils/request"
import Agent from "@/views/agent/Agent.vue"
import renderMixin from "@/mixins/renderMixin"
import AlertInfo from "./components/AlertInfo.vue"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  components: { Agent, AlertInfo },
  mixins: [renderMixin],

  data: () => ({
    is_loading: false,
    interval: false,
    tableData: [],
    defaultSort: {
      prop: "alerts",
      order: "descending"
    },
    agents: [],
    last_stats: {},
    customColors: [
      { color: "#5cb87a", percentage: 50 },
      { color: "#e6a23c", percentage: 80 },
      { color: "#f56c6c", percentage: 90 },
      { color: "#f56c6c", percentage: 100 }
    ]
  }),

  beforeDestroy() {
    clearInterval(this.interval)
  },

  mounted() {
    EventBus.$on("new_agent", () => {
      this.getAgents()
    })

    EventBus.$on("measurements", (measurements) => {
      for (const body of measurements) {
        const measurement = body.measurement
        const agent_id = body.agent_id

        if (measurement === "cpu") {
          const cpu = 100 - parseInt(body.tags.usage_idle)
          if (cpu) {
            this.applyStats(agent_id, "cpu", cpu)
          }
        } else if (measurement === "mem") {
          const mem = parseInt(body.tags.used_percent)
          if (mem) {
            this.applyStats(agent_id, "mem", mem)
          }
        } else if (measurement === "system") {
          const load = parseFloat(body.tags.load1)
          if (load) {
            this.applyStats(agent_id, "load", load.toFixed(2))
          }
        }
      }
    })

    EventBus.$on("reload", () => {
      this.getAgents()
    })

    this.getAgents()

    this.interval = setInterval(() => {
      this.getAgents()
    }, 10000)
  },

  methods: {
    is_down(last_seen) {
      const date = moment.utc(last_seen)
      return moment.utc().diff(date, "minutes") > 5
    },

    tableRowClassName(row) {
      const date = moment.utc(row.last_seen)
      const diff = moment.utc().diff(date, "minutes")

      if (diff > 10) {
        return "danger"
      } else if (diff > 2) {
        return "warning"
      }

      return "green"
    },

    renderLastSeen(date) {
      const last_seen = moment.utc(date)
      let diff = moment.utc().diff(last_seen, "minutes")
      if (diff < 60) return `${diff} minutes ago`

      diff = moment.utc().diff(last_seen, "hours")
      if (diff < 24) return `${diff} hours ago`

      diff = moment.utc().diff(last_seen, "days")
      return `${diff} days ago`
    },

    showDetail(row, column) {
      if (column.property === "alerts") {
        return
      }

      this.$refs.table.toggleRowExpansion(row)
    },

    fetchStats() {
      const data_to_fetch = {
        "cpu": "usage_idle",
        "mem": "used_percent",
        "system": "load1"
      }

      for (const agent of this.agents) {
        const params = []

        for (const [k, v] of Object.entries(data_to_fetch)) {
          params.push({
            agent_id: agent._id,
            measurement: k,
            field: v,
            agg: "last",
            interval: "1m",
            graph_type: "last"
          })
        }

        request.post("/api/v1/dashboard/query", params).then((response) => {
          try {
            const cpu = 100 - parseInt(response.data[`${agent._id}.cpu.usage_idle`].series[0].values[0][1])
            this.applyStats(agent._id, "cpu", cpu)
          } catch (err) {}

          try {
            const mem = parseInt(response.data[`${agent._id}.mem.used_percent`].series[0].values[0][1])
            this.applyStats(agent._id, "mem", mem)
          } catch (err) {}

          try {
            const load = parseInt(response.data[`${agent._id}.system.load1`].series[0].values[0][1])
            this.applyStats(agent._id, "load", load)
          } catch (err) {}
        })
      }
    },

    getAgents() {
      request.get("/api/v1/dashboard/home").then((response) => {
        const agents = []
        for (const agent of response.data) {
          const agent_id = agent._id

          if (!this.last_stats[agent_id]) { this.last_stats[agent_id] = { cpu: 0, mem: 0, load: 0 } }

          agents.push({
            _id: agent_id,
            ip_address: agent.ip_address,
            hostname: agent.hostname,
            last_seen: agent.last_seen,
            alerts: agent.alerts,
            os: agent.os,
            tags: agent.tags,
            cpu: this.last_stats[agent_id].cpu,
            mem: this.last_stats[agent_id].mem,
            load: this.last_stats[agent_id].load
          })
        }

        this.agents = agents
      })
    },

    applyStats(agent_id, data_type, value) {
      for (const i in this.agents) {
        const agent = this.agents[i]
        if (agent._id === agent_id) {
          this.agents[i][data_type] = value
          this.last_stats[agent_id][data_type] = value
          break
        }
      }
    }
  }
})
</script>

<style>
.el-table .danger-row {
  background-color: #F56C6C;
  color: #fff;
}
.el-table .warning-row {
  background-color: #f18705;
  color: #fff;
}
</style>
