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
      <el-menu-item index="1" route="/inputs/">
        <i class="fa fa-download mr-1" />{{ $t("Inputs") }}
      </el-menu-item>

      <el-menu-item index="2" style="float: right" route="/inputs/create">
        <i class="fa fa-plus" /> {{ $t("Add") }}
      </el-menu-item>
    </el-menu>

    <light-owl-table
      ref="table"
      uri="/api/v1/inputs/"
      :default-sort="sortOrder"
    >
      <template slot="columns">
        <el-table-column
          align="left"
          :sortable="true"
          prop="name"
          :label="$t('Name')"
        />

        <el-table-column
          align="left"
          :sortable="true"
          prop="plugin_name"
          :label="$t('Plugin')"
        />

        <el-table-column
          align="left"
          :sortable="true"
          prop="created_at"
          :label="$t('Created')"
        >
          <div slot-scope="{ $index, row }" class="d-flex">
            <span v-html="renderDate(row.created_at)" />
          </div>
        </el-table-column>

        <el-table-column
          align="left"
          :sortable="true"
          prop="updated_at"
          :label="$t('Updated')"
        >
          <div slot-scope="{ row }" class="d-flex">
            <span v-html="renderDate(row.updated_at)" />
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
            <router-link :to="constructURI(row)" class="mr-1">
              <el-button type="primary" size="mini">
                <i class="fa fa-edit" />
              </el-button>
            </router-link>
            <el-popconfirm
              :confirm-button-text="$t('Delete')"
              :cancel-button-text="$t('Cancel')"
              icon="el-icon-info"
              icon-color="orange"
              popper-class="popover-delete"
              :title="$t('Are you sure to delete this?')"
              @confirm="deleteInput(row)"
            >
              <el-button slot="reference" type="danger" size="mini">
                <i class="fa fa-trash" />
              </el-button>
            </el-popconfirm>
          </div>
        </el-table-column>
      </template>
    </light-owl-table>
  </div>
</template>

<script>
import LightOwlTable from "@/components/Table/index.vue"
import renderMixin from "@/mixins/renderMixin"
import request from "@/utils/request"

export default {
  components: { LightOwlTable },
  mixins: [renderMixin],

  data: () => ({
    popovers: {},
    sortOrder: {
      prop: "name",
      order: "descending"
    }
  }),

  mounted() {},

  methods: {
    refreshTable() {
      this.$refs.table.getData()
    },

    constructURI(data) {
      return `/inputs/edit/${data._id}`
    },

    deleteInput(data) {
      request.delete(`/api/v1/inputs/${data._id}`).then(() => {
        this.$message({
          type: "success",
          message: this.$t("Input successfully deleted"),
          showClose: true
        })

        this.refreshTable()
      })
    }
  }
}
</script>
