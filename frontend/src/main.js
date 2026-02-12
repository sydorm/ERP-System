import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import uk from 'element-plus/dist/locale/uk.mjs'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Pinia store
app.use(createPinia())

// Router
app.use(router)

// Element Plus with Ukrainian locale
app.use(ElementPlus, { locale: uk })

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.mount('#app')
