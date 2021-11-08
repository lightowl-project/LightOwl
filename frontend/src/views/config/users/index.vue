<template>
  <div class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#F58320"
    >
      <el-menu-item index="1" route="/users/">
        <i class="fa fa-users mr-1" />{{ $t("Users") }}
      </el-menu-item>

      <el-menu-item
        index="2"
        style="float: right"
        @click="dialogUserVisible = true"
      >
        <i class="fa fa-plus" /> {{ $t("Add") }}
      </el-menu-item>
    </el-menu>

    <el-dialog
      :title="$t('Add an user')"
      width="30%"
      :visible.sync="dialogUserVisible"
    >
      <div slot="header" />
      <el-row>
        <el-form ref="form" :model="form" label-width="150px">
          <el-form-item :label="$t('Username')">
            <el-input v-model="form.username" />
          </el-form-item>
          <el-form-item :label="$t('Password')">
            <el-input v-model="form.password" type="password" />
          </el-form-item>
          <el-form-item :label="$t('Confirm password')">
            <el-input
              v-model="form.confirm_password"
              type="password"
            />
          </el-form-item>
        </el-form>
      </el-row>
      <el-row class="text-center mt-2">
        <el-button type="warning" plain @click="closeDialog()">
          {{ $t("Cancel") }}
        </el-button>
        <el-button type="primary" @click="saveUser()">
          {{ $t("Save") }}
        </el-button>
      </el-row>
    </el-dialog>

    <el-card :body-style="{margin: 0, padding: 0}" class="no-border">
      <light-owl-table
        ref="table"
        uri="/api/v1/auth/users"
        :default-sort="sortOrder"
      >
        <template slot="columns">
          <el-table-column
            align="left"
            :sortable="true"
            prop="username"
            :label="$t('Username')"
          />

          <el-table-column
            align="left"
            :sortable="true"
            prop="disabled"
            :label="$t('Disabled')"
          >
            <div slot-scope="scope" class="d-flex">
              <span v-if="scope.row.disabled">
                <i class="fa fa-check" />
                <el-popconfirm
                  :confirm-button-text="$t('Enable')"
                  :cancel-button-text="$t('Cancel')"
                  icon="el-icon-info"
                  icon-color="orange"
                  popper-class="popover-delete"
                  :title="$t('Enable this user ?')"
                  @confirm="updateUser(scope.row._id, false)"
                >
                  <el-button
                    slot="reference"
                    style="float: right"
                    type="success"
                    size="mini"
                  >
                    <i class="fa fa-lock-open" />
                  </el-button>
                </el-popconfirm>
              </span>
              <span v-else>
                <i class="fa fa-times" />

                <el-popconfirm
                  :confirm-button-text="$t('Disable')"
                  :cancel-button-text="$t('Cancel')"
                  icon="el-icon-info"
                  icon-color="orange"
                  popper-class="popover-delete"
                  :title="$t('Disable this user ?')"
                  @confirm="updateUser(scope.row._id, true)"
                >
                  <el-button
                    slot="reference"
                    style="float: right"
                    type="warning"
                    size="mini"
                  >
                    <i class="fa fa-lock" />
                  </el-button>
                </el-popconfirm>
              </span>
            </div>
          </el-table-column>

          <el-table-column
            align="left"
            :sortable="true"
            prop="first_seen"
            :label="$t('Created')"
          >
            <div slot-scope="scope" class="d-flex">
              <span v-html="renderDate(scope.row.first_seen)" />
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
                @confirm="deleteUser(row)"
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
import request from "@/utils/request"

export default {
  components: { LightOwlTable },
  mixins: [renderMixin],

  data: () => ({
    dialogUserVisible: false,
    popovers: {},
    sortOrder: {
      prop: "hostname",
      order: "descending"
    },
    form: {
      username: "",
      password: "",
      confirm_password: ""
    }
  }),

  mounted() {},

  methods: {
    refreshTable() {
      this.$refs.table.getData()
    },

    deleteUser(data) {
      request.delete(`/api/v1/auth/users/${data._id}`).then(() => {
        this.refreshTable()

        this.$message({
          type: "success",
          message: this.$t("User successfully deleted"),
          showClose: true
        })
      }).catch((err) => {
        this.$message({
          type: "error",
          message: err.response.data.detail,
          showClose: true
        })
      })
    },

    closeDialog() {
      this.form = {
        username: "",
        password: "",
        confirm_password: ""
      }
      this.dialogUserVisible = false
      this.refreshTable()
    },

    updateUser(user_id, disabled) {
      request
        .post(`/api/v1/auth/users/${user_id}/update`, { disabled: disabled })
        .then((response) => {
          this.$message({
            type: "success",
            message: this.$t("User successfully updated"),
            showClose: true
          })

          this.refreshTable()
        })
        .catch((err) => {
          this.$message({
            type: "error",
            message: err.response.data.detail,
            showClose: true
          })
        })
    },

    saveUser() {
      const data = {
        username: this.form.username,
        password: this.form.password,
        confirm_password: this.form.confirm_password
      }

      request
        .post("/api/v1/auth/users", data)
        .then((response) => {
          this.closeDialog()
          this.$message({
            type: "success",
            message: this.$t("User successfully created"),
            showClose: true
          })
        })
        .catch((err) => {
          this.$message({
            type: "error",
            message: err.response.data.detail,
            showClose: true
          })
        })
    }
  }
}
</script>
