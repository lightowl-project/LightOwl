<template>
  <div class="">
    <span v-for="level in [5, 4, 3, 2, 1]" :key="level">
      <el-popover
        v-if="alerts_mapping[level] > 0"
        placement="bottom-start"
        width="1500"
        trigger="click"
      >
        <alert-list :agent_id="agent_id" :priority="level" />
        <div slot="reference" class="alert-info-tag">
          <el-tooltip :content="renderTooltip(level)" placement="bottom-start">
            <el-button size="mini" :class="renderButtonAlertClass(level)" style="margin-right: 5px">
              <i :class="renderIconAlert(level)" />
              <b>{{ alerts_mapping[level] }}</b>
            </el-button>
          </el-tooltip>
        </div>
      </el-popover>
    </span>
  </div>
</template>

<script>
import { defineComponent } from "@vue/composition-api"
import AlertList from "@/components/AlertList.vue"

export default defineComponent({
  components: { AlertList },
  props: {
    alerts: {
      type: Array,
      required: true
    },
    agent_id: {
      type: String,
      required: true
    }
  },

  data: () => ({
    link_to: "",
    alerts_mapping: {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
      5: 0
    }
  }),

  watch: {
    alerts() {
      this.constructAlertMapping()
    }
  },

  mounted() {
    this.link_to = `/agents/${this.agent_id}`
    this.constructAlertMapping()
  },

  methods: {
    constructAlertMapping() {
      const alert_mapping = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
      for (const alert of this.alerts) {
        alert_mapping[alert.priority] += 1
      }

      this.alerts_mapping = alert_mapping
    },

    renderButtonAlertClass(level) {
      const mapping = {
        5: "info",
        4: "low",
        3: "medium",
        2: "high",
        1: "critical"
      }

      return `alert-icon-${mapping[level]}`
    },

    renderIconAlert(level) {
      const mapping = {
        5: "question-circle",
        4: "exclamation-circle",
        3: "exclamation-circle",
        2: "exclamation-triangle",
        1: "exclamation-triangle"
      }

      return `fa fa-${mapping[level]} alert-info-icon`
    },

    renderTooltip(level) {
      const mapping = {
        5: this.$t("Info"),
        4: this.$t("Low"),
        3: this.$t("Medium"),
        2: this.$t("High"),
        1: this.$t("Critical")
      }

      return `${this.$t("Alert")}(s) ${mapping[level]}`
    }
  }
})
</script>
