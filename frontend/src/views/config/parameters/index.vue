<template>
  <div class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#F58320"
    >
      <el-menu-item index="1" route="/config/">
        <i class="el-icon-s-tools" />{{ $t("Parameters") }}
      </el-menu-item>
    </el-menu>

    <el-tabs tab-position="top" type="border-card">
      <el-tab-pane>
        <span slot="label">
          <i class="el-icon-message mr-1" />{{ $t("Mail") }}
        </span>
        <mail />
      </el-tab-pane>
      <el-tab-pane>
        <span slot="label">
          <i class="el-icon-odometer mr-1" />{{ $t("Retention") }}
        </span>
        <retention />
      </el-tab-pane>
      <!-- <el-tab-pane>
        <span slot="label">
          <i class="el-icon-position mr-1" />{{ $t("Twilio") }}
        </span>
        <twilio />
      </el-tab-pane> -->
    </el-tabs>
  </div>
</template>

<script>
import Mail from "./components/Mail.vue"
import Twilio from "./components/Twilio.vue"
import Retention from "./components/Retention.vue"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  components: { Mail, Retention, Twilio },
  data: () => ({
    retention_duration: "",
    mail: {},
    twilio: {}
  }),

  beforeMount() {
    // request.get("/api/v1/config").then((response) => {
    //   this.retention_duration = response.data.config.retention_duration;
    //   this.twilio = response.data.twilio;
    //   this.mail = response.data.mail;
    // });
  },

  methods: {}
})
</script>
