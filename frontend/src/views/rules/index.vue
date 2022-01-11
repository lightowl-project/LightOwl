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
      <el-menu-item index="1" route="/rules/">
        <i class="el-icon-s-claim" />{{ $t("Rules") }}
      </el-menu-item>

      <el-menu-item index="2" route="#">
        <el-input v-model="search" type="text" prefix-icon="el-icon-search" size="mini" :style="{width: '300px'}" :placeholder="$t('Search')" @keyup.enter.native="$refs.table.getData()" />
      </el-menu-item>

      <el-menu-item index="3" route="#">
        <el-select v-model="customParams.agent_id" clearable :placeholder="$t('Agent')" size="mini" @change="$refs.table.getData()">
          <el-option
            v-for="agent in agents"
            :key="agent._id"
            :label="render_asset_label(agent)"
            :value="agent._id"
          />
        </el-select>
      </el-menu-item>

      <el-menu-item index="'4" style="float: right" route="#" @click="modalEditRule = true">
        <i class="fa fa-plus" /> {{ $t("Add") }}
      </el-menu-item>
    </el-menu>

    <el-card :body-style="{margin: 0, padding: 0}">
      <light-owl-table ref="table" uri="/api/v1/rules/" :custom-params="customParams" :default-sort="sortOrder" :search="search" @rowClicked="showDetail">
        <template slot="columns">
          <el-table-column type="expand">
            <template slot-scope="{ $index, row }">
              <span v-if="row.field">
                <chart
                  :ref="renderChartRef($index)"
                  :agent_ids="getRuleAgents(row)"
                  :collector="row"
                  agg="last"
                />
              </span>
            </template>
          </el-table-column>
          <el-table-column
            width="100"
            align="left"
            prop="enabled"
            :sortable="true"
            :label="$t('Enabled')"
          >
            <div slot-scope="{ row }">
              <el-switch
                v-model="row.enabled"
                size="mini"
                @change="updateRule(row)"
              />
            </div>
          </el-table-column>
          <el-table-column
            width="100"
            align="left"
            :sortable="true"
            prop="priority"
            :label="$t('Priority')"
          >
            <div slot-scope="{ row }">
              <el-tag
                :type="renderTagPriority(row.priority)"
                size="small"
                effect="dark"
              >{{ row.priority }}</el-tag>
            </div>
          </el-table-column>
          <el-table-column
            width="200"
            align="left"
            :sortable="true"
            prop="name"
            :label="$t('Name')"
          />
          <el-table-column
            width="200"
            align="left"
            :sortable="true"
            prop="agent"
            :label="$t('Agents')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <el-tag v-for="agent in row.agents" :key="agent._id" effect="dark" size="small">
                {{ agent.ip_address }}
              </el-tag>
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            width="200"
            :sortable="true"
            prop="created_at"
            :label="$t('Dates')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <p style="margin: 0;padding: 0"><b>{{ $t("Created") }}:</b> <span v-html="renderDate(row.created_at)" /></p>
              <p style="margin: 0;padding: 0"><b>{{ $t("Updated") }}:</b> <span v-html="renderDate(row.updated_at)" /></p>
            </div>
          </el-table-column>

          <el-table-column align="left" :label="$t('Rule')">
            <div slot-scope="{ row }" class="d-flex">
              <span style="font-size: 15px">
                <b>{{ $t("If") }}</b>
                <el-tag
                  size="small"
                  style="margin: 0 10px"
                  type="primary"
                  effect="dark"
                >
                  {{ row.measurement }}.{{ row.field }}
                </el-tag>
                <b>{{ $t(row.operator) }}</b>
                <el-tag
                  size="small"
                  style="margin: 0 10px"
                  type="primary"
                  effect="dark"
                >
                  {{ row.pattern }}
                </el-tag>
                <span v-if="row.duration !== 'oneshot'">
                  <b>{{ $t("For") }}</b>
                  <el-tag
                    size="small"
                    style="margin: 0 10px"
                    type="primary"
                    effect="dark"
                  >
                    {{ $t(row.duration) }}
                  </el-tag>
                </span>
              </span>
            </div>
          </el-table-column>
          <el-table-column align="center" width="100" :label="$t('Actions')" prop="_id">
            <template slot-scope="{ row }" class="d-flex">
              <el-button
                type="primary"
                size="mini"
                @click="editRule(row)"
              >
                <i class="fa fa-edit" />
              </el-button>
              <el-popconfirm
                :confirm-button-text="$t('Delete')"
                :cancel-button-text="$t('Cancel')"
                icon="el-icon-info"
                icon-color="orange"
                popper-class="popover-delete"
                :title="$t('Are you sure to delete this rule ?')"
                @confirm="deleteRule(row)"
              >
                <el-button
                  slot="reference"
                  type="danger"
                  size="mini"
                  style="margin-left: 5px"
                >
                  <i class="fa fa-trash" />
                </el-button>
              </el-popconfirm>
            </template>
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
        :rule_id="rule_edit_id"
        @save="
          rule_edit_id = null;
          modalEditRule = false;
          refreshTable()
        "
      />
    </el-dialog>
  </div>
</template>

<script>
import LightOwlTable from "@/components/Table/index.vue"
import renderMixin from "@/mixins/renderMixin"
import Chart from "@/components/Chart.vue"
import EditRule from "./EditRule.vue"
import request from "@/utils/request"

export default {
  components: { Chart, LightOwlTable, EditRule },
  mixins: [renderMixin],

  data: () => ({
    popovers: {},
    customParams: {
      agent_id: null
    },
    rule_edit_id: null,
    modalEditRule: false,
    agents: [],
    search: "",
    sortOrder: {
      prop: "priority",
      order: "ascending"
    }
  }),

  mounted() {
    this.getAgents()
  },

  methods: {
    async getAgents() {
      const response = await request.get("/api/v1/agents", { params: { all: true }})
      this.agents = response.data
    },

    showDetail(row, column) {
      if (["_id", "enabled"].indexOf(column.property) > -1) {
        return
      }

      this.$refs.table.toggleRowExpansion(row)
    },

    renderChartRef(index) {
      return `charts-${index}`
    },

    getRuleAgents(rule) {
      const tmp = []
      for (const agent of rule.agents) {
        tmp.push(agent._id)
      }

      return tmp
    },

    updateRule(rule) {
      const data = {
        rule: rule._id,
        enabled: rule.enabled
      }

      request.post("/api/v1/rules/enable", data).then((response) => {
        let message = ""
        if (rule.enabled) message = this.$t("Rule successfully enabled")
        else message = this.$t("Rule successfully disabled")

        this.$message({
          type: "success",
          message: message,
          showClose: true
        })

        this.$refs.table.getData()
      })
    },

    refreshTable() {
      this.$refs.table.getData()
    },

    constructURI(data) {
      return `/rules/edit/${data._id}`
    },

    editRule(rule) {
      this.rule_edit_id = rule._id
      this.modalEditRule = true
    },

    deleteRule(data) {
      request.delete(`/api/v1/rules/${data._id}`).then(() => {
        this.refreshTable()
      })
    }
  }
}
</script>
