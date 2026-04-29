/**
 * Converts numeric amounts into official Ukrainian text descriptions.
 */

const ones = ['', 'один', 'два', 'три', 'чотири', 'п\'ять', 'шість', 'сім', 'вісім', 'дев\'ять'];
const onesFeminine = ['', 'одна', 'дві', 'три', 'чотири', 'п\'ять', 'шість', 'сім', 'вісім', 'дев\'ять'];
const teens = ['десять', 'одинадцять', 'дванадцять', 'тринадцять', 'чотирнадцять', 'п\'ятнадцять', 'шістнадцять', 'сімнадцять', 'вісімнадцять', 'дев\'ятнадцять'];
const tens = ['', '', 'двадцять', 'тридцять', 'сорок', 'п\'ятдесят', 'шістдесят', 'сімдесят', 'вісімдесят', 'дев\'яносто'];
const hundreds = ['', 'сто', 'двісті', 'триста', 'чотириста', 'п\'ятсот', 'шістсот', 'сімсот', 'вісімсот', 'дев\'ятсот'];

function getPluralForm(n: number, form1: string, form2: string, form5: string): string {
  n = Math.abs(n) % 100;
  const n1 = n % 10;
  if (n > 10 && n < 20) return form5;
  if (n1 > 1 && n1 < 5) return form2;
  if (n1 === 1) return form1;
  return form5;
}

function convertGroup(n: number, gender: 'M' | 'F' = 'M'): string {
  let result = '';
  const h = Math.floor(n / 100);
  const t = Math.floor((n % 100) / 10);
  const o = n % 10;

  if (h > 0) result += hundreds[h] + ' ';

  if (t === 1) {
    result += teens[o] + ' ';
  } else {
    if (t > 1) result += tens[t] + ' ';
    if (o > 0) {
      result += (gender === 'F' ? onesFeminine[o] : ones[o]) + ' ';
    }
  }

  return result;
}

export function numberToUkrainianWords(amount: number): string {
  if (amount === 0) return 'Нуль гривень 00 копійок';

  const integerPart = Math.floor(amount);
  const centsPart = Math.round((amount - integerPart) * 100);

  let result = '';

  // Billions
  const billions = Math.floor(integerPart / 1000000000);
  if (billions > 0) {
    result += convertGroup(billions, 'M') + getPluralForm(billions, 'мільярд', 'мільярди', 'мільярдів') + ' ';
  }

  // Millions
  const millions = Math.floor((integerPart % 1000000000) / 1000000);
  if (millions > 0) {
    result += convertGroup(millions, 'M') + getPluralForm(millions, 'мільйон', 'мільйони', 'мільйонів') + ' ';
  }

  // Thousands
  const thousands = Math.floor((integerPart % 1000000) / 1000);
  if (thousands > 0) {
    result += convertGroup(thousands, 'F') + getPluralForm(thousands, 'тисяча', 'тисячі', 'тисяч') + ' ';
  }

  // Remainder (Ones, Tens, Hundreds)
  const remainder = integerPart % 1000;
  if (remainder > 0) {
    result += convertGroup(remainder, 'F'); // Hryvnia is feminine
  } else if (integerPart === 0) {
    result += 'нуль ';
  }

  // Currency declension
  const currencyWord = getPluralForm(integerPart, 'гривня', 'гривні', 'гривень');
  result = result.trim() + ' ' + currencyWord;

  // Capitalize first letter
  result = result.charAt(0).toUpperCase() + result.slice(1);

  // Cents suffix
  const centsStr = centsPart < 10 ? `0${centsPart}` : `${centsPart}`;
  const centsWord = getPluralForm(centsPart, 'копійка', 'копійки', 'копійок');

  return `${result} ${centsStr} ${centsWord}`;
}
