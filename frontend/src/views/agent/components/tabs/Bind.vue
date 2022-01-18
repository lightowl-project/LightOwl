<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('Server incoming requests by DNS Opcode') }}
          </div>

          <time-chart ref="graph_bind_counter_QUERY" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('Incoming queries by Query type') }}
          </div>

          <time-chart ref="graph_bind_counter_A" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('Server statistics') }}
          </div>

          <time-chart ref="graph_bind_counter_Requestv4" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
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
    agent_id: String,
    required: true
  },

  data: (vm) => ({
    is_loading_max: true,
    is_loading_time: true,
    is_loading_stats: true,

    last: {
    },

    max: {
    },

    time: [{
      measurement: "bind_counter",
      fields: ["A", "AAAA", "PTR", "MX", "SRV", "TYPE65"]
    }, {
      measurement: "bind_counter",
      fields: ["QUERY", "IQUERY", "STATUS", "NOTIFY", "UPDATE"]
    }, {
      measurement: "bind_counter",
      fields: ["Requestv4", "ReqEdns0", "Response", "RespEDNS0", "QrySuccess", "QryAuthAns", "QryNoauthAns", "QryNxrrset", "QryNXDOMAIN", "QryRecursion", "QryDuplicate", "QryUDP"]
    }]
  }),

  methods: {
    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false
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
