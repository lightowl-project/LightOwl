<template>
  <el-card class="no-border" :body-style="{padding: '5px 10px'}">
    <el-row style="text-align: right; margin-bottom: 10px">
      <el-button
        size="mini"
        type="success"
        :loading="isLoadingTestTwilio"
        @click="testTwilio()"
      >
        <i class="fa fa-bolt" /> {{ $t("Test") }}
      </el-button>
      <el-button
        size="mini"
        type="primary"
        style="margin-right: 10px"
        :loading="isLoadingTwilioSave"
        @click="saveTwilioSettings()"
      >
        <i class="fa fa-save" /> {{ $t("Save") }}
      </el-button>
    </el-row>
    <el-row>
      <el-form label-position="right" label-width="120px" :model="twilio">
        <el-form-item :label="$t('Account SID')">
          <el-input v-model="twilio.account_sid" />
        </el-form-item>
        <el-form-item :label="$t('Auth Token')">
          <el-input v-model="twilio.auth_token" />
        </el-form-item>
        <el-form-item :label="$t('Number From')">
          <el-input v-model="twilio.number_from" />
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
    isLoadingTestTwilio: false,
    isLoadingTwilioSave: false,
    twilio: {
      account_sid: "",
      auth_token: "",
      number_from: ""
    }
  }),

  beforeMount() {
    request.get("/api/v1/config/twilio").then((response) => {
      this.twilio = response.data
    })
  },

  methods: {
    testTwilio() {
      this.isLoadingTestTwilio = true
      request
        .post("/api/v1/config/twilio/test", this.twilio)
        .then((response) => {
          this.$message({
            type: "success",
            message: this.$t("Valid Account SID and Auth Token"),
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
          this.isLoadingTestTwilio = false
        })
    },

    saveTwilioSettings() {
      this.isLoadingTwilioSave = true

      request
        .post("/api/v1/config/twilio", this.twilio)
        .then((response) => {
          this.$message({
            type: "success",
            message: this.$t("Twilio configuration saved"),
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
          this.isLoadingTwilioSave = false
        })
    }
  }
})
</script>
