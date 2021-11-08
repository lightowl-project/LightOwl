<template>
  <el-form @submit.prevent="saveApiKey">
    <el-card class="">
      <div slot="header" class="clearfix">
        <span> {{ $t("Create an API Key") }}</span>
        <el-button
          type="primary"
          :loading="loading"
          style="float: right"
          size="mini"
          @click.native.prevent="saveApiKey"
        >
          {{ $t("Create") }}
        </el-button>
      </div>
      <el-form-item class="mb-0" :label="$t('Expire')">
        <el-switch v-model="form.expire" />
      </el-form-item>
      <el-form-item
        v-if="form.expire"
        class="mb-0"
        :label="$t('Expiration date')"
      >
        <el-date-picker
          v-model="form.expire_at"
          type="date"
          format="yyyy-MM-DD"
        />
      </el-form-item>
    </el-card>
  </el-form>
</template>

<script>
import request from "@/utils/request"
import moment from "moment"

export default {
  name: "ApiKey",
  data: () => ({
    loading: false,
    form: {
      expire: false,
      expire_at: new moment().add(3, "month").format("YYYY-MM-DD")
    }
  }),

  methods: {
    saveApiKey() {
      request.post("/api/v1/auth/apikey", this.form).then((response) => {
        this.$message({
          type: "success",
          message: this.$t("API Key successfully created"),
          showClose: true
        })
        this.$emit("close")
      })
    }
  }
}
</script>
