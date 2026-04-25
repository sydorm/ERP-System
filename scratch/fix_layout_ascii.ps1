$path = "f:\Моделювання\R1\frontend\src\views\Inventory\ProductTabs\SpecificationTab.vue"
$content = Get-Content $path
# Line 85 is index 84
$content[84] = '                 <template #default="scope"><div class="flex flex-col gap-2"><el-radio-group v-model="scope.row.line_type" size="small" class="line-type-toggle"><el-radio-button label="material">MATERIAL</el-radio-button><el-radio-button label="detail">DETAIL</el-radio-button></el-radio-group>'
# Line 113 is index 112
$content[112] = '                   </el-select></div>'
$content | Set-Content $path
