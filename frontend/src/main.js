import Vue from "vue"
import i18n from "./plugins/i18n"

import "normalize.css/normalize.css" // A modern alternative to CSS resets

import ElementUI from "element-ui"
import VueClipboard from "vue-clipboard2"

import "element-ui/lib/theme-chalk/index.css"
import locale from "element-ui/lib/locale/lang/en" // lang i18n
import "@fortawesome/fontawesome-free/css/all.css"
import "@fortawesome/fontawesome-free/js/all.js"

// import socketio from 'socket.io';
// import VueSocketIO from 'vue-socket.io';

import "@/assets/css/style.css"
import "@/styles/element-variables.scss"
import "@/styles/index.scss" // global css

import App from "./App"
import store from "./store"
import router from "./router"

import "@/icons" // icon
import "@/permission" // permission control

// const SocketInstance = socketio("wss://127.0.0.1:8000/ws");
// Vue.use(VueSocketIO, SocketInstance)

// set ElementUI lang to EN
Vue.use(ElementUI, { locale })
Vue.use(VueClipboard)

Vue.config.productionTip = false

new Vue({
  el: "#app",
  router,
  store,
  i18n,
  render: (h) => h(App)
})
