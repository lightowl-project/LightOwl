<template>
  <div class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#F58320"
    >
      <el-menu-item index="1" route="/agents/">
        <i class="fa fa-laptop mr-1" />{{ $t("Agents") }}
      </el-menu-item>

      <el-menu-item index="2" route="#">
        <el-input v-model="search" type="text" prefix-icon="el-icon-search" size="mini" :style="{width: '300px'}" :placeholder="$t('Search')" @keyup.enter.native="$refs.table.getData()" />
      </el-menu-item>

      <el-menu-item
        index="3"
        style="float: right"
        @click="dialogAddAgentVisible = true"
      >
        <i class="fa fa-plus" /> {{ $t("Add") }}
      </el-menu-item>
    </el-menu>

    <el-dialog
      v-if="config"
      :title="$t('Add an agent')"
      width="30%"
      :visible.sync="dialogAddAgentVisible"
    >
      <div slot="header" />
      <p>
        {{ $t("Download the agent:") }}
        <el-link type="primary" size="mini" href="https://lightowl.io/dl/" target="_blank">
          <i class="fa fa-download" /> {{ $t("Here") }}
        </el-link>
      </p>
      <p>
        {{ $t("Choose the agent corresponding to your Operating System") }}
      </p>
      <p>
        {{ $t("Then launch the install script") }}:
      </p>
      <code v-html="install_script" />
    </el-dialog>

    <el-card :body-style="{margin: 0, padding: 0}" class="no-border">
      <light-owl-table
        ref="table"
        uri="/api/v1/agents/"
        :search="search"
        :default-sort="sortOrder"
        @rowClicked="openAgent"
      >
        <template slot="columns">
          <el-table-column
            align="left"
            :sortable="true"
            prop="hostname"
            :label="$t('Hostname')"
          />

          <el-table-column
            align="left"
            :sortable="true"
            prop="ip_address"
            :label="$t('IP Address')"
          />
          <el-table-column
            align="left"
            :sortable="true"
            prop="os"
            :label="$t('OS')"
          >
            <div slot-scope="scope" class="d-flex">
              <i :class="renderOSIcon(scope.row.os)" />
              {{ scope.row.os }}
            </div>
          </el-table-column>
          <el-table-column
            align="left"
            :sortable="true"
            prop="tags"
            :label="$t('Tags')"
          >
            <div slot-scope="scope" class="d-flex">
              <el-tag
                v-for="tag in scope.row.tags"
                :key="tag"
                type="primary"
                size="mini"
                effect="dark"
                v-html="tag"
              />
            </div>
          </el-table-column>

          <el-table-column
            align="left"
            :sortable="true"
            prop="created_at"
            :label="$t('Created')"
          >
            <div slot-scope="scope" class="d-flex">
              <span v-html="renderDate(scope.row.created_at)" />
            </div>
          </el-table-column>

          <el-table-column
            align="left"
            :sortable="true"
            prop="last_seen"
            :label="$t('Last seen')"
          >
            <div slot-scope="scope" class="d-flex">
              <span v-html="renderDate(scope.row.last_seen)" />
            </div>
          </el-table-column>

          <el-table-column
            align="left"
            :sortable="true"
            prop="_id"
            :width="150"
            :label="$t('Actions')"
          >
            <div slot-scope="{ row }" class="d-flex">
              <el-popconfirm
                :confirm-button-text="$t('Delete')"
                :cancel-button-text="$t('Cancel')"
                icon="el-icon-info"
                icon-color="orange"
                popper-class="popover-delete"
                :title="$t('Are you sure to delete this?')"
                @confirm="deleteAgent(row)"
              >
                <el-button slot="reference" type="danger" size="mini">
                  <i class="fa fa-trash" />
                </el-button>
              </el-popconfirm>
            </div>
          </el-table-column>
        </template>
      </light-owl-table>
    </el-card>
  </div>
</template>

<script>
import LightOwlTable from "@/components/Table/index.vue"
import renderMixin from "@/mixins/renderMixin"
import EventBus from "@/event-bus"
import request from "@/utils/request"

export default {
  components: { LightOwlTable },
  mixins: [renderMixin],

  data: () => ({
    dialogAddAgentVisible: false,
    popovers: {},
    config: {},
    search: "",
    install_script: "",
    sortOrder: {
      prop: "hostname",
      order: "descending"
    }
  }),

  beforeMount() {
    request.get("/api/v1/config/").then((response) => {
      this.config = response.data
      this.install_script = `bash ./install_plateform ${this.config.ip_address} ${this.config.agent_token}`
    })
  },

  mounted() {
    EventBus.$on("reload", () => {
      this.refreshTable()
    })
  },

  methods: {
    onCopy() {
      this.$message({
        type: "info",
        message: this.$t("Agent token copied"),
        showClose: true
      })
    },

    refreshTable() {
      this.$refs.table.getData()
    },

    deleteAgent(data) {
      request.delete(`/api/v1/agents/${data._id}`).then(() => {
        this.refreshTable()
      })
    },

    openAgent(agent, column) {
      if (column.label !== "Actions") this.$router.push(`/agents/${agent._id}`)
    }
  }
}
</script>
