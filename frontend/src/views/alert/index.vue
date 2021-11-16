<template>
  <div class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#F58320"
      router
    >
      <el-menu-item index="1" route="/alerts/">
        <i class="fa fa-bell" /> {{ $t("Alerts") }}
      </el-menu-item>

      <el-menu-item index="2" route="#">
        <el-select v-model="customParams.agent_id" clearable :placeholder="$t('Agent')" size="mini" @change="$refs.table.getData()">
          <el-option
            v-for="agent in agents"
            :key="agent._id"
            :label="agent.ip_address"
            :value="agent._id"
          />
        </el-select>
      </el-menu-item>

      <el-tooltip class="item" effect="dark" :content="$t('Acknowledge selected alerts')" placement="bottom">
        <el-menu-item index="3" route="#" style="float: right" @click="acknowledgeAlerts()">
          <i class="fa fa-check" />
        </el-menu-item>
      </el-tooltip>
    </el-menu>

    <el-card :body-style="{margin: 0, padding: 0}" class="no-border">
      <light-owl-table ref="table" uri="/api/v1/alerts/" row-key="_id" :custom-params="customParams" :default-sort="sortOrder" @rowClicked="showDetail" @selectionChange="selectionChange">
        <template slot="columns">
          <el-table-column type="selection" width="45" />
          <el-table-column type="expand">
            <template slot-scope="{ $index, row }">
              <chart-alert
                :ref="$index"
                :alert_id="row._id"
              />
            </template>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            width="90"
            prop="priority"
            :label="$t('Priority')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <el-tag
                :type="renderTagPriority(row.priority)"
                size="small"
                effect="dark"
              >{{ row.priority }}</el-tag>
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            width="150"
            prop="agent"
            :label="$t('Agent')"
          >
            <div slot-scope="{ row }" class="d-flex">
              {{ row.agent.ip_address }} <small>{{ row.agent.hostname }}</small>
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            width="150"
            prop="first_raise"
            :label="$t('First raise')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <span v-html="renderDate(row.first_raise)" />
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            width="150"
            prop="last_raise"
            :label="$t('Last raise')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <span v-html="renderDate(row.last_raise)" />
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            prop="rule"
            :label="$t('Rule')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <span v-if="row.rule">
                {{ row.rule.name }}
              </span>
              <span v-else>
                N/A
              </span>
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            prop="measurement"
            :label="$t('Measurement')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <span v-if="row.rule">
                {{ row.rule.measurement }}
              </span>
              <span v-else>
                N/A
              </span>
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            prop="field"
            :label="$t('Field')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <span v-if="row.rule">
                {{ row.rule.field }}
              </span>
              <span v-else>
                N/A
              </span>
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            prop="nb_raise"
            :label="$t('Nb raise')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <el-tag effect="dark" size="mini" type="danger">
                {{ row.nb_raise }}
              </el-tag>
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            prop="_id"
            :label="$t('Actions')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <!-- <router-link :to="buildViewerLink(row)">
                <el-tooltip class="item" effect="dark" :content="$t('Open Log Viewer')" placement="top">
                  <el-button type="default" size="mini"><i class="fa fa-search" /></el-button>
                </el-tooltip>
              </router-link> -->

              <el-tooltip class="item" effect="dark" :content="$t('Show Rule')" placement="top">
                <el-button type="info" size="mini" style="margin-left: 5px" @click="openRule(row)"><i class="el-icon-s-claim" /></el-button>
              </el-tooltip>

              <el-popconfirm
                :confirm-button-text="$t('Acknowledge')"
                :cancel-button-text="$t('Cancel')"
                icon="el-icon-info"
                icon-color="success"
                confirm-button-type="success"
                popper-class="popover-delete"
                :title="$t('Are you sure to acknowledge this alert ?')"
                @confirm="acknowledgeAlerts([row])"
              >
                <el-tooltip slot="reference" class="item" effect="dark" :content="$t('Acknowledge the alert')" placement="top">
                  <el-button type="success" size="mini" style="margin-left: 5px"><i class="fa fa-check" /></el-button>
                </el-tooltip>
              </el-popconfirm>
            </div>
          </el-table-column>
        </template>
      </light-owl-table>
    </el-card>

    <el-dialog :visible.sync="modalEditRule" width="70%" :show-close="false" custom-class="dialog-form" :destroy-on-close="true" @close="rule_edit_id = null;">
      <div slot="title">
        <span v-if="rule_edit_id">{{ $t("Edit Rule") }}</span>
        <span v-else>{{ $t("Create Rule") }}</span>

        <el-button
          type="primary"
          style="float: right"
          size="mini"
          @click="$refs.editRule.saveRule()"
        >
          <i class="fa fa-save" />
        </el-button>
        <el-button
          plain
          style="float: right; margin-right: 10px"
          size="mini"
          @click="modalEditRule = false"
        >
          <i class="fa fa-times" />
        </el-button>
      </div>
      <edit-rule
        v-if="modalEditRule"
        ref="editRule"
        :measurements="measurements_choices"
        :agent_id="agent_id"
        :rule_id="rule_edit_id"
        @save="
          rule_edit_id = null;
          modalEditRule = false;
        "
      />
    </el-dialog>
  </div>
</template>

<script>
import request from "@/utils/request"
import EventBus from "@/event-bus"
import renderMixin from "@/mixins/renderMixin"
import EditRule from "@/views/rules/EditRule.vue"
import ChartAlert from "@/components/ChartAlert.vue"
import { defineComponent } from "@vue/composition-api"
import LightOwlTable from "@/components/Table/index.vue"

export default defineComponent({
  components: { LightOwlTable, ChartAlert, EditRule },
  mixins: [renderMixin],

  props: {
    agent_id: {
      type: String,
      default: null
    },
    priority: {
      type: Number,
      default: null
    }
  },

  data: () => ({
    modalEditRule: false,
    measurements_choices: [],
    rule_edit_id: null,
    interval: null,
    agents: [],
    customParams: {},
    selected_rows: [],
    sortOrder: {
      prop: "priority",
      order: "ascending"
    }
  }),

  beforeMount() {
    this.customParams = {
      priority: this.priority,
      agent_id: this.agent_id
    }
  },

  mounted() {
    this.getAgents()
    this.fetch_measurements()

    EventBus.$on("reload", () => {
      this.$refs.table.getData()
    })

    this.interval = setInterval(() => {
      this.$refs.table.getData()
    }, 10000)
  },

  beforeDestroy() {
    if (this.interval) {
      clearInterval(this.interval)
    }
  },

  methods: {
    async getAgents() {
      const response = await request.get("/api/v1/agents", { params: { all: true }})
      this.agents = response.data
    },

    showDetail(row, column) {
      if (column.property === "_id") {
        return
      }

      this.$refs.table.toggleRowExpansion(row)
    },

    selectionChange(rows) {
      this.selected_rows = rows
    },

    openRule(alert) {
      this.rule_edit_id = alert.rule._id
      this.modalEditRule = true
    },

    fetch_measurements() {
      request
        .get(`/api/v1/inputs/measurements/${this.agent_id}`)
        .then((response) => {
          this.measurements_choices = response.data
        })
    },

    buildViewerLink(data) {
      return `/viewer/${data._id}`
    },

    async acknowledgeAlerts(alerts) {
      if (!alerts) {
        alerts = this.selected_rows
      }

      this.$refs.table.triggerLoading()
      for (const alert of alerts) {
        await request.post(`/api/v1/alerts/${alert._id}/acknowledge`)
      }
      this.$refs.table.getData()
    }
  }
})
</script>
