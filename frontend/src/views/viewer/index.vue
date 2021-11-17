<template>
  <div class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#F58320"
      style="padding-right: 10px"
    >
      <el-menu-item index="1">
        <i class="el-icon-view" />
      </el-menu-item>

      <el-menu-item index="2">
        <el-select v-model="selectedData" clearable :placeholder="$t('Measurement')" size="mini">
          <el-option
            v-for="measurement in measurements"
            :key="measurement"
            :label="measurement"
            :value="measurement"
          />
        </el-select>
      </el-menu-item>
      <el-menu-item index="3">
        <el-select v-model="selectedAgent" clearable :placeholder="$t('Agent')" size="mini" @change="fetchData()">
          <el-option
            v-for="agent in agents"
            :key="agent._id"
            :label="agent.ip_address"
            :value="agent._id"
          />
        </el-select>
      </el-menu-item>

      <el-menu-item index="3" style="float: right; padding: 0">
        <el-popover
          v-model="popoverDateOpen"
          trigger="click"
          placement="bottom-end"
          :offset="-70"
          width="725"
        >
          <div style="width: 20%; float: left">
            <span v-for="(text, key) in mappingDateRange" :key="key">
              <el-button
                type="text"
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

          <el-button slot="reference" size="mini" v-html="dateStr" />
        </el-popover>
      </el-menu-item>
    </el-menu>
    <div v-if="selectedData">
      <time-chart
        ref="graph"
        title=""
        height="300"
        :queries="queries"
        :date-range="dateRange"
        :options="chartOptions"
        @zoom="beforeZoom"
      />
      <el-table
        stipe
        size="mini"
        :data="logs"
        row-key="index"
        style="width: 100%"
        :default-sort="sort"
        highlight-current-row
        :empty-text="$t('No data')"
        header-row-class-name="thead-light"
        @sort-change="sortChange"
      >
        <el-table-column sortable :label="$t('Time')" prop="time">
          <div slot-scope="scope">
            <span v-html="renderDate(scope.row.time)" />
          </div>
        </el-table-column>
        <el-table-column :label="$t('Agent')" prop="lightowl_id">
          <div slot-scope="scope">
            <el-tag
              effect="dark"
              size="mini"
              v-html="getAgent(scope.row)"
            />
          </div>
        </el-table-column>
        <el-table-column
          v-for="(type, key) in mapping"
          :key="key"
          :label="key"
          :props="key"
        >
          <div slot-scope="scope">
            <span v-if="selectedField == key">
              <el-tag type="danger" effect="dark" size="mini" v-html="scope.row[key]" />
            </span>
            <span v-else v-html="scope.row[key]" />
          </div>
        </el-table-column>
      </el-table>
      <div
        slot="footer"
        class="
          col-12
          d-flex
          justify-content-center justify-content-sm-between
          flex-wrap
          pl-1
          pb-1
        "
      >
        <p class="card-category m-0 pagination-info" style="float: left">
          {{ $t("Showing") }} {{ pagination.from + 1 }} {{ $t("to") }}
          {{ pagination.to }} {{ $t("of") }} {{ pagination.total }}
          {{ $t("entries") }}

          <span v-if="selectedRows.length">
            &nbsp; &nbsp; {{ selectedRows.length }} {{ $t("rows selected") }}
          </span>
        </p>
        <base-pagination
          style="float: right"
          class="pagination-no-border mt-3 pr-1 mt-1"
          :current="pagination.currentPage"
          :per-page="pagination.perPage"
          :total="pagination.total"
          @change="paginationChanged($event)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import renderMixin from "@/mixins/renderMixin"
import TimeChart from "@/components/charts/TimeChart"
import BasePagination from "@/components/Table/BasePagination.vue"
import { defineComponent } from "@vue/composition-api"
import DateRangePicker from "vue2-daterange-picker"
import "vue2-daterange-picker/dist/vue2-daterange-picker.css"

export default defineComponent({
  components: { DateRangePicker, BasePagination, TimeChart },
  mixins: [renderMixin, statsMixin],

  data: () => ({
    chartOptions: {
      legend: {
        display: false,
        position: "bottom"
      }
    },
    logs: [],
    popoverDateOpen: false,
    selectedDate: "today",
    mapping: {},
    queries: [],
    expandRowKeys: [],
    measurements: [],
    selectedField: null,
    selectedRows: [],
    agents: [],
    selectedData: "",
    selectedAgent: null,
    dateRange: {
      startDate: new moment().subtract(7, "days").format(),
      endDate: new moment().format()
    },
    sort: {
      prop: "time",
      order: "descending"
    },
    pagination: {
      perPage: 25,
      from: 0,
      to: 25,
      page: 1,
      total: 0,
      perPageOptions: [
        { label: 10, value: 10 },
        { label: 20, value: 20 },
        { label: 30, value: 30 },
        { label: 50, value: 50 },
        { label: 100, value: 100 }
      ]
    }
  }),

  watch: {
    selectedData() {
      this.pagination.page = 1
      this.fetchMapping()
    }
  },

  computed: {
    collector() {
      return {
        measurement: this.selectedData
      }
    }
  },

  async beforeMount() {
    this.alert_id = this.$route.params.alert_id
    if (this.alert_id) {
      const response = await request.get(`/api/v1/alerts/${this.alert_id}`)
      this.selectedField = response.data.rule.field
      this.fetchMeasurements(response.data.rule.measurement)
      this.fetchAgents(response.data.agent._id)
    } else {
      this.fetchMeasurements()
      this.fetchAgents()
    }
  },

  methods: {
    getAgent(row) {
      if (row.lightowl_id === "lightowl") return "Lightowl"
      return this.agents[row.lightowl_id].ip_address
    },

    sortChange({ prop, order }) {
      this.sort = {
        prop: prop,
        order: order
      }
      this.pagination.page = 1
      this.fetchData()
    },

    selectDate(key, text) {
      this.selectedDate = key
      this.popoverDateOpen = false
      this.pagination.page = 1
      this.fetchData()
    },

    beforeZoom(start, end) {
      this.selectedDate = { startDate: moment(start), endDate: moment(end) }
    },
    updateValues() {
      this.selectedDate = "custom"
    },

    loadUI() {
      this.logs = []
      this.fetchMapping()
    },

    fetchMeasurements(init) {
      request.get("/api/v1/metrics/measurements").then((response) => {
        this.measurements = response.data
        this.selectedData = this.measurements[0]
        if (init) this.selectedData = init
      })
    },

    fetchAgents(init) {
      request
        .get("/api/v1/agents/", { params: { all: true }})
        .then((response) => {
          const agents = {}
          for (const tmp of response.data) {
            agents[tmp._id] = tmp
          }

          this.agents = agents
          this.selectedAgent = init
        })
    },

    fetchMapping() {
      request
        .get("/api/v1/inputs/mapping/", {
          params: { measurement: this.selectedData }
        })
        .then((response) => {
          this.mapping = response.data
          this.fetchData()
        })
    },

    paginationChanged(page) {
      this.pagination.page = page
      this.fetchData()
    },

    fetchData() {
      let startDate = moment.utc(this.dateRange.startDate)
      let endDate = moment.utc(this.dateRange.endDate)
      if (this.selectedDate !== "custom") {
        const dates = this.getRelativeDate(this.selectedDate)
        startDate = dates.startDate
        endDate = dates.endDate
      }

      const interval = this.calculateInterval({
        startDate: startDate,
        endDate: endDate
      })

      const params_graph = {
        date_start: startDate.format("YYYY-MM-DD HH:mm:ss"),
        date_end: endDate.format("YYYY-MM-DD HH:mm:ss"),
        measurement: this.selectedData,
        agent: this.selectedAgent,
        group_by: "host",
        interval: this.interval
      }

      const params = {
        date_start: startDate.format("YYYY-MM-DD HH:mm:ss"),
        date_end: endDate.format("YYYY-MM-DD HH:mm:ss"),
        measurement: this.selectedData,
        sort: `${this.sort.prop}|${this.sort.order}`,
        page: this.pagination.page,
        per_page: this.pagination.perPage,
        agent: this.selectedAgent,
        interval: interval
      }

      request
        .get("/api/v1/metrics/chart", { params: params_graph })
        .then((response) => {
          const data = []
          for (const serie of response.data.series) {
            const values = this.formatValues(serie.values)
            data.push({ name: serie.tags.host, data: values })
          }

          this.$refs.graph.updateSeries(data)
        })

      request
        .get("/api/v1/metrics/logs", { params: params })
        .then((response) => {
          this.logs = response.data.data
          this.pagination.total = response.data.count
          this.pagination.from = params.page * params.per_page - params.per_page
          this.pagination.to = params.per_page * params.page
        })
    }
  }
})
</script>
