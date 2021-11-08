<template>
  <div :class="classObj" class="app-wrapper">
    <div
      v-if="device === 'mobile' && sidebar.opened"
      class="drawer-bg"
      @click="handleClickOutside"
    />
    <sidebar class="sidebar-container" />
    <div class="main-container">
      <div :class="{ 'fixed-header': fixedHeader }">
        <navbar />
      </div>
      <app-main />
    </div>
  </div>
</template>

<script>
import { Navbar, Sidebar, AppMain } from "./components"
import ResizeMixin from "./mixin/ResizeHandler"
import { getToken } from "@/utils/auth"
import EventBus from "@/event-bus"

export default {
  name: "Layout",
  components: {
    Navbar,
    Sidebar,
    AppMain
  },
  mixins: [ResizeMixin],

  data: () => ({
    message: null
  }),

  computed: {
    sidebar() {
      return this.$store.state.app.sidebar
    },
    device() {
      return this.$store.state.app.device
    },
    fixedHeader() {
      return this.$store.state.settings.fixedHeader
    },
    classObj() {
      return {
        hideSidebar: !this.sidebar.opened,
        openSidebar: this.sidebar.opened,
        withoutAnimation: this.sidebar.withoutAnimation,
        mobile: this.device === "mobile"
      }
    }
  },

  beforeDestroy() {
    if (this.message) this.message.close()
  },

  mounted() {
    this.initWebSocket()

    // TODO: REMOVE
    setTimeout(() => {
      EventBus.$emit("alert")
    }, 2000)
  },

  methods: {
    handleClickOutside() {
      this.$store.dispatch("app/closeSideBar", { withoutAnimation: false })
    },

    async initWebSocket() {
      const mapping = {
        5: "info",
        4: "info",
        3: "warning",
        2: "warning",
        1: "error"
      }

      const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws"
      const ws_address = `${ws_scheme}://${location.hostname}/dashboard`

      this.ws = new WebSocket(ws_address)

      this.ws.onopen = () => {
        this.ws.send(getToken())
      }

      this.ws.onmessage = (event) => {
        if (event === "null") return
        const data = JSON.parse(event.data)
        if (data.measurements) {
          EventBus.$emit("measurements", data.measurements)
        } else if (data.alerts) {
          for (const alert of data.alerts) {
            const agent_link = `<a href='/#/agents/${alert.agent_id}/?panel=alerts'>${this.$t("Link")}</a>`
            if (this.message) this.message.close()

            EventBus.$emit("alert")
            this.message = this.$message({
              duration: 20000,
              showClose: true,
              type: mapping[alert.priority],
              dangerouslyUseHTMLString: true,
              message: `<p>${this.$t("New alert on agent")}: <b>${alert.agent}</b></p><p>${this.$t("Rule")}: <b>${alert.rule}</b></p><p>${agent_link}</p>`
            })
            EventBus.$emit("reload")
          }
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/styles/mixin.scss";
@import "~@/styles/variables.scss";

.app-wrapper {
  @include clearfix;
  position: relative;
  height: 100%;
  width: 100%;
  &.mobile.openSidebar {
    position: fixed;
    top: 0;
  }
}
.drawer-bg {
  background: #000;
  opacity: 0.3;
  width: 100%;
  top: 0;
  height: 100%;
  position: absolute;
  z-index: 999;
}

.fixed-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9;
  width: calc(100% - #{$sideBarWidth});
  transition: width 0.28s;
}

.hideSidebar .fixed-header {
  width: calc(100% - 54px);
}

.mobile .fixed-header {
  width: 100%;
}
</style>
