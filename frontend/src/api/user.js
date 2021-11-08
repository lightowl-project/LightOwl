import request from "@/utils/request"

export function login(data) {
  const formData = new FormData()
  formData.append("username", data.username)
  formData.append("password", data.password)

  const headers = { "Content-Type": "application/x-www-form-urlencoded" }
  return request.post("/api/v1/auth/token", formData, headers)
}

export function updateProfile(data) {
  return request({
    url: "/api/v1/auth/profile",
    method: "put",
    data
  })
}

export function getInfo() {
  return request({
    url: "/api/v1/auth/profile",
    method: "get"
  })
}

// export function logout() {
//   return request({
//     url: "/vue-admin-template/user/logout",
//     method: "post"
//   })
// }
