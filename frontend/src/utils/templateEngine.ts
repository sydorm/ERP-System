export interface PrintData {
  document: {
    number: string;
    date: string;
    contract?: string;
    comment?: string;
  };
  seller: {
    name: string;
    edrpou?: string;
    address?: string;
    phone?: string;
    iban?: string;
    bank_name?: string;
    mfo?: string;
  };
  buyer: {
    name: string;
    edrpou?: string;
    address?: string;
  };
  items: Array<{
    index: number;
    name: string;
    quantity: number;
    unit: string;
    price_with_vat: number;
    sum_with_vat: number;
  }>;
  totals: {
    items_count: number;
    total_without_vat: number;
    vat: number;
    total_with_vat: number;
    total_in_words: string;
  };
}

export function renderTemplate(html: string, data: any): string {
  if (!html) return '';
  let rendered = html;

  // 1. Build items_table HTML helper
  if (rendered.includes('{{items_table}}') && data.items) {
    let tableHtml = '';
    data.items.forEach((item: any) => {
      tableHtml += `<tr>
        <td>${item.index}</td>
        <td>${item.article || ''}</td>
        <td>${item.name}</td>
        <td>${item.quantity}</td>
        <td>${item.unit}</td>
        <td>${item.price_with_vat.toFixed(2)}</td>
        <td>${item.sum_with_vat.toFixed(2)}</td>
      </tr>`;
    });
    rendered = rendered.replace('{{items_table}}', tableHtml);
  }

  // 2. Replace scalar variables
  // Recursively flatten the data object for easier access e.g. {{document.number}}
  const flatData: Record<string, string> = {};

  function flatten(obj: any, prefix = '') {
    for (const key in obj) {
      if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
        flatten(obj[key], `${prefix}${key}.`);
      } else {
        flatData[`${prefix}${key}`] = obj[key] !== undefined && obj[key] !== null ? String(obj[key]) : '';
      }
    }
  }

  flatten(data);

  for (const key in flatData) {
    const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
    rendered = rendered.replace(regex, flatData[key]);
  }

  // Clean remaining unmatched tags
  rendered = rendered.replace(/{{\s*[\w\.]+\s*}}/g, '');

  return rendered;
}
