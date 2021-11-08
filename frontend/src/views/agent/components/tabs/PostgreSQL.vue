<template>
  <el-row :gutter="10">
    <el-col :md="24" :xl="24" style="margin: 10px 0">
      <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
        <div slot="header">
          {{ $t("Stats") }}
        </div>
        <time-chart ref="graph_postgresql_tup_fetched" height="600" :options="{}" :date-range="dateRange" />
      </el-card>
    </el-col>
  </el-row>
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

    last: {},

    max: {},

    time: [{
      measurement: "postgresql",
      fields: ["tup_fetched", "tup_returned", "tup_inserted", "tup_updated", "tup_deleted"]
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
