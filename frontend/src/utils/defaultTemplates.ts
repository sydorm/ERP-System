export const DEFAULT_INVOICE_HTML = `
<div style="font-family: Arial, sans-serif; color: #333; line-height: 1.4; padding: 20px; max-width: 800px; margin: 0 auto; border: 1px solid #eee;">
  <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <h2 style="color: #2563eb; margin: 0 0 10px 0;">РАХУНОК НА ОПЛАТУ</h2>
        <p style="margin: 0 0 5px 0;"><strong>№ {{document.number}}</strong></p>
        <p style="margin: 0;">від {{document.date}}</p>
      </td>
      <td style="width: 50%; text-align: right; vertical-align: top;">
        <div style="font-size: 14px; color: #64748b;">
          <strong>Постачальник:</strong><br>
          {{seller.name}}<br>
          ЄДРПОУ: {{seller.edrpou}}<br>
          IBAN: {{seller.iban}}
        </div>
      </td>
    </tr>
  </table>

  <hr style="border: none; border-top: 2px solid #e2e8f0; margin: 20px 0;">

  <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div style="font-size: 14px;">
          <strong style="color: #64748b;">ПЛАТНИК:</strong><br>
          <strong>{{buyer.name}}</strong><br>
          ЄДРПОУ: {{buyer.edrpou}}
        </div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: right;">
        <div style="font-size: 14px;">
          <strong style="color: #64748b;">ДОГОВІР:</strong><br>
          {{document.contract}}
        </div>
      </td>
    </tr>
  </table>

  <div style="margin-bottom: 30px;">
    {{items_table}}
  </div>

  <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
    <tr>
      <td style="width: 60%; vertical-align: top;">
        <div style="font-size: 13px; color: #64748b; border: 1px dashed #cbd5e1; padding: 10px; border-radius: 6px;">
          <strong>Умови оплати:</strong> Оплата згідно договору. Товар відпускається за фактом надходження коштів.
        </div>
      </td>
      <td style="width: 40%; vertical-align: top;">
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 6px 0; font-size: 14px; color: #64748b;">Сума без ПДВ:</td>
            <td style="padding: 6px 0; font-size: 14px; text-align: right;"><strong>{{totals.total_with_vat}}</strong></td>
          </tr>
          <tr>
            <td style="padding: 6px 0; font-size: 14px; color: #64748b;">ПДВ (20%):</td>
            <td style="padding: 6px 0; font-size: 14px; text-align: right;"><strong>{{totals.vat}}</strong></td>
          </tr>
          <tr style="border-top: 1px solid #cbd5e1;">
            <td style="padding: 10px 0; font-size: 16px; font-weight: bold;">Всього до сплати:</td>
            <td style="padding: 10px 0; font-size: 18px; font-weight: bold; color: #2563eb; text-align: right;">{{totals.total_with_vat}}</td>
          </tr>
        </table>
      </td>
    </tr>
  </table>

  <div style="margin-top: 30px; padding: 15px 0; border-top: 1px solid #e2e8f0; font-size: 14px;">
    <p style="margin: 0 0 10px 0;"><strong>Сума прописом:</strong> {{totals.total_in_words}}</p>
  </div>

  <table style="width: 100%; border-collapse: collapse; margin-top: 40px;">
    <tr>
      <td style="width: 50%;">
        <div style="border-bottom: 1px solid #333; width: 200px; margin-bottom: 5px; height: 30px;"></div>
        <span style="font-size: 12px; color: #64748b;">Виписав (підпис)</span>
      </td>
      <td style="width: 50%; text-align: right;">
        <div style="border-bottom: 1px solid #333; width: 200px; margin-bottom: 5px; height: 30px; margin-left: auto;"></div>
        <span style="font-size: 12px; color: #64748b;">Місце печатки</span>
      </td>
    </tr>
  </table>
</div>
`;

export const DEFAULT_SALES_INVOICE_HTML = `
<div style="font-family: Arial, sans-serif; color: #333; line-height: 1.4; padding: 20px; max-width: 800px; margin: 0 auto; border: 1px solid #eee;">
  <div style="text-align: center; margin-bottom: 20px;">
    <h2 style="margin: 0; color: #1e293b;">ВИДАТКОВА НАКЛАДНА</h2>
    <p style="margin: 5px 0;"><strong>№ {{document.number}}</strong> від {{document.date}}</p>
  </div>

  <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px;">
    <tr style="border-bottom: 1px solid #e2e8f0;">
      <td style="padding: 8px 0; color: #64748b; width: 150px;">Постачальник:</td>
      <td style="padding: 8px 0;"><strong>{{seller.name}}</strong>, ЄДРПОУ: {{seller.edrpou}}</td>
    </tr>
    <tr style="border-bottom: 1px solid #e2e8f0;">
      <td style="padding: 8px 0; color: #64748b;">Покупець:</td>
      <td style="padding: 8px 0;"><strong>{{buyer.name}}</strong>, ЄДРПОУ: {{buyer.edrpou}}</td>
    </tr>
    <tr>
      <td style="padding: 8px 0; color: #64748b;">Договір:</td>
      <td style="padding: 8px 0;">{{document.contract}}</td>
    </tr>
  </table>

  <div style="margin-bottom: 20px;">
    {{items_table}}
  </div>

  <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
    <tr>
      <td style="text-align: right; padding: 6px 0; font-size: 14px; color: #64748b; width: 80%;">Разом:</td>
      <td style="text-align: right; padding: 6px 0; font-size: 14px; font-weight: bold; width: 20%;">{{totals.total_with_vat}}</td>
    </tr>
    <tr>
      <td style="text-align: right; padding: 6px 0; font-size: 14px; color: #64748b;">У тому числі ПДВ:</td>
      <td style="text-align: right; padding: 6px 0; font-size: 14px; font-weight: bold;">{{totals.vat}}</td>
    </tr>
  </table>

  <div style="margin-top: 20px; padding: 10px 0; border-top: 2px solid #1e293b; font-size: 14px;">
    <p style="margin: 0;"><strong>Всього відпущено на суму:</strong> {{totals.total_in_words}}</p>
  </div>

  <table style="width: 100%; border-collapse: collapse; margin-top: 50px; font-size: 14px;">
    <tr>
      <td style="width: 50%;">
        Відпустив: _______________________
      </td>
      <td style="width: 50%; text-align: right;">
        Отримав: _______________________
      </td>
    </tr>
  </table>
</div>
`;
