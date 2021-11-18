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
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Connected Clients") }}
          </div>

          <h2 class="text-center" v-html="clients" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Processed commands") }}
          </div>

          <h2 class="text-center" v-html="total_commands_processed" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Used memory") }}
          </div>

          <h2 class="text-center" v-html="used_memory" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Total connections received") }}
          </div>
          <time-chart ref="graph_redis_total_connections_received" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Total Commands Processed") }}
          </div>
          <time-chart ref="graph_redis_total_commands_processed" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Instantaneous OPS per sec") }}
          </div>
          <time-chart ref="graph_redis_instantaneous_ops_per_sec" :options="optionsFormatNumbers" :date-range="dateRange" />
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

export default defineComponent({
  components: { TimeChart },
  mixins: [dashMixin, statsMixin, renderMixin],

  props: {
    agent_id: {
      type: String,
      required: true
    }
  },

  data: (vm) => ({
    is_loading_stats: true,
    is_loading_max: true,
    is_loading_time: true,

    uptime: "",
    clients: 0,
    total_commands_processed: 0,
    used_memory: 0,

    last: {
      redis: {
        fields: ["uptime", "clients", "total_commands_processed", "used_memory"]
      }
    },
    max: {},
    time: [{
      measurement: "redis",
      fields: ["total_connections_received"]
    }, {
      measurement: "redis",
      fields: ["total_commands_processed"]
    }, {
      measurement: "redis",
      fields: ["instantaneous_ops_per_sec"]
    }]
  }),

  methods: {
    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false

        this.uptime = this.renderUPtime(data["redis.uptime"])
        this.clients = data["redis.clients"]
        this.total_commands_processed = data["redis.total_commands_processed"]
        this.used_memory = this.formatBytes(data["redis.used_memory"])
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
