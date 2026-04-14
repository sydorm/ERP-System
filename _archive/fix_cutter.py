import os

html_path = r"g:\Моделювання\R1\calculator-app\frontend\cutter.html"
css_path = r"g:\Моделювання\R1\calculator-app\frontend\cutter.css"
js_path = r"g:\Моделювання\R1\calculator-app\frontend\cutter.js"

with open(html_path, "r", encoding="utf-8") as f:
    text = f.read()

style_start = text.find("<style>")
style_end = text.find("</style>")
css_content = text[style_start + 7:style_end].strip()

script_start = text.find("<script>")
if text.find("<script>", script_start + 8) != -1:
    script_start = text.rfind("<script>") # usually it's the last script tag

script_end = text.find("</script>", script_start)
js_content = text[script_start + 8:script_end].strip()

# 1. Fix ptKey
js_content = js_content.replace("function ptKey(x, y, z) { return `${x},${y},${z}`; }", "")
js_content = js_content.replace("""function ptKey(x, y, z) {
            // Use mm precision for keys to avoid collisions
            return `${Math.round(x * gridScale)},${Math.round(y * gridScale)},${Math.round(z * gridScale)}`;
        }""", """function ptKey(x, y, z) {
            return `${x},${y},${z}`;
        }""")

# 2. Fix drawJoints gridScale bug
js_content = js_content.replace("const [gx, gy, gz] = key.split(',').map(Number).map(v => v / gridScale);", "const [gx, gy, gz] = key.split(',').map(Number);")

# 3. Fix sendToMetal
js_content = js_content.replace("""function sendToMetal() {
            const total = segments.reduce((s, seg) => s + segLengthCm(seg), 0);
            if (total <= 0) { alert('Немає ліній для надсилання!'); return; }
            window.open(`/metal.html?cut_length=${(total / 100).toFixed(3)}`, '_blank');
        }""", """function sendToMetal() {
            const totalMm = segments.reduce((s, seg) => s + segLengthMm(seg), 0);
            if (totalMm <= 0) { alert('Немає ліній для надсилання!'); return; }
            window.open(`/metal.html?cut_length=${(totalMm / 1000).toFixed(3)}`, '_blank');
        }""")

# 4. Fix generateCutPlan function
old_generate = """function generateCutPlan() {
            if (segments.length === 0) { alert('Намалюйте хоча б одну лінію!'); return; }

            const imgDataUrl = canvas.toDataURL('image/png');
            const profile = getProfileLabel();
            const CUT_LABELS = { straight: '90°', '45': '45°', T: 'T-прим.' };

            // Group by rounded mm
            const groups = {};
            let totalCm = 0;
            segments.forEach(seg => {
                const lenCm = segLengthCm(seg);
                totalCm += lenCm;
                const lenMm = Math.round(lenCm * 10);
                if (!groups[lenMm]) groups[lenMm] = { lenCm, qty: 0, seg };
                groups[lenMm].qty++;
            });

            let rowNum = 0;
            const rows = Object.values(groups).map(g => {
                const lenMm = Math.round(g.lenCm * 10);
                const k1 = ptKey(g.seg.x1, g.seg.y1, g.seg.z1), k2 = ptKey(g.seg.x2, g.seg.y2, g.seg.z2);
                const c1 = CUT_LABELS[joints[k1]?.type || 'straight'];
                const c2 = CUT_LABELS[joints[k2]?.type || 'straight'];
                const odd = ++rowNum % 2 === 0 ? 'background:#f8fafc' : '';
                return `<tr style="${odd}">
      <td style="padding:6px 8px;text-align:center;font-weight:800;color:#1e3a8a">${rowNum}</td>
      <td style="padding:6px 8px;text-align:center;font-weight:700">${g.qty} шт</td>
      <td style="padding:6px 8px;font-weight:700;color:#1e293b">${lenMm} мм</td>
      <td style="padding:6px 8px;text-align:center">${c1} / ${c2}</td>
      <td style="padding:6px 8px;color:#64748b">${profile}</td>
    </tr>`;
            }).join('');

            const html = `
    <div style="font-family:'Segoe UI',sans-serif;padding:20px;max-width:800px;margin:0 auto">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;border-bottom:2px solid #0f172a;padding-bottom:10px">
        <div>
          <h2 style="font-size:18px;font-weight:900;color:#0f172a;margin-bottom:4px">📄 Карта розкрою металу</h2>
          <div style="font-size:12px;color:#64748b">${new Date().toLocaleDateString('uk-UA')} | Профіль: <strong style="color:#0f172a">${profile}</strong></div>
        </div>
        <div style="text-align:right;font-size:12px;color:#334155">
          <div>Відрізків (груп): <strong>${Object.keys(groups).length}</strong></div>
          <div>Загальна довжина: <strong style="color:#2563eb">${(totalCm / 100).toFixed(3)} м</strong></div>
        </div>
      </div>
      <div style="margin-bottom:16px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;text-align:center;padding:10px">
        <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;text-align:left">Малюнок (вид: ${activeView}, масштаб: ${gridScale} см/клітинка):</div>
        <img src="${imgDataUrl}" style="max-width:100%;max-height:300px;object-fit:contain;border:1px solid #e2e8f0">
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:12px;margin-bottom:14px">
        <thead><tr style="background:#0f172a;color:#fff">
          <th style="padding:8px;width:36px">№</th><th style="padding:8px;width:60px">К-сть</th>
          <th style="padding:8px">Довжина</th><th style="padding:8px">Різ (поч/кін)</th><th style="padding:8px">Профіль</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div style="padding:10px 14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;font-size:11px">
        <strong>💡 Примітки для різчика:</strong>
        <ul style="margin-top:5px;padding-left:16px;color:#475569">
          <li>Різ <strong>90°</strong> = прямий торець</li>
          <li>Різ <strong>45°</strong> = скіс для кутового з'єднання</li>
          <li>Різ <strong>T-прим.</strong> = примикання до поверхні труби</li>
          <li>Всі розміри — по зовнішньому розміру деталі</li>
        </ul>
      </div>
    </div>`;
            document.getElementById('cut-plan-body').innerHTML = html;
            document.getElementById('print-sheet').innerHTML = html;
            toggleDrawer(true);
        }"""

new_generate = """function generateCutPlan() {
            if (segments.length === 0) { alert('Намалюйте хоча б одну лінію!'); return; }

            const imgDataUrl = canvas.toDataURL('image/png');
            const profile = getProfileLabel();
            const CUT_LABELS = { straight: '90°', '45': '45°', T: 'T-прим.' };

            // Group by rounded mm
            const groups = {};
            let totalMm = 0;
            segments.forEach(seg => {
                const lenMm = segLengthMm(seg);
                totalMm += lenMm;
                const roundedMm = Math.round(lenMm);
                if (!groups[roundedMm]) groups[roundedMm] = { lenMm: roundedMm, qty: 0, seg };
                groups[roundedMm].qty++;
            });

            let rowNum = 0;
            const rows = Object.values(groups).map(g => {
                const lenMm = g.lenMm;
                const c1 = CUT_LABELS[g.seg.cut1 || 'straight'];
                const c2 = CUT_LABELS[g.seg.cut2 || 'straight'];
                const odd = ++rowNum % 2 === 0 ? 'background:#f8fafc' : '';
                return `<tr style="${odd}">
      <td style="padding:6px 8px;text-align:center;font-weight:800;color:#1e3a8a">${rowNum}</td>
      <td style="padding:6px 8px;text-align:center;font-weight:700">${g.qty} шт</td>
      <td style="padding:6px 8px;font-weight:700;color:#1e293b">${lenMm} мм</td>
      <td style="padding:6px 8px;text-align:center">${c1} / ${c2}</td>
      <td style="padding:6px 8px;color:#64748b">${profile}</td>
    </tr>`;
            }).join('');

            const html = `
    <div style="font-family:'Segoe UI',sans-serif;padding:20px;max-width:800px;margin:0 auto">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;border-bottom:2px solid #0f172a;padding-bottom:10px">
        <div>
          <h2 style="font-size:18px;font-weight:900;color:#0f172a;margin-bottom:4px">📄 Карта розкрою металу</h2>
          <div style="font-size:12px;color:#64748b">${new Date().toLocaleDateString('uk-UA')} | Профіль: <strong style="color:#0f172a">${profile}</strong></div>
        </div>
        <div style="text-align:right;font-size:12px;color:#334155">
          <div>Відрізків (груп): <strong>${Object.keys(groups).length}</strong></div>
          <div>Загальна довжина: <strong style="color:#2563eb">${(totalMm / 1000).toFixed(3)} м</strong></div>
        </div>
      </div>
      <div style="margin-bottom:16px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;text-align:center;padding:10px">
        <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;text-align:left">Малюнок (вид: ${activeView}, масштаб: ${gridScale} см/клітинка):</div>
        <img src="${imgDataUrl}" style="max-width:100%;max-height:300px;object-fit:contain;border:1px solid #e2e8f0">
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:12px;margin-bottom:14px">
        <thead><tr style="background:#0f172a;color:#fff">
          <th style="padding:8px;width:36px">№</th><th style="padding:8px;width:60px">К-сть</th>
          <th style="padding:8px">Довжина</th><th style="padding:8px">Різ (поч/кін)</th><th style="padding:8px">Профіль</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div style="padding:10px 14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;font-size:11px">
        <strong>💡 Примітки для різчика:</strong>
        <ul style="margin-top:5px;padding-left:16px;color:#475569">
          <li>Різ <strong>90°</strong> = прямий торець</li>
          <li>Різ <strong>45°</strong> = скіс для кутового з'єднання</li>
          <li>Різ <strong>T-прим.</strong> = примикання до поверхні труби</li>
          <li>Всі розміри — по зовнішньому розміру деталі</li>
        </ul>
      </div>
    </div>`;
            document.getElementById('cut-plan-body').innerHTML = html;
            document.getElementById('print-sheet').innerHTML = html;
            toggleDrawer(true);
        }"""

js_content = js_content.replace(old_generate, new_generate)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_content)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

new_html = text[:style_start] + '<link rel="stylesheet" href="cutter.css">\n' + text[style_end + 8:script_start] + '<script src="cutter.js"></script>\n' + text[script_end + 9:]
with open(html_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print("Успішно оновлено файли: cutter.css, cutter.js та cutter.html!")
