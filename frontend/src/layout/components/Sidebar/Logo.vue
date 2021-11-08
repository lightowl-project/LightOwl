<template>
  <div class="sidebar-logo-container" :class="{ collapse: collapse }">
    <transition name="sidebarLogoFade">
      <router-link
        v-if="collapse"
        key="collapse"
        class="sidebar-logo-link"
        to="/"
      >
        <img v-if="logo" :src="logo" class="sidebar-logo-small">
      </router-link>
      <router-link v-else key="expand" class="sidebar-logo-link" to="/">
        <img v-if="logo_full" :src="logo_full" class="sidebar-logo">
      </router-link>
    </transition>
  </div>
</template>

<script>
import EventBus from "@/event-bus"

export default {
  name: "SidebarLogo",
  props: {
    collapse: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    title: "LightOwl",
    logo: require("@/assets/img/logo/logo-white.png"),
    logo_full: require("@/assets/img/logo/logo-full-white.png")
  }),

  mounted() {
    EventBus.$on("alert", () => {
      this.logo = require("@/assets/img/logo/logo-red.png")
      this.logo_full = require("@/assets/img/logo/logo-full-red.png")

      setTimeout(() => {
        this.logo = require("@/assets/img/logo/logo-white.png")
        this.logo_full = require("@/assets/img/logo/logo-full-white.png")
      }, 5000)
    })
  }
}
</script>

<style lang="scss" scoped>
.sidebarLogoFade-enter-active {
  transition: opacity 1.5s;
}

.sidebarLogoFade-enter,
.sidebarLogoFade-leave-to {
  opacity: 0;
}

.sidebar-logo-container {
  position: relative;
  width: 100%;
  height: 50px;
  line-height: 50px;
  background: #2b2f3a;
  text-align: center;
  overflow: hidden;

  & .sidebar-logo-link {
    height: 100%;
    width: 100%;

    & .sidebar-logo-small {
      width: 100%;
      vertical-align: middle;
    }

    & .sidebar-logo {
      margin-left: 5px;
      width: 200px;
      vertical-align: middle;
      margin-right: 12px;
    }

    & .sidebar-title {
      display: inline-block;
      margin: 0;
      color: #fff;
      font-weight: 600;
      line-height: 50px;
      font-size: 14px;
      font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
      vertical-align: middle;
    }
  }

  &.collapse {
    .sidebar-logo {
      margin-right: 0px;
    }
  }
}
</style>
