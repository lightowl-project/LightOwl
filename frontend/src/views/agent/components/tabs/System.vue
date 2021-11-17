<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Uptime") }}
          </div>

          <h2 class="text-center" v-html="uptime" />
        </el-card>
      </el-col>
      <el-col :md="2">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("CPUs") }}
          </div>

          <h2 class="text-center" v-html="nb_cpus" />
        </el-card>
      </el-col>
      <el-col :md="2">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Load") }}
          </div>

          <h2 class="text-center" v-html="load1" />
        </el-card>
      </el-col>
      <el-col :md="2">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Threads") }}
          </div>

          <h2 class="text-center" v-html="total_threads" />
        </el-card>
      </el-col>
      <el-col :md="2">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Processes") }}
          </div>

          <h2 class="text-center" v-html="total_processes" />
        </el-card>
      </el-col>
      <el-col :md="2">
        <el-card v-loading="is_loading_stats" :style="renderStyle('zombies')" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Zombies") }}
          </div>

          <h2 class="text-center" v-html="zombies_processes" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("RAM Available") }}
          </div>

          <h2 class="text-center" v-html="mem_available" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" :style="renderStyle('swap')" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("SWAP Used") }}
          </div>

          <h2 class="text-center" v-html="formatBytes(swap_used)" />
        </el-card>
      </el-col>
      <el-col :md="2">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Users") }}
          </div>

          <h2 class="text-center" v-html="current_users" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="10">
      <el-col :md="12">
        <el-col :md="8">
          <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
            <div slot="header">
              {{ $t("CPU") }}
            </div>
            <gauge-chart ref="graphCPU" height="200px" :agent_id="agent_id" graph_name="cpu" />
          </el-card>
        </el-col>
        <el-col :md="8">
          <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
            <div slot="header">
              {{ $t("Memory") }}
            </div>
            <gauge-chart ref="graphMEM" height="200px" :agent_id="agent_id" graph_name="mem" />
          </el-card>
        </el-col>
        <el-col :md="8">
          <el-card v-loading="is_loading_max" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
            <div slot="header">
              {{ $t("Disk Used") }}
            </div>
            <gauge-chart ref="graphDISK" height="200px" :agent_id="agent_id" graph_name="disk" />
          </el-card>
        </el-col>

        <el-col :md="24" :xl="12" style="margin: 10px 0">
          <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
            <div slot="header">
              {{ $t("Memory Usage") }}
            </div>
            <time-chart ref="graph_mem_used_percent" :options="optionsMemPercent" :date-range="dateRange" />
          </el-card>
        </el-col>

        <el-col :md="24" :xl="12" style="margin-top: 10px">
          <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
            <div slot="header">
              {{ $t("Processes") }}
            </div>
            <time-chart ref="graph_processes_total" :options="optionsProcessesTotal" :date-range="dateRange" />
          </el-card>
        </el-col>
      </el-col>

      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("CPU") }}
          </div>
          <time-chart ref="graph_cpu_usage_user" :options="optionsCPUUsage" :date-range="dateRange" />
        </el-card>
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always">
          <div slot="header">
            {{ $t("System load") }}
          </div>
          <time-chart ref="graph_system_load1" :options="{}" :date-range="dateRange" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import dashMixin from "@/mixins/dashMixin"
import renderMixin from "@/mixins/renderMixin"
import { defineComponent } from "@vue/composition-api"
import TimeChart from "@/components/charts/TimeChart.vue"
import GaugeChart from "@/components/charts/GaugeChart.vue"

export default defineComponent({
  components: { GaugeChart, TimeChart },
  mixins: [dashMixin, statsMixin, renderMixin],

  props: {
    agent_id: {
      type: String,
      required: true
    }
  },

  data: (vm) => ({
    is_loading_max: true,
    is_loading_time: true,
    is_loading_stats: true,
    load1: 0,
    nb_cpus: 0,
    uptime: "",
    total_threads: 0,
    total_processes: 0,
    zombies_processes: 0,
    mem_available: 0,
    swap_used: 0,
    current_users: 0,

    last: {
      cpu: {
        fields: ["usage_idle"]
      },
      mem: {
        fields: ["used_percent", "available"]
      },
      system: {
        fields: ["uptime", "n_users", "load1", "n_cpus"]
      },
      processes: {
        fields: ["total_threads", "zombies", "total"]
      },
      swap: {
        fields: ["used"]
      }
    },

    max: {
      disk: {
        fields: ["used_percent"],
        where: ""
      }
    },

    time: [{
      measurement: "system",
      fields: ["load1"]
    }, {
      measurement: "mem",
      fields: ["used_percent"]
    }, {
      measurement: "cpu",
      fields: ["usage_user", "usage_system"]
    }, {
      measurement: "processes",
      fields: ["total"],
      agg: "last"
    }],

    optionsCPUUsage: {
      yaxis: {
        labels: {
          formatter: (val) => {
            return `${val.toFixed(2)} %`
          }
        }
      }
    },

    optionsProcessesTotal: {
      yaxis: {
        labels: {
          formatter: (val) => {
            return parseInt(val)
          }
        }
      }
    },

    optionsMemPercent: {
      yaxis: {
        labels: {
          offsetX: 10,
          rotate: -30,
          formatter: (val) => {
            return `${val.toFixed(2)} %`
          }
        }
      }
    }
  }),

  async beforeMount() {
    const response = await request.get(`/api/v1/agents/${this.agent_id}`)
    const agent = response.data
    switch (agent.os) {
      case "Linux":
        this.max.disk.where = "path = '/'"
        break
    }
  },

  methods: {
    resize() {
      this.$refs.graphCPU.resize()
      this.$refs.graphMEM.resize()
      this.$refs.graphDISK.resize()
    },

    renderStyle(graph_name) {
      const style = {}

      if (graph_name === "swap") {
        if (this.swap_used > 0) {
          style["background-color"] = "#f56c6c"
          style["color"] = "#fff"
        }
      } else if (graph_name === "zombies") {
        if (this.zombies_processes > 0) {
          style["background-color"] = "#f56c6c"
          style["color"] = "#fff"
        }
      }

      return style
    },

    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false

        this.uptime = this.renderUPtime(data["system.uptime"])

        this.$refs.graphCPU.updateData(parseInt(100 - data["cpu.usage_idle"]))
        this.$refs.graphMEM.updateData(parseFloat(data["mem.used_percent"]))
        this.load1 = parseFloat(data["system.load1"])
        this.nb_cpus = parseInt(data["system.n_cpus"])
        this.total_threads = parseInt(data["processes.total_threads"])
        this.total_processes = parseInt(data["processes.total"])
        this.zombies_processes = parseInt(data["processes.zombies"])
        this.mem_available = this.formatBytes(data["mem.available"])
        this.swap_used = data["swap.used"]
        this.current_users = data["system.n_users"]
      } else if (graph_type === "max") {
        this.is_loading_max = false
        this.$refs.graphDISK.updateData(parseFloat(data["disk.used_percent"]).toFixed(2))
      } else if (graph_type === "time") {
        this.is_loading_time = false
        for (const element of this.time) {
          const series = this.formatTimeSeries(element, data)
          this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateSeries(series)
          if (element.colors) { this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateColors(element.colors) }
        }
      }

      this.resize()
    }
  }
})
</script>
