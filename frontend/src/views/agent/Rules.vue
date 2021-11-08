<template>
  <div>
    <light-owl-table ref="table" uri="/api/v1/rules/" :default-sort="sortOrder" :custom-params="{agent_id: agent_id}" @rowClicked="showDetail">
      <template slot="columns">
        <el-table-column type="expand">
          <template slot-scope="{ $index, row }">
            <span v-if="row.field">
              <chart
                :ref="renderChartRef($index)"
                :agent_ids="[agent_id]"
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
          <template slot="header">
            <el-button
              style="float: right"
              type="primary"
              size="mini"
              plain
              @click="modalEditRule = true"
            >
              <i class="fa fa-plus" /> {{ $t("Add") }}
            </el-button>
          </template>
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

    <el-dialog :visible.sync="modalEditRule" :width="renderDialogWidth()" :show-close="false" custom-class="dialog-form" :destroy-on-close="true" @close="rule_edit_id = null;">
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
        :agent_id="agent_id"
        :rule_id="rule_edit_id"
        @save="
          rule_edit_id = null;
          modalEditRule = false;
          $refs.table.getData()
        "
      />
    </el-dialog>
  </div>
</template>

<script>
import LightOwlTable from "@/components/Table/index.vue"
import { defineComponent } from "@vue/composition-api"
import EditRule from "@/views/rules/EditRule.vue"
import renderMixin from "@/mixins/renderMixin"
import Chart from "@/components/Chart.vue"
import request from "@/utils/request"

export default defineComponent({
  components: { Chart, EditRule, LightOwlTable },
  mixins: [renderMixin],

  props: {
    agent_id: {
      type: String,
      required: true
    }
  },
  data: () => ({
    rule_edit_id: null,
    modalEditRule: false,
    sortOrder: {
      prop: "priority",
      order: "ascending"
    }
  }),

  methods: {
    showDetail(row, column) {
      if (column.property === "_id") {
        return
      }

      this.$refs.table.toggleRowExpansion(row)
    },

    renderRule(rule) {
      const sql = `If ${rule.measurement}.${rule.field} ${this.$t(
        rule.operator
      )} ${rule.pattern} for ${this.$t(rule.duration)}`
      return sql
    },

    renderChartRef(index) {
      return `charts-${index}`
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

    editRule(rule) {
      this.rule_edit_id = rule._id
      this.modalEditRule = true
    },

    deleteRule(rule) {
      request.delete(`/api/v1/rules/${rule._id}`).then((response) => {
        this.$message({
          type: "success",
          message: this.$t("Rule successfully deleted"),
          showClose: true
        })

        this.$refs.table.getData()
      })
    }
  }
})
</script>
