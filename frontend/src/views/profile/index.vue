<template>
  <div class="app-container">
    <el-row :gutter="20" justify="center">
      <el-col :xs="24" :sm="8" :md="8" :lg="8" :xl="6">
        <el-form label-position="right" @submit.prevent="saveProfile">
          <el-card
            class="box-card"
            :body-style="{ padding: '5px 10px 10px 10px' }"
          >
            <div slot="header" class="clearfix">
              <span>{{ $t("Edit Profile") }}</span>
              <el-button
                type="primary"
                :loading="loadingProfile"
                style="float: right"
                size="mini"
                @click.native.prevent="saveProfile"
              >
                <i class="fa fa-save" /> {{ $t("Save") }}
              </el-button>
            </div>
            <el-form-item class="mb-0" :label="$t('Username')">
              <el-input v-model="form.username" />
            </el-form-item>
            <el-form-item class="mb-0" :label="$t('Current password')">
              <el-input v-model="form.current_password" type="password" />
            </el-form-item>
            <el-form-item class="mb-0" :label="$t('New password')">
              <el-input v-model="form.new_password" type="password" />
            </el-form-item>
            <el-form-item class="mb-0" :label="$t('Confirm password')">
              <el-input v-model="form.confirm_password" type="password" />
            </el-form-item>
          </el-card>
        </el-form>
      </el-col>

      <el-col :xs="24" :sm="12" :md="16" :lg="16" :xl="12">
        <el-card class="box-card" :body-style="{ padding: '0' }">
          <div slot="header" class="clearfix">
            <span>{{ $t("API Keys") }}</span>
            <el-popover
              v-model="popoverAdd"
              placement="bottom"
              class="popover-no-padding"
              width="400"
              trigger="click"
            >
              <api-key
                @close="
                  popoverAdd = false;
                  refreshTable();
                "
              />
              <el-button
                slot="reference"
                type="primary"
                style="float: right"
                size="mini"
              >
                <i class="fa fa-plus" /> {{ $t("Add") }}
              </el-button>
            </el-popover>
          </div>
          <light-owl-table
            ref="table"
            uri="/api/v1/auth/apikey"
            :default-sort="sortOrder"
          >
            <template slot="columns">
              <el-table-column
                align="left"
                :sortable="true"
                prop="api_key"
                :label="$t('API Key')"
                :width="100"
              >
                <div slot-scope="{ row }" class="d-flex">
                  <el-tooltip
                    class="item"
                    effect="dark"
                    :content="$t('Copy API Key')"
                    placement="top"
                  >
                    <el-button
                      v-clipboard:copy="row.api_key"
                      v-clipboard:success="onCopy"
                      type="primary"
                      size="mini"
                    >
                      <i class="fa fa-copy" />
                    </el-button>
                  </el-tooltip>
                </div>
              </el-table-column>

              <el-table-column
                align="left"
                :sortable="true"
                prop="created_at"
                :label="$t('Created at')"
              >
                <div slot-scope="{ $index, row }" class="d-flex">
                  <span v-html="renderDate(row.created_at)" />
                </div>
              </el-table-column>
              <el-table-column
                align="left"
                :sortable="true"
                prop="expire"
                :label="$t('Expire')"
              >
                <div slot-scope="{ $index, row }" class="d-flex">
                  <i :class="row.expire ? 'fa fa-check' : 'fa fa-times'" />
                </div>
              </el-table-column>

              <el-table-column
                align="left"
                :sortable="true"
                prop="expire_at"
                :label="$t('Expire at')"
              >
                <div slot-scope="{ $index, row }" class="d-flex">
                  <span v-if="row.expire">{{ row.expire_at }}</span>
                  <span v-else>N/A</span>
                </div>
              </el-table-column>

              <el-table-column
                align="left"
                :sortable="true"
                prop="_id"
                :width="150"
                :label="$t('Actions')"
              >
                <div slot-scope="{ $index, row }" class="d-flex">
                  <el-popconfirm
                    :confirm-button-text="$t('Delete')"
                    :cancel-button-text="$t('Cancel')"
                    icon="el-icon-info"
                    icon-color="orange"
                    popper-class="popover-delete"
                    :title="$t('Are you sure to delete this?')"
                    @confirm="deleteApiKey(row)"
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
      </el-col>
    </el-row>
  </div>
</template>

<script>
import LightOwlTable from "@/components/Table/index.vue"
import renderMixin from "@/mixins/renderMixin"
import { updateProfile } from "@/api/user"
import request from "@/utils/request"
import ApiKey from "./ApiKey.vue"

export default {
  components: { LightOwlTable, ApiKey },
  mixins: [renderMixin],
  data: () => ({
    loadingProfile: false,
    popoverAdd: false,
    popovers: {},
    sortOrder: {
      prop: "created_at",
      order: "descending"
    },
    form: {
      username: "",
      current_password: "",
      new_password: "",
      confirm_password: ""
    }
  }),

  mounted() {
    this.$store.dispatch("user/getInfo").then((data) => {
      this.form.username = data.username
    })
  },

  methods: {
    refreshTable() {
      this.$refs.table.getData()
    },
    saveProfile() {
      this.loadingProfile = true
      updateProfile(this.form)
        .then(() => {
          this.loadingProfile = false
          this.$message({
            type: "success",
            message: this.$t("Profile successfully updated"),
            showClose: true
          })
        })
        .catch((err) => {
          if (err.response.status === 400) {
            const error = this.$t(err.response.data.detail)
            this.$message({
              type: "error",
              message: error,
              showClose: true
            })

            this.loadingProfile = false
          }
        })
    },

    deleteApiKey(data) {
      request.delete(`/api/v1/auth/apikey/${data._id}`).then((response) => {
        this.$message({
          type: "success",
          message: this.$t("API Key successfully deleted"),
          showClose: true
        })
        this.refreshTable()
      })
    },

    onCopy() {
      this.$message({
        type: "info",
        message: this.$t("API Key copied"),
        showClose: true
      })
    }
  }
}
</script>
<style>
</style>
