<template>
  <div class="text-center">
    <el-row>
      <el-col :xl="22" style="float: left">
        <span v-for="level in [5, 4, 3, 2, 1]" :key="level">
          <el-popover
            v-if="alerts_mapping[level] > 0"
            placement="bottom-start"
            width="1500"
            trigger="click"
          >
            <alert-list :agent_id="agent_id" :priority="level" />
            <el-col slot="reference" :xl="4" class="alert-info-tag">
              <!-- <el-tooltip  :content="renderTooltip(level)" placement="bottom-start"> -->
              <i :class="renderIconAlert(level)" />
              <b>{{ alerts_mapping[level] }}</b>
              <!-- </el-tooltip> -->
            </el-col>
          </el-popover>
        </span>
      </el-col>

      <el-tooltip class="item" :content="$t('Show more')" placement="bottom-end" style="float: right">
        <router-link :to="link_to">
          <el-link size="medium" type="warning" style="float: right; margin-right: 10px" :underline="false">
            <i class="fa fa-arrow-circle-right fa-2x" />
          </el-link>
        </router-link>
      </el-tooltip>
    </el-row>
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
    alerts_mapping: {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
      5: 0
    },
    link_to: ""
  }),

  watch: {
    alerts() {
      this.alerts_mapping = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0
      }

      for (const alert of this.alerts) {
        this.alerts_mapping[alert.priority] += 1
      }
    }
  },

  mounted() {
    this.link_to = `/agents/${this.agent_id}`
  },

  methods: {
    renderIconAlert(level) {
      const mapping = {
        5: {
          icon: "question-circle",
          class: "info"
        },
        4: {
          icon: "exclamation-circle",
          class: "low"
        },
        3: {
          icon: "exclamation-circle",
          class: "medium"
        },
        2: {
          icon: "exclamation-triangle",
          class: "high"
        },
        1: {
          icon: "exclamation-triangle",
          class: "critical"
        }
      }

      return `fa fa-${mapping[level].icon} fa-2x mr-1 alert-icon-${mapping[level].class}`
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
