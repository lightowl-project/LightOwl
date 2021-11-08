<template>
  <div class="app-container">
    <el-row :gutter="20" justify="center">
      <el-card class="box-card" :body-style="{ padding: '0' }">
        <div slot="header" class="clearfix">
          <span>{{ $t("Plugins") }}</span>
          <router-link to="/plugins/edit">
            <el-button type="primary" style="float: right" size="mini">
              <i class="fa fa-plus" /> {{ $t("Add") }}
            </el-button>
          </router-link>
        </div>
        <light-owl-table
          ref="table"
          uri="/api/v1/plugins/"
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
              prop="plugin_type"
              :label="$t('Type')"
            />

            <el-table-column
              align="right"
              :sortable="true"
              prop="_id"
              :width="150"
              :label="$t('Actions')"
            >
              <div slot-scope="{ $index, row }" class="d-flex">
                <router-link :to="constructURI(row)" class="mr-1">
                  <el-button type="primary" size="mini">
                    <i class="fa fa-edit" />
                  </el-button>
                </router-link>
                <el-popover
                  v-model="popovers[row._id]"
                  placement="bottom"
                  :title="$t('Are you sure to delete this ?')"
                  :width="260"
                  trigger="click"
                >
                  <el-button
                    :outline="true"
                    type="primary"
                    size="mini"
                    @click="popovers[row._id] = false"
                  >
                    {{ $t("Cancel") }}
                  </el-button>
                  <el-button
                    :outline="true"
                    class="float-right"
                    type="danger"
                    style="float: right"
                    size="mini"
                    @click="deletePlugin(row)"
                  >
                    {{ $t("Delete") }}
                  </el-button>
                  <el-button slot="reference" type="danger" size="mini">
                    <i class="fa fa-trash" />
                  </el-button>
                </el-popover>
              </div>
            </el-table-column>
          </template>
        </light-owl-table>
      </el-card>
    </el-row>
  </div>
</template>

<script>
import LightOwlTable from "@/components/Table/index.vue"

export default {
  components: { LightOwlTable },
  data: () => ({
    popovers: {},
    sortOrder: {
      prop: "created_at",
      order: "descending"
    }
  }),

  mounted() {},

  methods: {
    refreshTable() {
      this.$refs.table.getData()
    },

    constructURI(data) {
      return `/plugins/edit/${data._id}`
    },

    deletePlugin(data) {}
  }
}
</script>
