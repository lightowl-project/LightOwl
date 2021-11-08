<template>
  <el-card :style="{ width: '100%', height: '100%', overflow: 'auto' }">
    <div slot="header" class="clearfix">
      <i class="fa fa-edit" /> {{ $t("Create a widget") }}
      <el-button
        type="text"
        class="text-black"
        style="float: right; padding: 0"
        @click="close()"
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
      <el-row :gutter="20">
        <el-col :md="16">
          <el-row class="mb-1" style="text-align: right">
            <span v-if="['time'].indexOf(form.graph_type) > -1">
              <label class="mr-1">{{ $t("Interval") }}:</label>
              <el-select
                v-model="form.interval"
                class="mr-1"
                size="mini"
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
            </span>
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
            <el-button
              size="mini"
              style="margin-left: 10px"
              type="primary"
              plain
              @click="fetchData()"
            >
              <i class="fa fa-sync-alt" />
            </el-button>
          </el-row>
          <el-row class="mb-1">
            <el-col>
              <div style="height: 400px; padding: 10px">
                <!-- <el-skeleton v-if="is_loading" animated style="width: 100%x">
                  <template slot="template">
                    <el-skeleton-item
                      variant="image"
                      style="width: 100%; height: 400px"
                    />
                  </template>
                </el-skeleton> -->
                <graph
                  :is="mapping_chart[form.graph_type]"
                  ref="graph"
                  :labels="labels"
                  :title="form.name"
                  :options="form.options"
                  :queries="form.queries"
                  @zoom="zoom"
                />
              </div>
            </el-col>
          </el-row>
          <el-row class="mt-1">
            <el-card shadow="always" :body-style="{ padding: '5px 10px' }">
              <div slot="header" class="clearfix">
                <span><i class="fa fa-search mr-1" />{{ $t("Queries") }}</span>
                <el-button
                  v-if="
                    !(
                      ['text'].indexOf(form.graph_type) > -1 &&
                      form.queries.length !== 0
                    )
                  "
                  plain
                  style="float: right"
                  size="mini"
                  type="primary"
                  @click="addQuery()"
                >
                  <i class="fa fa-plus" /> {{ $t("Add query") }}
                </el-button>
              </div>
              <table style="width: 100%; text-align: center" class="table">
                <thead>
                  <tr>
                    <th>{{ $t("Enabled") }}</th>
                    <th>{{ $t("Agg") }}</th>
                    <th>{{ $t("Field") }}</th>
                    <th>{{ $t("Filter") }}</th>
                    <th>{{ $t("Color") }}</th>
                    <th>{{ $t("Name") }}</th>
                    <th>{{ $t("Actions") }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(query, index) in form.queries" :key="index">
                    <td>
                      <el-switch
                        v-model="form.queries[index].enabled"
                        @change="fetchData()"
                      />
                    </td>
                    <td>
                      <el-select
                        v-model="form.queries[index].agg"
                        style="width: 100px"
                        size="mini"
                        @change="fetchData()"
                      >
                        <el-option value="mean" :label="$t('Mean')" />
                        <el-option value="sum" :label="$t('Sum')" />
                        <el-option value="last" :label="$t('Last')" />
                        <el-option value="first" :label="$t('First')" />
                      </el-select>
                    </td>
                    <td>
                      <el-cascader
                        v-model="form.queries[index].selected_data"
                        :props="cascaderSelectField"
                        style="width: 100%"
                        size="mini"
                        clearable
                        :filterable="true"
                        @change="fetchData()"
                      >
                        <template slot-scope="{ node, data }">
                          <span v-html="renderCascaderOption(node, data)" />
                        </template>
                      </el-cascader>
                    </td>
                    <td>
                      <el-popover placement="bottom" width="600">
                        <table
                          v-if="form.queries[index].selected_data"
                          class="filter-table"
                          style="
                            width: 100%;
                            padding: 10px 5px;
                            text-align: center;
                          "
                        >
                          <thead>
                            <tr>
                              <th>{{ $t("Field") }}</th>
                              <th>{{ $t("Operator") }}</th>
                              <th>{{ $t("Pattern") }}</th>
                              <th>
                                <el-button
                                  type="primary"
                                  size="mini"
                                  plain
                                  @click="addWhere(index)"
                                >
                                  <i class="fa fa-plus" />
                                </el-button>
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              v-for="(where, index_where) in query.where"
                              :key="index_where"
                            >
                              <td>
                                <el-select
                                  v-model="
                                    form.queries[index].where[index_where].field
                                  "
                                  size="mini"
                                  @change="
                                    fetchAvailableValues(index, index_where)
                                  "
                                >
                                  <el-option
                                    v-for="tag in where.availableTags"
                                    :key="tag"
                                    :label="tag"
                                    :value="tag"
                                  />
                                  <el-option
                                    :label="$t('Agent')"
                                    value="lightowl_id"
                                  />
                                </el-select>
                              </td>
                              <td>
                                <el-select
                                  v-model="
                                    form.queries[index].where[index_where]
                                      .operator
                                  "
                                  size="mini"
                                  :placeholder="$t('Operator')"
                                >
                                  <el-option :label="$t('Equal')" value="eq" />
                                  <el-option
                                    :label="$t('Lower than')"
                                    value="lt"
                                  />
                                  <el-option
                                    :label="$t('Lower than or equal to')"
                                    value="lte"
                                  />
                                  <el-option
                                    :label="$t('Greater than')"
                                    value="gt"
                                  />
                                  <el-option
                                    :label="$t('Greater than or equal to')"
                                    value="gte"
                                  />
                                </el-select>
                              </td>
                              <td>
                                <el-select
                                  v-if="where.field"
                                  v-model="
                                    form.queries[index].where[index_where]
                                      .pattern
                                  "
                                  size="mini"
                                  @change="fetchData()"
                                >
                                  <el-option
                                    v-for="value in where.availableValues"
                                    :key="value[0]"
                                    :label="value[1]"
                                    :value="value[0]"
                                  />
                                </el-select>
                              </td>
                              <td>
                                <el-button
                                  size="mini"
                                  type="danger"
                                  @click="
                                    form.queries[index].where.splice(
                                      index_where,
                                      1
                                    );
                                    fetchData();
                                  "
                                >
                                  <i class="fa fa-trash" />
                                </el-button>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                        <el-badge
                          slot="reference"
                          :value="form.queries[index].where.length"
                          class="item"
                          type="primary"
                        >
                          <el-button size="mini">
                            <i class="fa fa-filter" />
                          </el-button>
                        </el-badge>
                      </el-popover>
                    </td>
                    <td>
                      <el-color-picker
                        v-if="['text'].indexOf(form.graph_type) === -1"
                        v-model="form.queries[index].color"
                        show-alpha
                        size="small"
                        :predefine="predefineColors"
                        @change="updateOptions()"
                      />
                    </td>
                    <td>
                      <el-input
                        v-if="['text'].indexOf(form.graph_type) === -1"
                        v-model="form.queries[index].name"
                        size="mini"
                        @blur="fetchData()"
                      />
                    </td>
                    <td style="text-align: right">
                      <el-button
                        type="danger"
                        size="mini"
                        plain
                        @click="deleteQuery(index)"
                      >
                        <i class="fa fa-trash" />
                      </el-button>
                    </td>
                  </tr>
                </tbody>
                <tbody />
              </table>
            </el-card>
          </el-row>
        </el-col>

        <el-col :md="8">
          <el-card shadow="always" :body-style="{ padding: '5px 10px' }">
            <el-row>
              <el-form-item
                :label="$t('Title')"
                size="mini"
                class="mb-0"
                style="width: 100%"
              >
                <el-input v-model="form.name" @blur="updateOptions()" />
              </el-form-item>
            </el-row>
            <el-row>
              <el-form-item :label="$t('Graph')">
                <el-radio-group v-model="form.graph_type">
                  <el-radio-button label="time">
                    <i class="fas fa-chart-area" /> <br>
                    <small>{{ $t("Time") }}</small>
                  </el-radio-button>
                  <el-radio-button label="pie">
                    <i class="fas fa-chart-pie" /> <br>
                    <small>{{ $t("Pie") }}</small>
                  </el-radio-button>
                  <el-radio-button label="gauge">
                    <i class="fas fa-tachometer-alt" /> <br>
                    <small>{{ $t("Gauge") }}</small>
                  </el-radio-button>
                  <el-radio-button label="text">
                    <i class="fas fa-font" /> <br>
                    <small>{{ $t("Text") }}</small>
                  </el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-row>
            <el-row>
              <el-collapse v-model="activesTabs">
                <el-collapse-item
                  v-if="form.graph_type === 'time'"
                  :title="$t('Time Chart')"
                  name="time"
                >
                  <table style="width: 100%">
                    <tbody>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Chart type") }}</b>
                        </td>
                        <td>
                          <el-radio-group
                            v-model="form.options.timechart.type"
                            @change="
                              updateOptions();
                              fetchData();
                            "
                          >
                            <el-radio label="area">{{ $t("Area") }}</el-radio>
                            <el-radio label="line">{{ $t("Line") }}</el-radio>
                            <el-radio label="bar">{{ $t("Bar") }}</el-radio>
                          </el-radio-group>
                        </td>
                      </tr>
                      <tr v-if="form.options.timechart.type !== 'bar'">
                        <td>
                          <b class="mr-1">{{ $t("Line stroke") }}</b>
                        </td>
                        <td>
                          <el-radio-group
                            v-model="form.options.timechart.stroke.curve"
                            @change="updateOptions()"
                          >
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
                        </td>
                      </tr>
                      <tr v-if="form.queries.length > 1">
                        <td>
                          <b class="mr-1">{{ $t("Stack series") }}</b>
                        </td>
                        <td>
                          <el-switch
                            v-model="form.options.timechart.stacked"
                            @change="updateOptions()"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </el-collapse-item>
                <el-collapse-item
                  v-if="form.graph_type === 'pie'"
                  :title="$t('Pie Chart')"
                  name="pie"
                >
                  <table style="width: 100%">
                    <tbody>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Chart type") }}</b>
                        </td>
                        <td>
                          <el-radio-group
                            v-model="form.options.piechart.type"
                            @change="fetchData()"
                          >
                            <el-radio label="pie">{{ $t("Pie") }}</el-radio>
                            <el-radio label="donut">{{ $t("Donut") }}</el-radio>
                          </el-radio-group>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </el-collapse-item>
                <el-collapse-item
                  v-if="['text', 'gauge'].indexOf(form.graph_type) === -1"
                  :title="$t('Legend')"
                  name="legend"
                >
                  <table style="width: 100%">
                    <tbody>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Show") }}:</b>
                        </td>
                        <td>
                          <el-switch
                            v-model="form.options.legend.display"
                            @change="updateOptions()"
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Position") }}:</b>
                        </td>
                        <td>
                          <el-radio-group
                            v-model="form.options.legend.position"
                            @change="updateOptions()"
                          >
                            <el-radio label="top">{{ $t("Top") }}</el-radio>
                            <el-radio label="bottom">{{
                              $t("Bottom")
                            }}</el-radio>
                            <el-radio label="left">{{ $t("Left") }}</el-radio>
                            <el-radio label="right">{{ $t("Right") }}</el-radio>
                          </el-radio-group>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </el-collapse-item>
                <el-collapse-item
                  v-if="form.graph_type === 'gauge'"
                  :title="$t('Gauge options')"
                  name="gauge"
                >
                  <table style="width: 100%">
                    <tbody>
                      <tr>
                        <td style="width: 30%">
                          <b class="mr-1">{{ $t("Start Angle") }}</b>
                        </td>
                        <td>
                          <el-input-number
                            v-model="form.options.gauge.startAngle"
                            style="width: 100%"
                            @change="updateOptions()"
                          />
                        </td>
                      </tr>
                      <tr>
                        <td style="width: 30%">
                          <b class="mr-1">{{ $t("End Angle") }}</b>
                        </td>
                        <td>
                          <el-input-number
                            v-model="form.options.gauge.endAngle"
                            style="width: 100%"
                            @change="updateOptions()"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </el-collapse-item>
                <el-collapse-item
                  v-if="form.graph_type === 'text'"
                  :title="$t('Text options')"
                  name="text"
                >
                  <table style="width: 100%">
                    <tbody>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Background Color") }}</b>
                        </td>
                        <td>
                          <el-color-picker
                            v-model="form.options.text.background.color"
                            :predefine="predefineColors"
                            show-alpha
                            @change="fetchData()"
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Text Color") }}</b>
                        </td>
                        <td>
                          <el-color-picker
                            v-model="form.options.text.color"
                            :predefine="predefineColors"
                            show-alpha
                            @change="fetchData()"
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Title Font Size") }}</b>
                        </td>
                        <td>
                          <el-slider
                            v-model="form.options.text.title.fontSize"
                            :min="0"
                            :max="200"
                            @change="fetchData()"
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Value Font Size") }}</b>
                        </td>
                        <td>
                          <el-slider
                            v-model="form.options.text.value.fontSize"
                            :min="0"
                            :max="200"
                            @change="fetchData()"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </el-collapse-item>
                <el-collapse-item
                  v-if="form.graph_type === 'text'"
                  :title="$t('Transform text')"
                  name="transform"
                >
                  <table style="width: 100%; text-align: center">
                    <tbody>
                      <tr>
                        <td>
                          <b class="mr-1">{{ $t("Convert to int") }}</b>
                        </td>
                        <td>
                          <el-switch
                            v-model="form.options.text.convertToInt"
                            @change="updateOptions()"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <table style="width: 100%; text-align: center">
                    <thead>
                      <tr>
                        <th />
                        <th>{{ $t("Operator") }}</th>
                        <th>{{ $t("Pattern") }}</th>
                        <th>{{ $t("Text") }}</th>
                        <th>
                          <el-button
                            type="primary"
                            size="mini"
                            plain
                            @click="form.options.text.value_mapping.push({})"
                          >
                            <i class="fa fa-plus" />
                          </el-button>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(mapping, index) of form.options.text
                          .value_mapping"
                        :key="index"
                      >
                        <td>{{ $t("IF VALUE") }}</td>
                        <td>
                          <el-select
                            v-model="
                              form.options.text.value_mapping[index].operator
                            "
                            size="mini"
                            :placeholder="$t('Operator')"
                          >
                            <el-option :label="$t('Equal')" value="eq" />
                            <el-option :label="$t('Lower than')" value="lt" />
                            <el-option
                              :label="$t('Lower than or equal to')"
                              value="lte"
                            />
                            <el-option :label="$t('Greater than')" value="gt" />
                            <el-option
                              :label="$t('Greater than or equal to')"
                              value="gte"
                            />
                          </el-select>
                        </td>
                        <td>
                          <el-input
                            v-model="
                              form.options.text.value_mapping[index].pattern
                            "
                            type="number"
                            size="mini"
                          />
                        </td>
                        <td>
                          <el-input
                            v-model="
                              form.options.text.value_mapping[index].display
                            "
                            size="mini"
                            :placeholder="$t('Display text')"
                          />
                        </td>
                        <td>
                          <el-button
                            type="danger"
                            size="mini"
                            plain
                            @click="
                              form.options.text.value_mapping.splice(index, 1)
                            "
                          >
                            <i class="fa fa-trash" />
                          </el-button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </el-collapse-item>
              </el-collapse>
            </el-row>
          </el-card>
        </el-col>
      </el-row>
    </el-form>
  </el-card>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import TextChart from "@/components/charts/Text.vue"
import GaugeChart from "@/components/charts/GaugeChart.vue"
import PieChart from "@/components/charts/PieChart.vue"
import TimeChart from "@/components/charts/TimeChart.vue"
import DateRangePicker from "vue2-daterange-picker"
import "vue2-daterange-picker/dist/vue2-daterange-picker.css"

export default {
  components: { DateRangePicker, TimeChart, PieChart, TextChart, GaugeChart },
  mixins: [statsMixin],
  props: {
    widgetId: {
      type: String,
      default: ""
    }
  },
  data: (vm) => ({
    is_loading: false,
    labels: [],
    availableTags: [],
    availableValues: [],
    activeQuery: 0,
    activesTabs: ["time", "legend", "pie", "gauge", "transform", "text"],
    mapping_chart: {
      time: "TimeChart",
      pie: "PieChart",
      text: "TextChart",
      gauge: "GaugeChart"
    },
    selectedDate: vm.$t("Last 10 Minutes"),
    popoverDateOpen: false,
    dateRange: {
      startDate: new moment().subtract(10, "minutes").format(),
      endDate: new moment().format()
    },

    measurements: [],
    mapping: {},
    inputs: [],
    selected_data: null,

    form: {
      name: "",
      queries: [],
      interval: "auto",
      graph_type: "time",
      options: {
        timechart: {
          type: "area",
          stroke: {
            curve: "smooth"
          }
        },
        piechart: {
          type: "pie"
        },
        legend: {
          display: true,
          position: "bottom",
          align: "center",
          fontColor: "#000"
        },
        title: {
          display: true,
          fontColor: "#000"
        },
        gauge: {
          startAngle: -90,
          endAngle: 90
        },
        text: {
          value_mapping: [],
          convertToInt: true,
          color: "#000",
          background: {
            color: "#fff"
          },
          title: {
            fontSize: 30
          },
          value: {
            fontSize: 130
          }
        },
        line: {
          area: false
        }
      },
      optionsOld: {}
    }
  }),

  watch: {
    dateRange() {
      this.fetchData()
    },

    "form.interval"() {
      this.fetchData()
    },

    selectedDate() {
      this.fetchData()
    },

    "form.graph_type"(val) {
      switch (val) {
        case "gauge":
          this.activesTabs = ["legend", "gaugeoptions"]
          break
        case "line":
          this.activesTabs = ["legend", "lineoptions"]
          break
        case "text":
          this.activesTabs = ["legend", "textoptions"]
          break
      }
      this.fetchData()
    },

    "form.options.text.value_mapping"() {
      this.updateOptions()
    }
  },

  mounted() {
    if (!this.widgetId) {
      setTimeout(() => {
        this.addQuery()
        // this.form.queries[0].selected_data = ["system", "load1"]
        // this.fetchData()
      }, 1000)
    } else {
      this.is_loading = true
      request
        .get(`/api/v1/dashboard/widget/${this.widgetId}`)
        .then((response) => {
          this.form.name = response.data.name
          this.form.queries = response.data.queries
          this.form.options = response.data.options
          this.form.graph_type = response.data.graph_type
          this.fetchData()

          this.is_loading = false
        })
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

    fetchAvailableValues(query_index, where_index) {
      const tag = this.form.queries[query_index].where[where_index].field

      request
        .get("/api/v1/inputs/tag/values/", {
          params: {
            measurement: this.form.queries[query_index].selected_data[0],
            tag: tag
          }
        })
        .then((response) => {
          this.form.queries[query_index].where[where_index].availableValues =
            response.data
          this.$forceUpdate()
        })
    },

    addWhere(query_index) {
      const where = { operator: "eq" }

      request
        .get("/api/v1/inputs/tags/", {
          params: {
            measurement: this.form.queries[query_index].selected_data[0]
          }
        })
        .then((response) => {
          where.availableTags = response.data
          this.form.queries[query_index].where.push(where)
        })
    },

    zoom({ start, end }) {
      this.dateRange = [moment(start), moment(end)]
    },

    addQuery() {
      const color =
        this.predefineColors[
          Math.floor(Math.random() * this.predefineColors.length)
        ]

      this.form.queries.push({
        name: "",
        enabled: true,
        color: color,
        agg: "mean",
        where: []
      })

      this.activeQuery = this.form.queries.length - 1
      this.updateOptions()
    },

    deleteQuery(index) {
      this.form.queries.splice(index, 1)
      this.fetchData()
    },

    renderTitle(index) {
      return `${this.$t("Query")} ${index + 1}`
    },

    renderCascaderOption(node, data) {
      switch (data.type) {
        case "measurement":
          return data.label
        case "mapping":
          var html = `
            <span style="float: left; margin-right: 60px;">${data.label}</span>
            <span style="float: right; color: #8492a6; font-size: 13px: margin-left: 60px;">
              <b>${data.mapping_type}</b>
            </span>
          `
          return html
      }
    },

    fetchData() {
      this.is_loading = true
      this.form.options.title.text = this.form.name

      if (this.form.queries.length === 0) return

      let startDate = moment.utc(this.dateRange.startDate)
      let endDate = moment.utc(this.dateRange.endDate)
      if (this.selectedDate !== "custom") {
        const dates = this.getRelativeDate(this.selectedDate)
        startDate = dates.startDate
        endDate = dates.endDate
      }

      let interval = this.form.interval
      if (interval === "auto") {
        interval = this.calculateInterval({
          startDate: startDate,
          endDate: endDate
        })
      }

      const params = {
        queries: [],
        date_start: startDate.format("YYYY-MM-DD HH:mm:ss"),
        date_end: endDate.format("YYYY-MM-DD HH:mm:ss"),
        graph_type: this.form.graph_type,
        interval: interval
      }

      const queries = []

      for (const query of this.form.queries) {
        if (query.enabled && query.selected_data) {
          queries.push({
            color: query.color,
            name: query.name,
            measurement: query.selected_data[0],
            field: query.selected_data[1],
            agg: query.agg,
            where: query.where
          })
        }
      }

      params.queries = queries

      request.post("/api/v1/dashboard/query", params).then((response) => {
        const data = this.formatDatasets(
          this.form.graph_type,
          response.data,
          params
        )

        this.labels = data.labels
        this.$refs.graph.updateSeries(data.datasets)
        this.is_loading = false
      })
    },

    updateOptions() {
      this.$refs.graph.updateOptions()
    },

    saveWidget() {
      const params = {
        name: this.form.name,
        queries: this.form.queries,
        options: this.form.options,
        interval: this.form.interval,
        graph_type: this.form.graph_type
      }

      if (!this.widgetId) {
        request
          .post("/api/v1/dashboard/widget", params)
          .then((response) => {
            const widgetId = response.data._id
            this.$message({
              type: "success",
              message: this.$t("Widget successfully created"),
              showClose: true
            })
            this.$emit("save", widgetId)
          })
          .catch((err) => {
            throw err
          })
      } else {
        request
          .put(`/api/v1/dashboard/widget/${this.widgetId}`, params)
          .then((response) => {
            this.$message({
              type: "success",
              message: this.$t("Widget successfully updated"),
              showClose: true
            })
            this.$emit("save", this.widgetId, true)
          })
      }
    },

    close() {
      this.$emit("close")
    }
  }
}
</script>
<style>
.el-card__header {
  padding: 10px !important;
}

.el-collapse-item__content {
  padding-bottom: 0px;
}

.el-form--inline .el-form-item__label {
  padding-bottom: 0 !important;
}
.apexcharts-canvas {
  width: 100%;
  text-align: center;
}

.filter-table tbody tr td {
  padding: 0;
}
</style>
