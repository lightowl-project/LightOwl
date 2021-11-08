<template>
  <div>
    <el-card class="no-border" :body-style="{padding: '5px 10px'}">
      <el-row style="text-align: right; margin-bottom: 10px">
        <el-button
          size="mini"
          type="success"
          @click="testMailDialog = true"
        >
          <i class="fa fa-bolt" /> {{ $t("Test") }}
        </el-button>
        <el-button
          size="mini"
          type="primary"
          style="margin-right: 10px"
          :loading="isLoadingMailSave"
          @click="saveMailSettings()"
        >
          <i class="fa fa-save" /> {{ $t("Save") }}
        </el-button>
      </el-row>
      <el-row>
        <el-form label-position="right" label-width="120px" :model="mail">
          <el-form-item :label="$t('SMTP Server')">
            <el-input v-model="mail.smtp_server" />
          </el-form-item>
          <el-form-item :label="$t('SMTP Port')">
            <el-input v-model="mail.smtp_port" type="number" />
          </el-form-item>
          <el-form-item :label="$t('SSL')">
            <el-switch v-model="mail.ssl" />
          </el-form-item>
          <el-form-item :label="$t('Authentication')">
            <el-switch v-model="mail.auth" />
          </el-form-item>
          <el-form-item v-if="mail.auth" :label="$t('Email address')">
            <el-input v-model="mail.email" type="email" />
          </el-form-item>
          <el-form-item v-if="mail.auth" :label="$t('Password')">
            <el-input v-model="mail.password" type="password" />
          </el-form-item>
        </el-form>
      </el-row>
    </el-card>
    <el-dialog
      :title="$t('Test Send Mail')"
      :visible.sync="testMailDialog"
      width="30%"
    >
      <el-form label-position="top">
        <el-form-item :label="$t('Send mail to')" label-width="100px">
          <el-input v-model="test_to" />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="testMailDialog = false">
          {{ $t("Cancel") }}
        </el-button>
        <el-button
          type="primary"
          :loading="isLoadingTestMail"
          @click="testMail()"
        >
          {{ $t("Test") }}
        </el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import request from "@/utils/request"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  data: () => ({
    isLoadingMailSave: false,
    isLoadingTestMail: false,
    testMailDialog: false,
    test_to: "",
    mail: {
      auth: false,
      smtp_server: "",
      smtp_port: 587,
      email: "",
      password: "",
      ssl: false
    }
  }),

  beforeMount() {
    request.get("/api/v1/config/mail").then((response) => {
      this.mail = response.data
    })
  },

  methods: {
    testMail() {
      this.isLoadingTestMail = true
      const data = Object.assign({}, this.mail)
      data.to = this.test_to

      request
        .post("/api/v1/config/test/mail", data)
        .then((response) => {
          this.$message({
            type: "success",
            message: this.$t("Mail successfully sent"),
            showClose: true
          })
          this.testMailDialog = false
        })
        .catch((err) => {
          if (err.response.status === 500) {
            this.$message({
              type: "error",
              message: err.response.data.detail,
              showClose: true
            })
          }
        })
        .then(() => {
          this.isLoadingTestMail = false
        })
    },

    saveMailSettings() {
      this.isLoadingMailSave = true
      request
        .post("/api/v1/config/mail", this.mail)
        .then(() => {
          this.$message({
            type: "success",
            message: this.$t("Mail Settings successfully saved"),
            showClose: true
          })
        })
        .catch((err) => {
          if (err.response.status === 400) {
            this.$message({
              type: "error",
              message: err.response.data.detail,
              showClose: true
            })
          }
        })
        .then(() => {
          this.isLoadingMailSave = false
        })
    }
  }
})
</script>
