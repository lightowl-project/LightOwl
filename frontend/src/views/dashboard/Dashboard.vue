<template>
  <div class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#F58320"
    >
      <el-menu-item index="1">
        {{ name }}
      </el-menu-item>
      <el-menu-item index="4" style="float: right" @click="editDashboard()">
        <i class="fa fa-edit" />
      </el-menu-item>
      <el-menu-item index="6" style="float: right; padding: 0">
        <el-popover
          v-model="popoverDateOpen"
          trigger="click"
          placement="bottom-end"
          :offset="-50"
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

      <el-menu-item index="3" style="float: right; padding: 0" />
      <el-menu-item index="2" style="float: right; padding: 0">
        <label class="mr-1">{{ $t("Interval") }}:</label>
        <el-select
          v-model="interval"
          size="mini"
          class="mr-1"
          style="width: 70px"
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
      </el-menu-item>
      <el-menu-item index="5" style="float: right; padding: 0">
        <label class="mr-1"><i class="fa fa-sync" /></label>
        <el-select
          v-model="refresh"
          style="width: 70px"
          size="mini"
          class="mr-1"
          :placeholder="$t('Refresh')"
        >
          <el-option label="1s" :value="1000" />
          <el-option label="5s" :value="5000" />
          <el-option label="10s" :value="10000" />
          <el-option label="1m" :value="60000" />
          <el-option label="5m" :value="300000" />
        </el-select>
      </el-menu-item>
    </el-menu>
    <grid-layout
      :layout.sync="widgets"
      :col-num="12"
      :row-height="30"
      :is-draggable="false"
      :is-resizable="false"
      :is-mirrored="false"
      :vertical-compact="true"
      :margin="[5, 5]"
      :use-css-transforms="true"
    >
      <grid-item
        v-for="(item, index) in widgets"
        :key="item.pk"
        :x="item.x"
        :y="item.y"
        :w="item.w"
        :h="item.h"
        :i="item.i"
      >
        <widget
          :index="index"
          :interval="interval"
          :refresh="refresh"
          :selected-date="selectedDate"
          :date-range="dateRange"
          :widget-id="item.widget_id"
          @zoom="zoom"
        />
      </grid-item>
    </grid-layout>
  </div>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import VueGridLayout from "vue-grid-layout"
import statsMixin from "@/mixins/statsMixin"
import Widget from "./components/Widget.vue"
import renderMixin from "@/mixins/renderMixin"
import DateRangePicker from "vue2-daterange-picker"
import "vue2-daterange-picker/dist/vue2-daterange-picker.css"

export default {
  name: "Dashboard",

  components: {
    GridLayout: VueGridLayout.GridLayout,
    GridItem: VueGridLayout.GridItem,
    DateRangePicker,
    Widget
  },

  mixins: [renderMixin, statsMixin],

  data: () => ({
    name: null,
    editMode: false,
    refresh: 10000,
    popoverDateOpen: false,
    widgets: [],
    components: {},
    dashboard_id: null,
    no_dashboard: false,
    interval: "auto",
    selectedDate: "7d",
    dateRange: {
      startDate: new moment().subtract(7, "days").format(),
      endDate: new moment().format()
    }
  }),

  mounted() {
    // this.fetch_inputs();
    if (!this.$route.params.id) {
      this.fetch_general_dashboard()
    } else {
      this.dashboard_id = this.$route.params.id
      this.fetch_dashboard()
    }
  },

  methods: {
    updateValues() {
      this.selectedDate = "custom"
    },

    selectDate(key, text) {
      this.selectedDate = key
      this.popoverDateOpen = false
    },

    zoom({ start, end }) {
      this.dateRange = { startDate: moment(start), endDate: moment(end) }
    },
    fetch_dashboard() {
      request.get(`/api/v1/dashboard/${this.dashboard_id}`).then((response) => {
        this.name = response.data.name
        this.widgets = response.data.widgets
      })
    },

    fetch_general_dashboard() {
      request
        .get("/api/v1/dashboard/", { params: { general: true }})
        .then((response) => {
          this.dashboard_id = response.data._id
          this.name = response.data.name
          this.widgets = response.data.widgets
        })
        .catch((err) => {
          if (err.response.status === 404) {
            this.no_dashboard = true
          }
        })
    },

    renderStyle(item) {
      return `
        background-color: ${item.color};
        color: #fff;
      `
    },

    editDashboard() {
      this.$router.push(`/edit/${this.dashboard_id}`)
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  // &-container {
  // margin: 30px;
  // }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
}
.card-panel {
  height: 108px;
  cursor: pointer;
  font-size: 12px;
  position: relative;
  overflow: hidden;
  color: #666;
  background: #fff;
  box-shadow: 4px 4px 40px rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.05);
  .card-panel-icon-wrapper {
    float: left;
    margin: 14px 0 0 14px;
    padding: 16px;
    transition: all 0.38s ease-out;
    border-radius: 6px;
  }
  .card-panel-title {
    float: left;
    padding: 0px 5px;
  }
  .card-panel-icon {
    float: left;
    font-size: 48px;
  }
  .card-panel-description {
    float: right;
    font-weight: bold;
    margin: 0px;
    padding-top: 0px;
    padding-right: 20px;
    margin-left: 0px;
    .card-panel-text {
      line-height: 18px;
      color: rgba(0, 0, 0, 0.45);
      font-size: 16px;
      margin-bottom: 12px;
    }
    .card-panel-num {
      font-size: 20px;
    }
  }
}

.el-card__header {
  padding: 5px 10px;
}
.chart-container {
  position: relative;
  width: 100%;
  height: calc(100vh - 50px);
}
</style>
