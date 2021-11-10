<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Number of containers") }}
          </div>

          <h2 class="text-center" v-html="nb_container" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="12">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("CPU") }}
          </div>
          <time-chart ref="graph_docker_container_cpu_usage_percent" :options="optionsCPUUsage" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Memory") }}
          </div>
          <time-chart ref="graph_docker_container_mem_usage" :options="optionsMemUsage" :date-range="dateRange" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="24">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('Network') }}
          </div>

          <time-chart ref="graph_docker_container_net_rx_bytes" :options="optionsNetUsage" :date-range="dateRange" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import statsMixin from "@/mixins/statsMixin"
import dashMixin from "@/mixins/dashMixin"
import { defineComponent } from "@vue/composition-api"
import TimeChart from "@/components/charts/TimeChart.vue"
import GaugeChart from "@/components/charts/GaugeChart.vue"

export default defineComponent({
  components: { GaugeChart, TimeChart },
  mixins: [dashMixin, statsMixin],

  props: {
    agent_id: String,
    required: true
  },

  data: (vm) => ({
    is_loading_max: true,
    is_loading_time: true,
    is_loading_stats: true,

    nb_container: 0,

    last: {
      docker: {
        fields: ["n_containers"]
      }
    },

    max: {},

    time: [{
      measurement: "docker_container_cpu",
      fields: ["usage_percent"],
      group_by: "container_name"
    }, {
      measurement: "docker_container_mem",
      fields: ["usage"],
      group_by: "container_name"
    }, {
      measurement: "docker_container_net",
      fields: ["rx_bytes"],
      group_by: "container_name",
      convert: {
        operator: "div",
        value: 100000
      }
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

    optionsMemUsage: {
      yaxis: {
        labels: {
          offsetX: 10,
          rotate: -30,
          formatter: (val) => {
            return vm.formatBytes(val)
          }
        }
      }
    },

    optionsNetUsage: {
      yaxis: {
        labels: {
          formatter: (val) => {
            return vm.formatBytes(val)
          }
        }
      }
    }
  }),

  methods: {
    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false
        this.nb_container = data["docker.n_containers"]
      } else if (graph_type === "max") {
        this.is_loading_max = false
      } else if (graph_type === "time") {
        this.is_loading_time = false
        for (const element of this.time) {
          const series = this.formatTimeSeries(element, data, element.convert)
          this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateSeries(series)
          if (element.colors) { this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateColors(element.colors) }
        }
      }

      this.resize()
    }
  }
})
</script>
