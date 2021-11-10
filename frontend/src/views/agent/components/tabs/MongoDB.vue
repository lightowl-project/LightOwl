<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="12">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Open Connections") }}
          </div>

          <h2 class="text-center" v-html="open_connections" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Virtual Memory") }}
          </div>

          <h2 class="text-center" v-html="virtual_memory" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="10">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Operations") }}
          </div>
          <time-chart ref="graph_mongodb_commands_per_sec" :options="{}" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Network") }}
          </div>
          <time-chart ref="graph_mongodb_net_in_bytes" :options="{}" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Memory") }}
          </div>
          <time-chart ref="graph_mongodb_vsize_megabytes" :options="{}" :date-range="dateRange" />
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

export default defineComponent({
  components: { TimeChart },
  mixins: [dashMixin, statsMixin],

  props: {
    agent_id: String,
    required: true
  },

  data: () => ({
    is_loading_max: true,
    is_loading_time: true,
    is_loading_stats: true,

    open_connections: 0,
    virtual_memory: 0,

    last: {
      mongodb: {
        fields: ["open_connections", "vsize_megabytes"]
      }
    },
    max: {},
    time: [{
      measurement: "mongodb",
      fields: ["commands_per_sec", "deletes_per_sec", "getmores_per_sec", "inserts_per_sec", "queries_per_sec", "updates_per_sec"]
    }, {
      measurement: "mongodb",
      fields: ["net_in_bytes", "net_out_bytes"]
    }, {
      measurement: "mongodb",
      fields: ["vsize_megabytes", "resident_megabytes"]
    }]
  }),

  methods: {
    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false
        this.open_connections = data["mongodb.open_connections"]
        this.virtual_memory = this.formatBytes(data["mongodb.vsize_megabytes"] * 1000000)
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
    }
  }
})
</script>
