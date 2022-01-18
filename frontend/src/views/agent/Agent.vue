<template>
  <div v-if="agent" class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#304156"
      text-color="#fff"
      active-text-color="#F58320"
      router
    >
      <el-menu-item index="1" route="#">
        <i class="fa fa-address-card mr-1" />
        <span v-html="agent.ip_address" />
      </el-menu-item>
      <el-menu-item index="2" route="#">
        <i class="fa fa-server mr-1" />
        <span v-html="agent.hostname" />
      </el-menu-item>
      <el-menu-item index="3" route="#">
        <i :class="renderOSIcon(agent.os, 'mr-1')" />
        <span v-html="agent.os" />
      </el-menu-item>
      <el-menu-item index="4" route="#">
        <i class="fa fa-calendar-alt mr-1" />{{ $t("Last seen") }}:
        <span v-html="renderDate(agent.last_seen)" />
      </el-menu-item>
      <el-menu-item index="5" route="#">
        <el-tag
          v-for="tag in agent.tags"
          :key="tag"
          :disable-transitions="false"
          style="padding: 0"
          effect="dark"
        >
          <div
            style="display: block;width: 100%;height:100%;padding: 0 10px"
            @mouseover="hoverTag(true, tag)"
            @mouseout="hoverTag(false, tag)"
          >
            <span v-if="!isClosable[tag]">
              {{ tag }}
            </span>
            <el-button v-else size="large" type="text" style="padding: 0" @click="handleDeleteTag(tag)">
              <i class="el-icon-close" :style="{'font-size': '15px', top: 0, right: 0, 'margin-right': 0}" />
            </el-button>
          </div>
        </el-tag>
        <el-input
          v-if="tagVisible"
          ref="saveTagInput"
          v-model="tagValue"
          class="input-new-tag"
          size="mini"
          @keyup.enter.native="handleTagConfirm"
          @blur="handleTagConfirm"
        />
        <el-button v-else class="button-new-tag" size="small" @click="showTagInput">{{ $t('Add tag') }}</el-button>
      </el-menu-item>

      <el-menu-item index="6" route="#" style="float: right">
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
      <el-menu-item index="7" style="float: right; padding: 0">
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

    <el-tabs v-model="selectedPanel" tab-position="top" type="border-card" @tab-click="tabClick">
      <el-tab-pane name="dashboards">
        <span slot="label">
          <i class="fa fa-tachometer-alt" /> {{ $t("Dashboards") }}
        </span>
        <agent-dashboard ref="dashboard" :agent_id="agent_id" :date-range="dateRange" :selected-date="selectedDate" :interval="interval" />
      </el-tab-pane>
      <el-tab-pane name="paquets">
        <span slot="label">
          <i class="fa fa-database" /> {{ $t("Softwares") }}
        </span>
        <softwares :agent="agent" />
      </el-tab-pane>
      <el-tab-pane name="alerts">
        <span slot="label">
          <i class="fa fa-bell mr-1" />{{ $t("Alerts") }}
        </span>
        <alert-list :agent_id="agent._id" />
      </el-tab-pane>
      <el-tab-pane name="plugins">
        <span slot="label">
          <i class="el-icon-message mr-1" />{{ $t("Plugins") }}
        </span>
        <el-card
          class="box-card no-round"
          shadow="always"
          :body-style="{ padding: '5px 10px' }"
        >
          <el-row>
            <el-button
              type="primary"
              style="float: right"
              size="mini"
              plain
              @click="addInput()"
            >
              <i class="fa fa-plus" /> {{ $t("Add") }}
            </el-button>
          </el-row>
          <el-row>
            <div ref="pluginContainer">
              <el-card
                v-for="input in inputs"
                :key="input._id"
                class="box-card no-round card-plugin"
                shadow="hover"
                :style="renderStyle(input.plugin)"
                :body-style="{
                  padding: '5px 10px',
                  'background-color': '#405672',
                  height: '100%'
                }"
              >
                <div slot="header" class="">
                  <span>{{ input.plugin.title }}</span>
                  <div style="position: relative; top: -20px; right: 0px">
                    <el-popconfirm
                      :confirm-button-text="$t('Delete')"
                      :cancel-button-text="$t('Cancel')"
                      icon="el-icon-info"
                      icon-color="orange"
                      popper-class="popover-delete"
                      :title="$t('Are you sure to delete this?')"
                      @confirm="deleteInput(input)"
                    >
                      <el-button
                        v-if="input.plugin.title !== 'System'"
                        slot="reference"
                        type="danger"
                        size="mini"
                        style="float: right; padding: 4px"
                      >
                        <i class="fa fa-trash" />
                      </el-button>
                    </el-popconfirm>
                    <el-button
                      type="primary"
                      size="mini"
                      style="float: right; margin-right: 5px; padding: 4px"
                      @click="editInput(input)"
                    >
                      <i class="fa fa-edit" />
                    </el-button>
                    <el-popover
                      placement="bottom"
                      :title="input.plugin.title"
                      width="400"
                      trigger="click"
                      :content="input.plugin.description"
                    >
                      <el-button
                        slot="reference"
                        style="float: right; margin-right: 5px; padding: 4px"
                      >
                        <i class="fa fa-info-circle" />
                      </el-button>
                    </el-popover>
                  </div>
                </div>
                <p class="text-center">
                  <i
                    v-if="input.plugin.icon"
                    :class="renderIcon(input.plugin.icon, 'large')"
                  />
                  <img
                    v-else-if="input.plugin.img"
                    :width="input.plugin.img_size"
                    :src="renderImage(input.plugin.img)"
                  >
                </p>
              </el-card>
            </div>
          </el-row>
        </el-card>
      </el-tab-pane>
      <el-tab-pane name="rules">
        <span slot="label">
          <i class="el-icon-odometer mr-1" />{{ $t("Rules") }}
        </span>
        <rules :agent_id="agent_id" />
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogInputVisible"
      :width="renderDialogWidth()"
      @close="input_id = null"
    >
      <edit-input
        v-if="dialogInputVisible"
        :agent-id="agent._id"
        :input-id="input_id"
        @pluginSaved="inputSaved()"
      />
    </el-dialog>
  </div>
</template>

<script>
import Rules from "./Rules.vue"
import moment from "moment"
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import renderMixin from "@/mixins/renderMixin"
import Softwares from "./components/Softwares.vue"
import EditInput from "@/views/input/EditInput.vue"
import AlertList from "@/components/AlertList.vue"
import DateRangePicker from "vue2-daterange-picker"
import "vue2-daterange-picker/dist/vue2-daterange-picker.css"
import AgentDashboard from "./components/AgentDashboard.vue"

export default {
  components: { EditInput, Rules, AlertList, AgentDashboard, DateRangePicker, Softwares },
  mixins: [renderMixin, statsMixin],

  props: {
    propAgent: {
      type: String,
      default: null
    }
  },

  data: () => ({
    dialogInputVisible: false,
    popoverDateOpen: false,
    selectedDate: "1h",
    pluginChoices: [],
    interval: "auto",
    dateRange: {
      startDate: new moment().subtract(1, "hour").format(),
      endDate: new moment().format()
    },
    dialogTitle: "",
    tagVisible: false,
    tagValue: "",
    isClosable: {},
    selectedPanel: "dashboards",
    input_id: null,
    agent: null,
    agent_id: null,
    inputs: []
  }),

  watch: {
  },

  beforeMount() {
    if (this.propAgent) {
      this.agent_id = this.propAgent
    }

    request.get("/api/v1/inputs/plugins").then((response) => {
      this.pluginChoices = response.data
    })
  },

  mounted() {
    if (this.$route.params.id) {
      this.agent_id = this.$route.params.id
    }

    if (this.$route.query.panel) {
      this.selectedPanel = this.$route.query.panel
    }

    request.get(`/api/v1/agents/${this.agent_id}`).then((response) => {
      this.agent = response.data
      this.fetchInputs()
    })

    window.addEventListener("resize", () => {
      this.$forceUpdate()
    })
  },

  methods: {
    hoverTag(state, tag) {
      this.isClosable = {}
      this.isClosable[tag] = state
      this.$forceUpdate()
    },

    handleDeleteTag(tag) {
      this.agent.tags.splice(this.agent.tags.indexOf(tag), 1)
      request.put(`/api/v1/agents/${this.agent._id}`, { tags: this.agent.tags }).then((response) => {
        this.$message({
          type: "success",
          message: this.$t("Tags successfully saved"),
          showClose: true
        })
      })
    },

    showTagInput() {
      this.tagVisible = true
      this.$nextTick(_ => {
        this.$refs.saveTagInput.$refs.input.focus()
      })
    },

    handleTagConfirm() {
      const tagValue = this.tagValue
      if (tagValue) {
        if (this.agent.tags.indexOf(tagValue) === -1) {
          this.agent.tags.push(tagValue)

          request.put(`/api/v1/agents/${this.agent._id}`, { tags: this.agent.tags }).then((response) => {
            this.$message({
              type: "success",
              message: this.$t("Tags successfully saved"),
              showClose: true
            })
          })
        }
      }
      this.tagVisible = false
      this.tagValue = ""
    },

    tabClick() {
      setTimeout(() => {
        this.calculateFlipWidth()
        this.$refs.dashboard.resize()
        this.$forceUpdate()
      }, 10)
    },

    calculateFlipWidth() {
      const windowSize = window.innerWidth
      let element_per_line = 8
      if (windowSize < 3000) element_per_line = 4
      if (windowSize < 1000) element_per_line = 1

      const element = this.$refs.pluginContainer
      const width = `${element.clientWidth / element_per_line - 1}px`
      return width
    },

    renderStyle(item) {
      return `
        width: ${this.calculateFlipWidth()};
        height: 150px;
        background-color: #304156;
        float: left;
        color: #fff;
      `
    },

    fetchInputs() {
      request.get(`/api/v1/agents/inputs/${this.agent_id}`).then((response) => {
        const inputs = []
        for (const tmp of response.data) {
          for (const plugin of this.pluginChoices) {
            if (plugin.title.toLowerCase() === tmp.plugin_name.toLowerCase()) {
              tmp.plugin = plugin
              inputs.push(tmp)
              break
            }
          }
        }
        this.inputs = response.data
      })
    },

    addInput() {
      this.dialogTitle = this.$t("Add Plugin")
      this.dialogInputVisible = true
    },

    editInput(input) {
      this.dialogTitle = this.$t("Edit Plugin")
      this.input_id = input._id
      this.dialogInputVisible = true
    },

    deleteInput(input) {
      request.delete(`/api/v1/inputs/${input._id}`).then((response) => {
        this.$message({
          type: "success",
          message: this.$t("Input successfully deleted"),
          showClose: true
        })

        this.fetchInputs()
      })
    },

    inputSaved() {
      this.input_id = null
      this.dialogInputVisible = false
      this.fetchInputs()
    }
  }
}
</script>

<style lang="scss" scoped>
.panel-group {
  margin-top: 20px;
  margin-left: 0 !important;
  margin-right: 0 !important;
  .card-panel-col {
    margin-bottom: 32px;
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
    &:hover {
      // .card-panel-icon-wrapper {
      //   color: #fff;
      // }
      // .icon-ipaddress {
      //   background: #f49b51;
      // }
      .icon-message {
        background: #36a3f7;
      }
      .icon-money {
        background: #f4516c;
      }
      .icon-shopping {
        background: #34bfa3;
      }
    }
    .icon-people {
      color: #40c9c6;
    }
    .icon-message {
      color: #36a3f7;
    }
    .icon-money {
      color: #f4516c;
    }
    .icon-shopping {
      color: #34bfa3;
    }
    .card-panel-icon-wrapper {
      float: left;
      background-color: #fff;
      margin: 14px 0 0 14px;
      padding: 16px;
      transition: all 0.38s ease-out;
      border-radius: 6px;
    }
    .card-panel-icon {
      float: left;
      font-size: 48px;
    }
    .card-panel-description {
      text-align: right;
      font-weight: bold;
      padding: 26px;
      margin-left: 0px;
      font-size: 20px;
      .card-panel-text {
        line-height: 18px;
        color: #eee;
        font-size: 20px;
        margin-bottom: 12px;
        font-size: 18px;
      }
      .card-panel-info {
        font-size: 18px;
      }
      .card-panel-num {
        font-size: 18px;
      }
    }
  }
}
@media (max-width: 550px) {
  .card-panel-description {
    display: none;
  }
  .card-panel-icon-wrapper {
    float: none !important;
    width: 100%;
    height: 100%;
    margin: 0 !important;
    .svg-icon {
      display: block;
      margin: 14px auto !important;
      float: none !important;
    }
  }
}
</style>
