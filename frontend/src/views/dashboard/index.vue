<template>
  <div class="dashboard-container">
    <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#F58320"
    >
      <el-menu-item index="1" style="padding-right: 5px;">
        <el-select v-model="selectedAgent" size="mini" :placeholder="$t('Add an agent')">
          <el-option
            v-for="item in agents"
            :key="item._id"
            :label="item.ip_address"
            :value="item._id"
          />
        </el-select>
      </el-menu-item>
      <el-menu-item v-if="selectedAgent" index="2" @click="addWidget">
        <i class="fa fa-plus" />
      </el-menu-item>
      <el-menu-item
        index="4"
        style="float: right"
        @click="saveGeneralDashboard()"
      >
        <i class="fa fa-save" />
      </el-menu-item>
    </el-menu>
    <grid-layout
      :layout.sync="widgets"
      :col-num="12"
      :row-height="30"
      :is-draggable="true"
      :is-resizable="true"
      :is-mirrored="false"
      :vertical-compact="true"
      :margin="[5, 5]"
      :use-css-transforms="true"
    >
      <grid-item
        v-for="(item, index) in widgets"
        :key="item.agent"
        :x="item.x"
        :y="item.y"
        :w="item.w"
        :h="item.h"
        :i="index"
      >
        <agent :ref="renderAgentRef(item.agent)" :agent_id="item.agent" />
      </grid-item>
    </grid-layout>
  </div>
</template>

<script>
import request from "@/utils/request"
import EventBus from "@/event-bus"
import Agent from "./components/Agent.vue"
import VueGridLayout from "vue-grid-layout"
import statsMixin from "@/mixins/statsMixin"
import renderMixin from "@/mixins/renderMixin"

export default {
  name: "Dashboard",

  components: {
    GridLayout: VueGridLayout.GridLayout,
    GridItem: VueGridLayout.GridItem,
    Agent
  },

  mixins: [renderMixin, statsMixin],

  data: () => ({
    selectedAgent: null,
    refresh: 10000,
    widgets: [],
    agents: [],
    ws: null
  }),

  beforeMount() {
    this.getGeneralDashboard()
  },

  beforeDestroy() {
    if (this.ws) {
      this.ws.close()
    }
  },

  mounted() {
    EventBus.$on("measurement", (data) => {
      data = JSON.parse(data)
      for (const body of data) {
        const measurement = body.measurement
        const agent_id = body.agent_id

        if (!this.$refs[this.renderAgentRef(agent_id)]) {
          return
        }

        if (measurement === "cpu") {
          const cpu = 100 - parseInt(body.tags.usage_idle)
          if (cpu) {
            this.$refs[this.renderAgentRef(agent_id)][0].agent_data.cpu = cpu
          }
        } else if (measurement === "mem") {
          const mem = parseInt(body.tags.used_percent)
          if (mem) {
            this.$refs[this.renderAgentRef(agent_id)][0].agent_data.mem = mem
          }
        } else if (measurement === "system") {
          const load = parseFloat(body.tags.load1)
          if (load) {
            this.$refs[this.renderAgentRef(agent_id)][0].agent_data.load = load.toFixed(2)
          }
        }
      }
    })
  },

  methods: {
    renderAgentRef(id) {
      return `agent-${id}`
    },

    getGeneralDashboard() {
      this.getAgents()
    },

    getAgents() {
      request
        .get("/api/v1/agents/", { params: { all: true }})
        .then((response) => {
          this.agents = response.data

          // TODO: REMOVE
          while (this.agents.length > 0) {
            this.selectedAgent = this.agents[0]._id
            this.addWidget()
          }
        })
    },

    addWidget() {
      const tmp = {
        w: 4,
        h: 6,
        x: (this.widgets.length * 4) % 12,
        y: this.widgets.length + 12,
        i: this.widgets.length,
        agent: this.selectedAgent
      }

      let i = 0
      for (i in this.agents) {
        if (this.agents[i]._id === this.selectedAgent) {
          break
        }
      }

      this.agents.splice(i, 1)
      this.widgets.push(tmp)
      this.selectedAgent = null
    },

    saveGeneralDashboard() {}
  }
}
</script>

<style lang="scss" scoped>
</style>
