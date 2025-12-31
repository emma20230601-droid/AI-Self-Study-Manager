// src/utils/exportCalendarPdf.js
import pdfMake from "pdfmake/build/pdfmake.js";
import { NotoSansTC } from "../fonts/NotoSansTC.js";

// 載入字型
pdfMake.vfs = { "NotoSansTC-Regular.ttf": NotoSansTC };
pdfMake.fonts = {
  NotoSansTC: {
    normal: "NotoSansTC-Regular.ttf",
    bold: "NotoSansTC-Regular.ttf",
    italics: "NotoSansTC-Regular.ttf",
    bolditalics: "NotoSansTC-Regular.ttf",
  },
};

/**
 * 匯出「整個月」的 PDF
 * @param {Object} tasksByDate - { "YYYY-MM-DD": [task, ...], ... }
 * @param {String} currentMonthStr - 月份文字
 * @param {String} fileName - PDF 檔名
 */
export const exportMonthCalendarPDF = (
  tasksByDate,
  currentMonthStr = "",
  fileName = "月曆.pdf"
) => {
  const days = Object.keys(tasksByDate).sort();
  const body = [["日期", "任務清單"]];

  for (const day of days) {
    const tasks = tasksByDate[day]
      .map((task) => `${task.subject}：${task.title} (${task.type})`)
      .join("\n");
    body.push([day, tasks]);
  }

  const docDefinition = makeDocDefinition(body, currentMonthStr);

  pdfMake.createPdf(docDefinition).download(fileName);
};

/**
 * 匯出「當前月」的 PDF
 * @param {Object} tasksByDate - { "YYYY-MM-DD": [task, ...], ... }
 * @param {Date} currentMonthDate - 畫面停留的月份 (ex: new Date(2025, 8) 代表 2025/9)
 * @param {String} fileName - PDF 檔名
 */
export const exportCurrentMonthPDF = (
  tasksByDate,
  currentMonthDate,
  fileName = "當月月曆.pdf"
) => {
  const targetYear = currentMonthDate.getFullYear();
  const targetMonth = currentMonthDate.getMonth() + 1; // 1-based

  const days = Object.keys(tasksByDate)
    .filter((day) => {
      const [y, m] = day.split("-").map(Number);
      return y === targetYear && m === targetMonth;
    })
    .sort();

  const body = [["日期", "任務清單"]];

  for (const day of days) {
    const tasks = tasksByDate[day]
      .map((task) => `${task.subject}：${task.title} (${task.type})`)
      .join("\n");
    body.push([day, tasks]);
  }

  const currentMonthStr = `${targetYear}年${targetMonth}月`;
  const docDefinition = makeDocDefinition(body, currentMonthStr);

  pdfMake.createPdf(docDefinition).download(fileName);
};

/** 共用的 PDF 樣式 */
function makeDocDefinition(body, currentMonthStr) {
  return {
    pageSize: "A4",
    pageMargins: [20, 20, 20, 20],
    defaultStyle: {
      font: "NotoSansTC",
      fontSize: 12,
    },
    content: [
      { text: currentMonthStr, style: "header", margin: [0, 0, 0, 10] },
      {
        table: {
          headerRows: 1,
          widths: ["auto", "*"],
          body,
        },
        layout: {
          fillColor: (rowIndex) => (rowIndex === 0 ? "#eeeeee" : null),
          hLineWidth: () => 0.5,
          vLineWidth: () => 0.5,
        },
      },
    ],
    styles: {
      header: { fontSize: 16, bold: true },
    },
  };
}
