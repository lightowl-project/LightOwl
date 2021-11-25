<template>
  <div>
    <light-owl-table ref="table" uri="/api/v1/alerts/" :custom-params="{priority: priority, agent_id: agent_id}" :default-sort="sortOrder" @rowClicked="showDetail">
      <template slot="columns">
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
          width="100"
          prop="agent"
          :label="$t('Agent')"
        >
          <div slot-scope="{ row }" class="d-flex">
            {{ row.agent.ip_address }}
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
          width="200"
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
            <router-link :to="buildViewerLink(row)">
              <el-tooltip class="item" effect="dark" :content="$t('Open Log Viewer')" placement="top">
                <el-button type="default" size="mini"><i class="fa fa-search" /></el-button>
              </el-tooltip>
            </router-link>

            <el-popconfirm
              :confirm-button-text="$t('Acknowledge')"
              :cancel-button-text="$t('Cancel')"
              icon="el-icon-info"
              icon-color="success"
              confirm-button-type="success"
              popper-class="popover-delete"
              :title="$t('Are you sure to acknowledge this alert ?')"
              @confirm="acknowledgeAlert(row)"
            >
              <el-tooltip slot="reference" class="item" effect="dark" :content="$t('Acknowledge the alert')" placement="top">
                <el-button type="success" size="mini" style="margin-left: 5px"><i class="fa fa-check" /></el-button>
              </el-tooltip>
            </el-popconfirm>
          </div>
        </el-table-column>
      </template>
    </light-owl-table>

  </div>
</template>

<script>
import request from "@/utils/request"
import EventBus from "@/event-bus"
import renderMixin from "@/mixins/renderMixin"
import ChartAlert from "@/components/ChartAlert.vue"
import { defineComponent } from "@vue/composition-api"
import LightOwlTable from "@/components/Table/index.vue"

export default defineComponent({
  components: { LightOwlTable, ChartAlert },
  mixins: [renderMixin],

  props: {
    agent_id: {
      type: String,
      required: true
    },
    priority: {
      type: Number,
      default: null
    }
  },

  data: () => ({
    measurements_choices: [],
    rule_edit_id: null,
    sortOrder: {
      prop: "priority",
      order: "descending"
    }
  }),

  mounted() {
    this.fetch_measurements()
  },

  methods: {
    showDetail(row, column) {
      if (column.property === "_id") {
        return
      }

      this.$refs.table.toggleRowExpansion(row)
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

    acknowledgeAlert(alert) {
      request.post(`/api/v1/alerts/${alert._id}/acknowledge`).then((response) => {
        this.$refs.table.getData()
        EventBus.$emit("reload")
      })
    }
  }
})
</script>
