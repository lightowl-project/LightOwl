<template>
  <el-card :style="{ width: '100%', height: '100%', overflow: 'auto' }">
    <div slot="header" class="clearfix">
      <i class="fa fa-edit" /> {{ $t("Create a widget") }}
      <el-button
        type="text"
        class="text-black"
        style="float: right; padding: 0"
        @click="$emit('close')"
      >
        <i class="fa fa-times fa-2x" />
      </el-button>
      <el-button
        size="mini"
        type="primary"
        style="float: right; margin-right: 10px"
        plain
        @click="saveWidget()"
      >
        <i class="fa fa-save mr-1" /> {{ $t("Save") }}
      </el-button>
    </div>

    <el-form ref="form" :model="form" label-position="top" :inline="true">
      <el-form-item>
        <el-select
          v-model="form.agent"
          size="small"
          style="width: 300px"
          :placeholder="$t('Agent')"
        >
          <el-option
            v-for="agent in agents"
            :key="agent._id"
            :label="agent.ip_address"
            :value="agent._id"
          />
        </el-select>
      </el-form-item>
      <el-form-item v-if="measurements.length">
        <el-select
          v-model="form.measurement"
          size="small"
          style="width: 300px"
          :placeholder="$t('Measurement')"
        >
          <el-option
            v-for="measurement in measurements"
            :key="measurement"
            :label="measurement"
            :value="measurement"
          />
        </el-select>
      </el-form-item>
      <el-form-item v-if="Object.keys(mapping).length">
        <el-select
          v-model="form.field"
          size="small"
          style="width: 300px"
          :placeholder="$t('Measurement')"
        >
          <el-option
            v-for="(type, field) in mapping"
            :key="field"
            :label="field"
            :value="field"
          />
        </el-select>
      </el-form-item>

      <el-form-item v-if="form.field">
        <el-popover placement="right" width="400" trigger="click">
          <el-form-item :label="$t('Color')">
            <el-color-picker
              v-model="options.color"
              show-alpha
              size="small"
              :predefine="predefineColors"
              @change="updateOptions()"
            />
          </el-form-item>
          <el-form-item :label="$t('Line Stroke')">
            <el-radio-group v-model="options.curve" @change="updateOptions()">
              <el-radio label="smooth">
                {{ $t("Smooth") }}
              </el-radio>
              <el-radio label="straight">
                {{ $t("Straight") }}
              </el-radio>
              <el-radio label="stepline">
                {{ $t("Stepline") }}
              </el-radio>
            </el-radio-group>
          </el-form-item>
          <el-button slot="reference" size="small">{{
            $t("Options")
          }}</el-button>
        </el-popover>
      </el-form-item>

      <div style="float: right">
        <el-popover
          v-model="popoverDateOpen"
          trigger="click"
          placement="bottom-end"
          :offset="-50"
          width="725"
          style="margin-right: 10px"
        >
          <div style="width: 20%; float: left">
            <span v-for="(text, key) in mappingDateRange" :key="key">
              <el-button
                type="text"
                size="medium"
                style="color: #000; width: 100%"
                @click="selectDate(key, text)"
              >
                {{ text }}
              </el-button>
              <el-divider class="m-0" />
            </span>
          </div>
          <div style="width: 75%; float: right">
            <date-range-picker
              ref="picker"
              v-model="dateRange"
              :locale-data="{ firstDay: 1, format: 'dd-mm-yyyy HH:mm:ss' }"
              :max-date="maxDate"
              :single-date-picker="false"
              :time-picker="true"
              :time-picker24hour="true"
              :show-week-numbers="true"
              :show-dropdowns="true"
              opens="inline"
              :ranges="false"
              :auto-apply="true"
              @update="updateValues"
            />
          </div>
          <el-button slot="reference" size="small" v-html="dateStr" />
        </el-popover>

        <el-form-item>
          <el-select
            v-model="interval"
            size="small"
            class="mr-1"
            :placeholder="$t('Interval')"
          >
            <el-option label="auto" value="auto" />
            <el-option label="1m" value="1m" />
            <el-option label="10m" value="10m" />
            <el-option label="30m" value="30m" />
            <el-option label="1h" value="1h" />
            <el-option label="6h" value="6h" />
            <el-option label="12h" value="12h" />
            <el-option label="1d" value="1d" />
            <el-option label="7d" value="7d" />
            <el-option label="14d" value="14d" />
            <el-option label="30d" value="30d" />
          </el-select>
        </el-form-item>
      </div>
    </el-form>

    <el-row v-if="form.field">
      <time-chart ref="chart" :options="options" @zoom="zoom" />
    </el-row>
  </el-card>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import DateRangePicker from "vue2-daterange-picker"
import { defineComponent } from "@vue/composition-api"
import TimeChart from "@/components/charts/TimeChart.vue"
import "vue2-daterange-picker/dist/vue2-daterange-picker.css"

export default defineComponent({
  components: { DateRangePicker, TimeChart },
  mixins: [statsMixin],
  props: {
    widgetId: {
      type: String,
      default: ""
    }
  },
  data: () => ({
    agents: [],
    measurements: [],
    mapping: {},
    form: {},
    selectedDate: "10m",
    popoverDateOpen: false,
    interval: "auto",
    dateRange: {
      startDate: new moment().subtract(10, "minutes").format(),
      endDate: new moment().format()
    },
    options: {
      color: "#F49B51",
      legend: {
        display: true,
        position: "bottom"
      },
      curve: "smooth"
    }
  }),

  watch: {
    "form.agent"(agent_id) {
      this.getMeasurements()
    },

    "form.measurement"() {
      this.getMapping()
    },

    "form.field"() {
      this.fetchData()
    }
  },

  mounted() {
    this.getAgents()
  },

  methods: {
    getAgents() {
      request
        .get("/api/v1/agents/", { params: { all: true }})
        .then((response) => {
          this.agents = response.data

          if (this.widgetId) {
            request
              .get(`/api/v1/dashboard/widget/${this.widgetId}`)
              .then((response) => {
                this.form.agent = response.data.agent
                this.getMeasurements(response.data)
              })
          }
        })
    },

    getMeasurements(initial) {
      request
        .get(`/api/v1/inputs/measurements/${this.form.agent}`)
        .then((response) => {
          this.measurements = response.data
          if (initial) {
            this.form.measurement = initial.measurement
            this.getMapping(initial)
          }
        })
    },

    getMapping(initial) {
      request
        .get("/api/v1/inputs/mapping/", {
          params: { measurement: this.form.measurement }
        })
        .then((response) => {
          this.mapping = response.data
          if (initial) {
            this.form.field = initial.field
            this.fetchData()
            this.$forceUpdate()
          }
        })
    },

    updateOptions() {
      this.$refs.chart.updateOptions()
    },

    fetchData() {
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

      const data = {
        agent_id: this.form.agent,
        measurement: this.form.measurement,
        field: this.form.field,
        date_start: startDate.format("YYYY-MM-DD HH:mm:ss"),
        date_end: endDate.format("YYYY-MM-DD HH:mm:ss"),
        graph_type: "time",
        interval: interval
      }

      request.post("/api/v1/dashboard/query", data).then((response) => {
        this.$refs.chart.updateSeries([
          {
            name: "data",
            data: this.formatDatasets("time", response.data)
          }
        ])
      })
    },

    saveWidget() {
      const params = {
        graph_type: "time",
        agent: this.form.agent,
        measurement: this.form.measurement,
        field: this.form.field,
        interval: this.interval,
        options: this.options
      }

      request.post("/api/v1/dashboard/widget", params).then((response) => {
        const widgetId = response.data._id
        this.$message({
          type: "success",
          message: this.$t("Widget successfully created"),
          showClose: true
        })

        this.$emit("save", widgetId)
      })
    }
  }
})
</script>
