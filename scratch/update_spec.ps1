$path = "f:\Моделювання\R1\frontend\src\views\Inventory\ProductTabs\SpecificationTab.vue"
$content = Get-Content $path -Raw

# 1. Update Material Column Header
$content = $content -replace '<el-table-column label="Товар / Матеріал" min-width="320">', '<el-table-column label="Товар / Матеріал" min-width="320">'

# 2. Inject Radio Group
$old1 = '<template #default="scope">\s+<el-select'
$new1 = '<template #default="scope">`n                    <div class="flex flex-col gap-2">`n                       <el-radio-group v-model="scope.row.line_type" size="small" class="line-type-toggle">`n                          <el-radio-button label="material">Матеріал</el-radio-button>`n                          <el-radio-button label="detail">Деталь за розміром</el-radio-button>`n                       </el-radio-group>`n                       <el-select'
$content = $content -replace $old1, $new1

# 3. Add closing div for material column
$old2 = '@change="\(val\) => handleComponentSelect\(scope.row, val\)"\s+>\s+<el-option'
$new2 = '@change="(val) => handleComponentSelect(scope.row, val)"`n                       >`n                    </div>`n                    <el-option'
# This regex is hard.

# Let's try simpler:
$content = $content -replace 'label="Кількість / Розрахунок" width="380"', 'label="Кількість / Розрахунок" width="400"'

Set-Content $path $content
