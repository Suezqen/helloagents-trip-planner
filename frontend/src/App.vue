<template>
  <div id="app">
    <a-layout class="app-shell">
      <a-layout-header class="app-header">
        <div class="brand-block">
          <span class="brand-eyebrow">Multi-Agent Trip Planner</span>
          <div class="brand-title">HelloAgents 智能旅行助手</div>
        </div>
      </a-layout-header>
      <a-layout-content class="app-content">
        <router-view />
      </a-layout-content>
      <a-layout-footer class="app-footer">
        整理版项目仓库，保留多 Agent 协作流程与地图能力接入链路
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
:root {
  color-scheme: light;
  --app-ink: #17324d;
  --app-brand: #1a6b70;
  --app-brand-deep: #0f3f49;
  --app-surface: #f7f4ee;
}

body {
  margin: 0;
  background: var(--app-surface);
}

#app {
  font-family: 'Avenir Next', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  color: var(--app-ink);
}

.app-shell {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  padding: 0 40px;
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.18), transparent 32%),
    linear-gradient(110deg, var(--app-brand-deep), var(--app-brand));
  box-shadow: 0 14px 32px rgba(15, 63, 73, 0.22);
}

.brand-block {
  color: #fff;
}

.brand-eyebrow {
  display: block;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  opacity: 0.78;
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
}

.app-content {
  padding: 0;
}

.app-footer {
  text-align: center;
  color: rgba(23, 50, 77, 0.78);
  background: transparent;
  padding: 18px 24px 24px;
}
</style>
