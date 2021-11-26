<template>
  <el-card class="no-border" :body-style="{padding: '5px 10px'}">
    <el-row style="text-align: right; margin-bottom: 10px">
      <el-button
        size="mini"
        type="primary"
        style="margin-right: 10px"
        :loading="isLoadingRet"
        @click="applyRetentionPolicy()"
      >
        <i class="fa fa-bolt" /> {{ $t("Apply") }}
      </el-button>
    </el-row>
    <el-row>
      <el-form label-position="right" label-width="120px">
        <el-form-item :label="$t('Duration')">
          <el-select
            v-model="retention_duration"
            style="width: 100%"
            placeholder="Select"
          >
            <el-option :label="$t('1 day')" value="1d" />
            <el-option :label="$t('2 day')" value="2d" />
            <el-option :label="$t('3 day')" value="3d" />
            <el-option :label="$t('4 day')" value="4d" />
            <el-option :label="$t('1 week')" value="1w" />
            <el-option :label="$t('2 week')" value="2w" />
            <el-option :label="$t('3 week')" value="3w" />
            <el-option :label="$t('4 week')" value="4w" />
            <el-option :label="$t('3 month')" value="12w" />
          </el-select>
          <small
            v-html="$t('Set the default retention policy for all metrics')"
          />
        </el-form-item>
      </el-form>
    </el-row>
  </el-card>
</template>

<script>
import request from "@/utils/request"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  data: () => ({
    retention_duration: "",
    isLoadingRet: false
  }),

  beforeMount() {
    request.get("/api/v1/config/").then((response) => {
      this.retention_duration = response.data.retention_duration
    })
  },

  methods: {
    applyRetentionPolicy() {
      this.isLoadingRet = true
      const data = {
        retention_duration: this.retention_duration
      }

      request
        .post("/api/v1/config/retention", data)
        .then(() => {
          this.$message({
            type: "success",
            message: this.$t("Retention successfully applied"),
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
        .then(() => {
          this.isLoadingRet = false
        })
    }
  }
})
</script>
