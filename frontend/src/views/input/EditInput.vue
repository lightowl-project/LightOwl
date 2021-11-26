<template>
  <el-row>
    <el-steps :active="step" align-center>
      <el-step :title="$t('Select Plugin')" />
      <el-step :title="$t('Configure')" />
    </el-steps>

    <div v-if="step === 1">
      <el-row class="mt-3">
        <div ref="pluginContainer">
          <span v-for="item in pluginChoices" :key="item.key">
            <el-card
              v-if="ignored_plugins.indexOf(item.title.toLowerCase()) === -1"
              class="box-card no-round card-plugin"
              shadow="hover"
              :style="renderStyle()"
              :body-style="{
                padding: '5px 10px',
                'background-color': '#405672',
                height: '100%',
              }"
            >
              <div slot="header">
                <span>{{ item.title }}</span>
                <el-button
                  type="default"
                  size="mini"
                  style="float: right; margin-right: 5px; padding: 4px"
                  @click="
                    pluginName = item.title
                    step++
                  "
                >
                  {{ $t("Select") }}
                </el-button>
                <el-popover
                  placement="bottom"
                  :title="item.title"
                  width="500"
                  trigger="click"
                >
                  <p v-html="item.description" />
                  <el-button
                    slot="reference"
                    style="float: right; margin-right: 5px; padding: 4px"
                  >
                    <i class="fa fa-info-circle" />
                  </el-button>
                </el-popover>
              </div>
              <p class="text-center">
                <i v-if="item.icon" :class="renderIcon(item.icon, 'large')" />
                <img
                  v-else-if="item.img"
                  :width="item.img_size"
                  :src="renderImage(item.img)"
                >
              </p>
            </el-card>
          </span>
        </div>
      </el-row>
    </div>
    <div v-else-if="step === 2">
      <el-row v-if="pluginName" class="mt-2">
        <Plugin
          ref="plugin"
          :edit="inputId !== null"
          :plugin-config="pluginConfig"
          :plugin-name="pluginName"
          @finish="savePlugin"
          @back="back()"
        />
      </el-row>
    </div>
  </el-row>
</template>

<script>
import Plugin from "./plugin.vue"
import request from "@/utils/request"
import renderMixin from "@/mixins/renderMixin"

export default {
  components: { Plugin },
  mixins: [renderMixin],
  props: {
    agentId: {
      type: String,
      required: true
    },
    inputId: {
      type: String,
      default: null
    }
  },
  data: () => ({
    configFile: "",
    is_loading: false,
    id: null,
    cards: {},
    step: 1,
    pluginComponent: null,
    pluginChoices: [],
    pluginName: "",
    pluginConfig: {},
    ignored_plugins: [],
    finalConfiguration: {}
  }),

  watch: {
    step(val) {
      this.$nextTick(() => {
        this.$forceUpdate()
      })
    }
  },

  beforeMount() {
    this.getAgentInput()

    request.get("/api/v1/inputs/plugins").then((response) => {
      for (const data of response.data) {
        this.cards[data.key] = false
      }

      this.pluginChoices = response.data
    })

    if (this.inputId) {
      request.get(`/api/v1/inputs/${this.inputId}`).then((response) => {
        this.pluginName = response.data.plugin_name
        this.pluginConfig = response.data.config
        this.step++
      })
    }
  },

  methods: {
    back() {
      this.pluginName = ""
      this.step--
      setTimeout(() => {
        this.calculateFlipWidth()
      })
    },

    async getAgentInput() {
      const response = await request.get(`/api/v1/agents/inputs/${this.agentId}`)
      const ignored_plugins = []

      for (const plugin of response.data) {
        ignored_plugins.push(plugin.plugin_name)
      }

      this.ignored_plugins = ignored_plugins
    },

    calculateFlipWidth() {
      const windowSize = window.innerWidth
      let element_per_line = 5
      if (windowSize < 3000) element_per_line = 4
      if (windowSize < 2000) element_per_line = 3
      if (windowSize < 1300) element_per_line = 2
      if (windowSize < 1000) element_per_line = 1

      const element = this.$refs.pluginContainer
      if (element) {
        const width = `${element.clientWidth / element_per_line - 1}px`
        return width
      }
    },

    renderStyle() {
      return `
        width: ${this.calculateFlipWidth()};
        height: 150px;
        background-color: #304156;
        float: left;
        color: #fff;
      `
    },

    savePlugin(finalConfiguration) {
      const form = {
        agent_id: this.agentId,
        plugin_name: this.pluginName.toLowerCase(),
        config: finalConfiguration
      }

      if (!this.inputId) {
        request
          .post("/api/v1/inputs/", form)
          .then(() => {
            this.$message({
              type: "success",
              message: this.$t("Input successfully created"),
              showClose: true
            })

            this.$emit("pluginSaved")
          })
          .catch((err) => {
            if (err.response.status === 400) {
              if (err.response.data.detail === "UNIQUE") {
                const message =
                  this.$t("Input ") +
                  this.plugin_name +
                  " " +
                  this.$t("already exists")

                this.$message({
                  type: "error",
                  message: message,
                  showClose: true
                })
              }
            }
          })
      } else {
        request.put(`/api/v1/inputs/${this.inputId}`, form).then((response) => {
          this.$message({
            type: "success",
            message: this.$t("Input successfully updated"),
            showClose: true
          })

          this.$emit("pluginSaved")
        })
      }
    }
  }
}
</script>

<style >
.el-card__header {
  padding: 10px 20px;
}
</style>
