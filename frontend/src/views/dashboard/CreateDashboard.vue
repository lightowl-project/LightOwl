<template>
  <div class="dashboard-container">
    <no-widgets v-if="!widgets.length" @newWidget="newWidget = true" />
    <div v-else>
      <el-menu
        class="el-menu-demo"
        mode="horizontal"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#F58320"
      >
        <el-menu-item index="1" @click="newWidget = true">
          <i class="fa fa-plus mr-1" />{{ $t("Add a Widget") }}
        </el-menu-item>

        <el-menu-item index="4" style="float: right" @click="saveDashboard()">
          <i class="fa fa-save" />
        </el-menu-item>
        <el-menu-item index="8" style="float: right; padding: 0">
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
                :time-picker24hour="true"
                :show-week-numbers="true"
                :show-dropdowns="true"
                :time-picker="true"
                :auto-apply="true"
                opens="inline"
                :ranges="false"
                @update="updateValues"
              />
            </div>
            <el-button slot="reference" size="mini" v-html="dateStr" />
          </el-popover>
        </el-menu-item>

        <el-menu-item index="2" style="float: right; padding: 0">
          <label class="mr-1">{{ $t("Interval") }}:</label>
          <el-select
            v-model="interval"
            size="mini"
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
        </el-menu-item>
      </el-menu>

      <grid-layout
        :layout.sync="widgets"
        :col-num="12"
        :row-height="30"
        :is-draggable="true"
        :is-resizable="true"
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
            :ref="renderRef(index)"
            :edit-mode="true"
            :index="index"
            :interval="interval"
            :selected-date="selectedDate"
            :date-range="dateRange"
            :widget-id="item.widget_id"
            @editWidget="editWidget"
            @deleteWidget="deleteWidget"
          />
        </grid-item>
      </grid-layout>
    </div>
    <el-drawer
      size="50%"
      :with-header="false"
      :visible.sync="newWidget"
      direction="rtl"
      :before-close="handleClose"
    >
      <create-widget
        v-if="newWidget"
        :widget-id="widget_id_edit"
        @close="
          newWidget = false;
          widget_id_edit = null;
        "
        @save="addWidget"
      />
    </el-drawer>
  </div>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import VueGridLayout from "vue-grid-layout"
import Widget from "./components/Widget.vue"
import CreateWidget from "./CreateWidget.vue"
import DateRangePicker from "vue2-daterange-picker"
import "vue2-daterange-picker/dist/vue2-daterange-picker.css"
import NoWidgets from "./NoWidgets.vue"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  components: {
    GridLayout: VueGridLayout.GridLayout,
    GridItem: VueGridLayout.GridItem,
    DateRangePicker,
    CreateWidget,
    NoWidgets,
    Widget
  },
  mixins: [statsMixin],
  data: () => ({
    selectedDate: "7d",
    popoverDateOpen: false,
    interval: "auto",
    newWidget: false,
    widget_id_edit: null,
    dateRange: {
      startDate: new moment().subtract(7, "days").format(),
      endDate: new moment().format()
    },
    id: null,
    widgets: []
  }),

  mounted() {
    if (this.$route.params.id) {
      this.id = this.$route.params.id
      request.get(`/api/v1/dashboard/${this.id}`).then((response) => {
        this.name = response.data.name
        this.widgets = response.data.widgets
        if (!this.widgets.length) this.newWidget = true
      })
    }
  },

  methods: {
    renderRef(index) {
      return `widget_${index}`
    },

    handleClose(done) {
      this.$confirm(this.$t("Are you sure you want to close this ?"))
        .then((_) => {
          this.widget_id_edit = null
          done()
        })
        .catch((_) => {})
    },

    selectDate(key, text) {
      this.selectedDate = key
      this.popoverDateOpen = false
    },

    addWidget(widget_id, edit) {
      this.newWidget = false
      this.widget_id_edit = null

      const tmp = {
        x: (this.widgets.length * 6) % 12,
        y: this.widgets.length + 12, // puts it at the bottom
        w: 6,
        h: 10,
        i: this.widgets.length,
        widget_id: widget_id
      }

      if (!edit) {
        this.widgets.push(tmp)
      } else {
        for (const i in this.widgets) {
          const widget = this.widgets[i]
          if (widget.widget_id === widget_id) {
            this.$refs[`widget_${i}`][0].init()
            break
          }
        }
      }
    },

    editWidget(widget_id) {
      this.widget_id_edit = widget_id
      this.newWidget = true
    },

    deleteWidget(index) {
      const item = this.widgets[index]
      request
        .delete(`/api/v1/dashboard/widget/${item.widget_id}`)
        .then((response) => {
          this.widgets.splice(index, 1)
          this.$message({
            type: "success",
            message: this.$t("Widget successfully deleted"),
            showClose: true
          })
        })
    },

    saveDashboard() {
      if (!this.id) {
        this.$prompt(this.$t("Dashboard name"), this.$t("Save"), {
          confirmButtonText: this.$t("Save"),
          cancelButtonText: this.$t("Cancel")
        })
          .then(({ value }) => {
            const params = {
              name: value,
              widgets: this.widgets
            }

            request.post("/api/v1/dashboard/", params).then((response) => {
              this.$message({
                type: "success",
                message: this.$t("Dashboard successfully created"),
                showClose: true
              })
              this.$router.push(`/dashboard/${response.data._id}`)
            })
          })
          .catch(() => {})
      } else {
        const params = {
          name: this.name,
          widgets: this.widgets
        }
        request.put(`/api/v1/dashboard/${this.id}`, params).then((response) => {
          this.$message({
            type: "success",
            message: this.$t("Dashboard successfully updated"),
            showClose: true
          })
          this.$router.push(`/dashboard/${this.id}`)
        })
      }
    }
  }
})
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
