<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="2">
        <el-card v-loading="is_loading_stats" :style="renderStyle('health')" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Health") }}
          </div>

          <h2 class="text-center" v-html="renderHealth()" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" :style="renderStyle('unassigned_shards')" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Unassigned Shards") }}
          </div>

          <h2 class="text-center" v-html="unassigned_shards" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Documents") }}
          </div>

          <h2 class="text-center" v-html="docs_count" />
        </el-card>
      </el-col>
      <el-col :md="3">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Active shards") }}
          </div>

          <h2 class="text-center" v-html="active_shards" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Stored data size") }}
          </div>

          <h2 class="text-center" v-html="stored_data_size" />
        </el-card>
      </el-col>
      <el-col :md="3">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Used data") }}
          </div>

          <h2 class="text-center" v-html="renderUsedData()" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10">
      <el-col :md="14">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("JVM Heap") }}
          </div>
          <time-chart ref="graph_elasticsearch_jvm_mem_heap_max_in_bytes" height="300" :options="optionsJVM" :date-range="dateRange" />
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
    agent_id: {
      type: String,
      required: true
    }
  },

  data: (vm) => ({
    is_loading_max: true,
    is_loading_stats: true,
    is_loading_time: true,

    health: "",
    unassigned_shards: 0,
    stored_data_size: "",
    active_shards: 0,
    docs_count: 0,
    used_data: 0,

    last: {
      elasticsearch_indices: ["docs_count"],
      elasticsearch_clusterstats_indices: ["store_size_in_bytes"],
      elasticsearch_fs: ["data_0_total_in_bytes", "data_0_free_in_bytes"],
      elasticsearch_cluster_health: ["status", "unassigned_shards", "active_shards"]
    },

    max: {},

    time: [{
      measurement: "elasticsearch_jvm",
      fields: ["mem_heap_max_in_bytes", "mem_heap_used_in_bytes"]
    }],

    optionsJVM: {
      yaxis: {
        labels: {
          offsetX: 0,
          rotate: -30,
          formatter: (val) => {
            return vm.formatBytes(val)
          }
        }
      }
    }
  }),

  methods: {
    renderUsedData() {
      return `${this.used_data} %`
    },

    renderHealth() {
      const mapping = {
        green: "OK",
        yellow: "WARNING",
        red: "KO"
      }

      return mapping[this.health]
    },

    renderStyle(graph_name) {
      const style = {}

      if (graph_name === "health") {
        if (this.health === "green") {
          style["background-color"] = "#34BFA3"
          style["color"] = "#FFF"
        } else if (this.health === "yellow") {
          style["background-color"] = "#f9b55c"
          style["color"] = "#FFF"
        } else if (this.health === "red") {
          style["background-color"] = "#F4516C"
          style["color"] = "#FFF"
        }
      } else if (graph_name === "unassigned_shards") {
        if (this.unassigned_shards === 0) {
          style["background-color"] = "#34BFA3"
          style["color"] = "#FFF"
        } else {
          style["background-color"] = "#F4516C"
          style["color"] = "#FFF"
        }
      }

      return style
    },

    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false
        this.health = data["elasticsearch_cluster_health.status"]
        this.unassigned_shards = data["elasticsearch_cluster_health.unassigned_shards"]
        this.active_shards = data["elasticsearch_cluster_health.active_shards"]
        this.docs_count = data["elasticsearch_indices.docs_count"]
        this.stored_data_size = this.formatBytes(data["elasticsearch_clusterstats_indices.store_size_in_bytes"])

        this.used_data = parseFloat(((data["elasticsearch_fs.data_0_total_in_bytes"] - data["elasticsearch_fs.data_0_free_in_bytes"]) / data["elasticsearch_fs.data_0_total_in_bytes"]) * 100).toFixed(2)
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

      // this.resize()
    }
  }
})
</script>
