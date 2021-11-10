<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="12">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Banned") }}
          </div>

          <h2 class="text-center" v-html="banned" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Failed") }}
          </div>

          <h2 class="text-center" v-html="failed" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="10">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Failed over time") }}
          </div>
          <time-chart ref="graph_fail2ban_failed" :options="{}" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Banned over time") }}
          </div>
          <time-chart ref="graph_fail2ban_banned" :options="{}" :date-range="dateRange" />
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

  data: () => ({
    is_loading_max: true,
    is_loading_time: true,
    is_loading_stats: true,

    failed: 0,
    banned: 0,

    last: {
      fail2ban: {
        fields: ["failed", "banned"]
      }
    },

    max: {},

    time: [{
      measurement: "fail2ban",
      fields: ["failed"]
    }, {
      measurement: "fail2ban",
      fields: ["banned"]
    }]
  }),

  methods: {
    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false
        this.failed = data["fail2ban.failed"]
        this.banned = data["fail2ban.banned"]
      } else if (graph_type === "max") {
        this.is_loading_max = false
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
