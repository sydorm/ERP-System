<template>
  <router-view />
</template>

<script setup>
// Root App component
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', 'Segoe UI', sans-serif;
  background-color: var(--erp-bg-page);
  color: var(--erp-text-main);
}

#app {
  width: 100%;
  height: 100vh;
}
</style>
