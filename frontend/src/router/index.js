import Vue from "vue"
import Router from "vue-router"

Vue.use(Router)

/* Layout */
import Layout from "@/layout"

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: "/login",
    component: () => import("@/views/login/index"),
    hidden: true
  },

  {
    path: "/404",
    component: () => import("@/views/404"),
    hidden: true
  },

  {
    path: "/",
    component: Layout,
    meta: { title: "Dashboard", icon: "dashboard" },
    children: [{
      path: "",
      name: "Home",
      meta: { title: "Home", icon: "fa fa-home" },
      component: () => import("@/views/dashboard/Home")
    }]
  },
  {
    path: "/agents",
    component: Layout,
    meta: { title: "Agents", icon: "fa fa-server" },
    children: [{
      path: "",
      name: "Agents",
      component: () => import("@/views/agent/index"),
      hidden: true
    }, {
      path: ":id?",
      name: "Agent",
      foo: "bar",
      component: () => import("@/views/agent/Agent"),
      hidden: true
    }]
  },
  {
    path: "/alerts",
    component: Layout,
    meta: { title: "Alerts", icon: "fa fa-bell" },
    children: [{
      path: "",
      name: "Alerts",
      component: () => import("@/views/alert/index"),
      hidden: true
    }]
  },
  {
    path: "/rules",
    component: Layout,
    meta: { title: "Rules", icon: "el-icon-s-claim" },
    children: [{
      path: "",
      name: "Rules",
      component: () => import("@/views/rules/index"),
      hidden: true
    },
    {
      path: "create",
      name: "Create Rule",
      component: () => import("@/views/rules/EditRule"),
      hidden: true
    }]
  },
  {
    path: "/viewer/",
    component: Layout,
    meta: { title: "Viewer", icon: "el-icon-view" },
    children: [{
      path: "",
      name: "Viewer",
      component: () => import("@/views/viewer/index"),
      hidden: true
    }, {
      path: ":alert_id?",
      component: () => import("@/views/viewer/index"),
      hidden: true
    }]
  },
  {
    path: "/config",
    component: Layout,
    meta: { title: "Administration", icon: "el-icon-s-tools" },
    children: [{
      path: "",
      name: "Parameters",
      component: () => import("@/views/config/parameters/index"),
      meta: { title: "Parameters", icon: "el-icon-setting" }
    }, {
      path: "/users",
      name: "Users",
      component: () => import("@/views/config/users/index"),
      meta: { title: "Users", icon: "el-icon-user-solid" }
    }]
  },
  {
    path: "/profile",
    component: Layout,
    hidden: true,
    children: [{
      path: "",
      name: "Profile",
      component: () => import("@/views/profile/index"),
      meta: { title: "Profile", icon: "user" }
    }]
  },
  // 404 page must be placed at the end !!!
  { path: "*", redirect: "/404", hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
