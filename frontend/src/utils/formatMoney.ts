/**
 * Standardized monetary formatting utility.
 */
export function formatMoney(amount: number): string {
  if (amount === undefined || amount === null) return '0,00 грн';
  
  // Format to 2 decimals, replace standard dot with comma
  const formatted = amount.toFixed(2).replace('.', ',');
  
  // Add spaces as thousand separators
  return formatted.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' грн';
}
