<template>
  <div class="home">
    <el-container>
      <el-header>
        <h1>ERP System</h1>
      </el-header>
      <el-main>
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Ласкаво просимо!</span>
            </div>
          </template>
          <el-alert
            title="Проект успішно створено"
            type="success"
            description="Backend і Frontend готові до розробки. Запустіть 'docker-compose up --build' для старту."
            show-icon
            :closable="false"
          />
          
          <div class="info-section">
            <h3>Наступні кроки:</h3>
            <ol>
              <li>Налаштувати автентифікацію</li>
              <li>Створити реєстрацію компанії</li>
              <li>Додати користувачів</li>
              <li>Розробити основні модулі</li>
            </ol>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
// Home page
</script>

<style scoped>
.home {
  width: 100%;
  height: 100vh;
}

.el-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.el-main {
  padding: 20px;
}

.info-section {
  margin-top: 20px;
}

.info-section h3 {
  margin-bottom: 10px;
  color: #303133;
}

.info-section ol {
  margin-left: 20px;
}

.info-section li {
  margin: 8px 0;
  color: #606266;
}
</style>
