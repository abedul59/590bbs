type ThemeGroup = '經典配色' | '台灣節慶' | '美國節慶' | '英國節慶'

export type FestivalSkin = {
  description: string
  motifs: [string, string]
  scene: string
  header: string
  surface: string
  surfaceAlt: string
  border: string
  ink: string
  radius: string
  shadow: string
  font: string
}

type Theme = {
  label: string
  group: ThemeGroup
  bg: string
  text: string
  hover: string
  hoverText: string
  ring: string
  festival?: FestivalSkin
}

const theme = (label: string, group: ThemeGroup, color: string, shade = 600, hoverShade = 700): Theme => ({
  label, group,
  bg: `bg-${color}-${shade}`,
  text: `text-${color}-${shade}`,
  hover: `hover:bg-${color}-${hoverShade}`,
  hoverText: `group-hover:text-${color}-${shade}`,
  ring: `focus:ring-${color}-500`,
})

const festivalTheme = (
  label: string, group: Exclude<ThemeGroup, '經典配色'>, color: string,
  festival: FestivalSkin, shade = 600, hoverShade = 700,
): Theme => ({ ...theme(label, group, color, shade, hoverShade), festival })

const serif = 'Georgia, "Noto Serif TC", "Times New Roman", serif'
const rounded = '"Arial Rounded MT Bold", "Noto Sans TC", Arial, sans-serif'
const modern = '"Trebuchet MS", "Noto Sans TC", Arial, sans-serif'
const classic = 'Garamond, Georgia, "Noto Serif TC", serif'

export const themeConfig: Record<string, Theme> = {
  purple:  theme('🔮 皇家紫（預設）', '經典配色', 'purple'),
  blue:    theme('🌊 海洋藍', '經典配色', 'blue'),
  emerald: theme('🌿 翡翠綠', '經典配色', 'emerald'),
  rose:    theme('🌹 玫瑰紅', '經典配色', 'rose'),
  amber:   theme('🍯 琥珀黃', '經典配色', 'amber', 500, 600),
  slate:   theme('🪨 石板灰', '經典配色', 'slate', 700, 800),
  teal:    theme('🦚 藍綠色', '經典配色', 'teal'),
  indigo:  theme('🌌 靛藍色', '經典配色', 'indigo'),
  fuchsia: theme('🌺 桃紅色', '經典配色', 'fuchsia'),
  orange:  theme('🍊 橘色', '經典配色', 'orange'),

  tw_lunar_new_year: festivalTheme('🧧 農曆新年・福氣紅', '台灣節慶', 'red', {
    description: '剪紙、燙金與春聯風格', motifs: ['春', '🧧'],
    scene: 'radial-gradient(circle at 15% 10%, #fde68a 0 2px, transparent 3px), linear-gradient(135deg, #fff7ed, #fee2e2 48%, #fecaca)',
    header: 'linear-gradient(110deg, #7f1d1d, #dc2626 55%, #991b1b)', surface: 'rgba(255,251,235,.94)', surfaceAlt: 'rgba(254,226,226,.82)', border: '#f59e0b', ink: '#7f1d1d', radius: '6px', shadow: '0 12px 30px rgba(127,29,29,.18)', font: serif,
  }),
  tw_lantern: festivalTheme('🏮 元宵節・花燈橘', '台灣節慶', 'orange', {
    description: '夜空燈海與圓燈籠光暈', motifs: ['🏮', '✨'],
    scene: 'radial-gradient(circle at 20% 20%, rgba(251,146,60,.35) 0 45px, transparent 46px), radial-gradient(circle at 80% 35%, rgba(250,204,21,.28) 0 65px, transparent 66px), linear-gradient(160deg, #172554, #312e81 55%, #7c2d12)',
    header: 'linear-gradient(90deg, #1e1b4b, #c2410c, #1e1b4b)', surface: 'rgba(255,247,237,.93)', surfaceAlt: 'rgba(255,237,213,.82)', border: '#fb923c', ink: '#431407', radius: '24px', shadow: '0 14px 34px rgba(30,27,75,.3)', font: rounded,
  }, 500, 600),
  tw_peace: festivalTheme('🕊️ 和平紀念日・和平藍', '台灣節慶', 'sky', {
    description: '清朗天空、白鴿與安靜留白', motifs: ['🕊️', '☁️'],
    scene: 'linear-gradient(180deg, #e0f2fe 0%, #f8fafc 58%, #ecfeff 100%)',
    header: 'linear-gradient(100deg, #075985, #38bdf8)', surface: 'rgba(255,255,255,.9)', surfaceAlt: 'rgba(224,242,254,.72)', border: '#7dd3fc', ink: '#0c4a6e', radius: '18px', shadow: '0 10px 28px rgba(14,116,144,.13)', font: modern,
  }),
  tw_children: festivalTheme('🧒 兒童節・童趣青', '台灣節慶', 'cyan', {
    description: '彩色積木、圓角與活潑泡泡', motifs: ['🎈', '🧩'],
    scene: 'radial-gradient(circle at 8% 18%, #fde047 0 16px, transparent 17px), radial-gradient(circle at 90% 12%, #f9a8d4 0 24px, transparent 25px), radial-gradient(circle at 75% 85%, #86efac 0 20px, transparent 21px), #ecfeff',
    header: 'linear-gradient(90deg, #0891b2, #06b6d4 35%, #a855f7 70%, #ec4899)', surface: 'rgba(255,255,255,.94)', surfaceAlt: 'rgba(207,250,254,.78)', border: '#22d3ee', ink: '#164e63', radius: '30px', shadow: '0 9px 0 rgba(8,145,178,.18)', font: rounded,
  }),
  tw_dragon_boat: festivalTheme('🐉 端午節・粽葉綠', '台灣節慶', 'green', {
    description: '粽葉紋理、江水波紋與龍舟', motifs: ['🐉', '🌿'],
    scene: 'repeating-linear-gradient(120deg, rgba(21,128,61,.08) 0 2px, transparent 2px 18px), linear-gradient(180deg, #ecfdf5, #cffafe)',
    header: 'linear-gradient(105deg, #14532d, #15803d 55%, #0e7490)', surface: 'rgba(247,254,231,.93)', surfaceAlt: 'rgba(209,250,229,.78)', border: '#4ade80', ink: '#14532d', radius: '4px 22px 4px 22px', shadow: '0 13px 26px rgba(20,83,45,.17)', font: serif,
  }),
  tw_qixi: festivalTheme('💞 七夕・浪漫粉', '台灣節慶', 'pink', {
    description: '銀河星光、柔霧與浪漫弧線', motifs: ['💞', '🌌'],
    scene: 'radial-gradient(circle at 25% 20%, rgba(255,255,255,.8) 0 1px, transparent 2px), radial-gradient(circle at 75% 45%, rgba(255,255,255,.65) 0 1px, transparent 2px), linear-gradient(140deg, #312e81, #831843 55%, #fbcfe8)',
    header: 'linear-gradient(100deg, #312e81, #be185d)', surface: 'rgba(253,242,248,.91)', surfaceAlt: 'rgba(243,232,255,.8)', border: '#f9a8d4', ink: '#701a75', radius: '28px 8px 28px 8px', shadow: '0 16px 40px rgba(112,26,117,.25)', font: classic,
  }),
  tw_ghost: festivalTheme('🪷 中元節・蓮花紫', '台灣節慶', 'violet', {
    description: '暮色蓮花、燭光與沉靜氛圍', motifs: ['🪷', '🕯️'],
    scene: 'radial-gradient(ellipse at 50% 100%, rgba(167,139,250,.28), transparent 52%), linear-gradient(160deg, #111827, #312e81 55%, #4c1d95)',
    header: 'linear-gradient(90deg, #111827, #5b21b6, #111827)', surface: 'rgba(245,243,255,.92)', surfaceAlt: 'rgba(237,233,254,.77)', border: '#8b5cf6', ink: '#2e1065', radius: '2px 18px', shadow: '0 18px 36px rgba(17,24,39,.34)', font: serif,
  }),
  tw_mid_autumn: festivalTheme('🥮 中秋節・月光金', '台灣節慶', 'yellow', {
    description: '滿月、桂花金與深藍夜色', motifs: ['🌕', '🥮'],
    scene: 'radial-gradient(circle at 82% 14%, #fef3c7 0 75px, rgba(254,243,199,.2) 76px, transparent 105px), linear-gradient(150deg, #0f172a, #172554 70%, #713f12)',
    header: 'linear-gradient(90deg, #0f172a, #854d0e)', surface: 'rgba(255,251,235,.93)', surfaceAlt: 'rgba(254,243,199,.8)', border: '#eab308', ink: '#422006', radius: '22px', shadow: '0 15px 38px rgba(15,23,42,.3)', font: classic,
  }, 600, 700),
  tw_national_day: festivalTheme('🇹🇼 國慶日・青天藍', '台灣節慶', 'blue', {
    description: '青天、旗幟切角與慶典光束', motifs: ['🇹🇼', '🎉'],
    scene: 'linear-gradient(150deg, rgba(37,99,235,.12) 0 25%, transparent 25%), linear-gradient(30deg, rgba(220,38,38,.12) 0 25%, transparent 25%), #f8fafc',
    header: 'linear-gradient(90deg, #1e3a8a 0 58%, #dc2626 58%)', surface: 'rgba(255,255,255,.95)', surfaceAlt: 'rgba(219,234,254,.8)', border: '#2563eb', ink: '#172554', radius: '3px', shadow: '8px 8px 0 rgba(220,38,38,.12)', font: modern,
  }, 700, 800),
  tw_pride: festivalTheme('🌈 彩虹驕傲・亮彩桃', '台灣節慶', 'fuchsia', {
    description: '彩虹光譜、玻璃卡片與自由色彩', motifs: ['🌈', '✨'],
    scene: 'linear-gradient(125deg, #fee2e2, #fef3c7 20%, #dcfce7 40%, #cffafe 60%, #dbeafe 80%, #fae8ff)',
    header: 'linear-gradient(90deg, #ef4444, #f59e0b, #22c55e, #06b6d4, #8b5cf6, #ec4899)', surface: 'rgba(255,255,255,.72)', surfaceAlt: 'rgba(255,255,255,.5)', border: 'rgba(217,70,239,.55)', ink: '#581c87', radius: '26px', shadow: '0 16px 36px rgba(147,51,234,.18)', font: rounded,
  }, 500, 600),

  us_new_year: festivalTheme('🎆 新年・午夜靛藍', '美國節慶', 'indigo', {
    description: '午夜煙火、金粉與倒數派對', motifs: ['🎆', '🥂'],
    scene: 'repeating-radial-gradient(circle at 50% 0%, rgba(250,204,21,.25) 0 1px, transparent 2px 34px), linear-gradient(145deg, #020617, #1e1b4b 60%, #4c1d95)',
    header: 'linear-gradient(90deg, #020617, #4338ca, #020617)', surface: 'rgba(238,242,255,.92)', surfaceAlt: 'rgba(224,231,255,.76)', border: '#facc15', ink: '#1e1b4b', radius: '12px', shadow: '0 0 28px rgba(250,204,21,.2)', font: modern,
  }, 700, 800),
  us_valentines: festivalTheme('💘 情人節・愛心玫紅', '美國節慶', 'rose', {
    description: '情書紙張、心形柔光與緞帶', motifs: ['💌', '💘'],
    scene: 'radial-gradient(circle at 10% 20%, rgba(244,63,94,.14) 0 35px, transparent 36px), radial-gradient(circle at 90% 75%, rgba(236,72,153,.13) 0 60px, transparent 61px), #fff1f2',
    header: 'linear-gradient(100deg, #9f1239, #f43f5e, #be185d)', surface: 'rgba(255,255,255,.91)', surfaceAlt: 'rgba(255,228,230,.8)', border: '#fda4af', ink: '#881337', radius: '32px 12px', shadow: '0 14px 35px rgba(190,24,93,.17)', font: classic,
  }, 500, 600),
  us_st_patricks: festivalTheme('☘️ 聖派翠克節・幸運綠', '美國節慶', 'green', {
    description: '三葉草、金幣與愛爾蘭酒館', motifs: ['☘️', '🪙'],
    scene: 'radial-gradient(circle at 12% 18%, rgba(250,204,21,.3) 0 4px, transparent 5px), repeating-linear-gradient(45deg, rgba(22,101,52,.06) 0 12px, transparent 12px 24px), #f0fdf4',
    header: 'linear-gradient(90deg, #14532d, #16a34a, #ca8a04)', surface: 'rgba(250,255,245,.94)', surfaceAlt: 'rgba(220,252,231,.8)', border: '#22c55e', ink: '#14532d', radius: '18px 18px 4px 18px', shadow: '0 10px 0 rgba(202,138,4,.16)', font: rounded,
  }),
  us_memorial_day: festivalTheme('⭐ 陣亡將士紀念日・榮耀藍', '美國節慶', 'blue', {
    description: '莊重海軍藍、星章與紀念緞帶', motifs: ['⭐', '🕊️'],
    scene: 'repeating-linear-gradient(0deg, rgba(30,58,138,.04) 0 28px, rgba(220,38,38,.045) 28px 56px), #f8fafc',
    header: 'linear-gradient(100deg, #172554, #1e40af 70%, #991b1b)', surface: 'rgba(255,255,255,.96)', surfaceAlt: 'rgba(239,246,255,.86)', border: '#94a3b8', ink: '#172554', radius: '2px', shadow: '0 12px 24px rgba(15,23,42,.16)', font: serif,
  }, 800, 900),
  us_independence: festivalTheme('🇺🇸 獨立日・自由紅', '美國節慶', 'red', {
    description: '星條旗、煙火與美式海報', motifs: ['🇺🇸', '🎇'],
    scene: 'repeating-linear-gradient(0deg, rgba(220,38,38,.1) 0 22px, rgba(255,255,255,.5) 22px 44px), linear-gradient(90deg, rgba(30,64,175,.18), transparent 38%)',
    header: 'linear-gradient(90deg, #1e3a8a 0 40%, #fff 40% 44%, #b91c1c 44%)', surface: 'rgba(255,255,255,.91)', surfaceAlt: 'rgba(219,234,254,.82)', border: '#dc2626', ink: '#172554', radius: '0px', shadow: '7px 7px 0 rgba(30,64,175,.18)', font: modern,
  }, 700, 800),
  us_labor_day: festivalTheme('🛠️ 勞動節・工業灰', '美國節慶', 'zinc', {
    description: '工業金屬、斜紋與工具質感', motifs: ['🛠️', '⚙️'],
    scene: 'repeating-linear-gradient(135deg, rgba(24,24,27,.06) 0 10px, transparent 10px 20px), linear-gradient(160deg, #f4f4f5, #d4d4d8)',
    header: 'linear-gradient(90deg, #18181b, #52525b, #ca8a04)', surface: 'rgba(250,250,250,.94)', surfaceAlt: 'rgba(228,228,231,.78)', border: '#71717a', ink: '#18181b', radius: '2px', shadow: '6px 8px 0 rgba(39,39,42,.18)', font: 'Impact, "Arial Narrow", sans-serif',
  }, 700, 800),
  us_halloween: festivalTheme('🎃 萬聖節・南瓜橘', '美國節慶', 'orange', {
    description: '暗夜、南瓜光與怪誕尖角', motifs: ['🎃', '🦇'],
    scene: 'radial-gradient(circle at 80% 10%, #fed7aa 0 55px, transparent 56px), linear-gradient(145deg, #09090b, #3f3f46 58%, #431407)',
    header: 'linear-gradient(90deg, #09090b, #c2410c, #09090b)', surface: 'rgba(255,247,237,.92)', surfaceAlt: 'rgba(254,215,170,.76)', border: '#f97316', ink: '#431407', radius: '2px 22px 2px 22px', shadow: '0 16px 0 rgba(0,0,0,.22)', font: 'Copperplate, fantasy',
  }),
  us_thanksgiving: festivalTheme('🦃 感恩節・豐收金', '美國節慶', 'amber', {
    description: '秋葉、木質餐桌與豐收色調', motifs: ['🦃', '🍂'],
    scene: 'repeating-linear-gradient(90deg, rgba(120,53,15,.045) 0 2px, transparent 2px 38px), linear-gradient(135deg, #fffbeb, #fed7aa)',
    header: 'linear-gradient(100deg, #78350f, #b45309, #92400e)', surface: 'rgba(255,251,235,.94)', surfaceAlt: 'rgba(254,215,170,.78)', border: '#d97706', ink: '#78350f', radius: '16px 4px', shadow: '0 12px 28px rgba(120,53,15,.2)', font: serif,
  }, 700, 800),
  us_christmas: festivalTheme('🎄 聖誕節・常青綠', '美國節慶', 'emerald', {
    description: '常青樹、雪點與紅綠禮物', motifs: ['🎄', '🎅'],
    scene: 'radial-gradient(circle, rgba(255,255,255,.9) 0 2px, transparent 3px) 0 0/34px 34px, linear-gradient(145deg, #ecfdf5, #fee2e2)',
    header: 'linear-gradient(90deg, #064e3b, #047857 62%, #991b1b)', surface: 'rgba(255,255,255,.93)', surfaceAlt: 'rgba(209,250,229,.78)', border: '#dc2626', ink: '#064e3b', radius: '20px', shadow: '0 14px 34px rgba(6,78,59,.2)', font: classic,
  }, 700, 800),
  us_black_history: festivalTheme('✊🏿 黑人歷史月・傳承金', '美國節慶', 'yellow', {
    description: '傳承織紋、黑金與文化色帶', motifs: ['✊🏿', '✨'],
    scene: 'repeating-linear-gradient(135deg, rgba(220,38,38,.09) 0 12px, rgba(234,179,8,.1) 12px 24px, rgba(22,163,74,.09) 24px 36px), #fffbeb',
    header: 'linear-gradient(90deg, #09090b 0 38%, #b91c1c 38% 59%, #ca8a04 59% 80%, #15803d 80%)', surface: 'rgba(255,255,255,.94)', surfaceAlt: 'rgba(254,249,195,.8)', border: '#ca8a04', ink: '#18181b', radius: '0 18px', shadow: '8px 8px 0 rgba(24,24,27,.17)', font: modern,
  }, 700, 800),

  uk_new_year: festivalTheme('🎇 新年・皇家藍', '英國節慶', 'blue', {
    description: '倫敦午夜、皇家藍與金色鐘聲', motifs: ['🎇', '🕛'],
    scene: 'radial-gradient(circle at 50% 8%, rgba(250,204,21,.23) 0 2px, transparent 3px) 0 0/42px 42px, linear-gradient(145deg, #0f172a, #1e3a8a)',
    header: 'linear-gradient(90deg, #0f172a, #1d4ed8, #0f172a)', surface: 'rgba(239,246,255,.93)', surfaceAlt: 'rgba(219,234,254,.78)', border: '#eab308', ink: '#172554', radius: '12px', shadow: '0 12px 32px rgba(15,23,42,.3)', font: classic,
  }, 700, 800),
  uk_st_davids: festivalTheme('🌼 聖大衛日・水仙黃', '英國節慶', 'yellow', {
    description: '水仙花田、威爾斯綠與春光', motifs: ['🌼', '🐉'],
    scene: 'radial-gradient(circle at 15% 18%, rgba(250,204,21,.25) 0 28px, transparent 29px), linear-gradient(160deg, #fefce8, #dcfce7)',
    header: 'linear-gradient(90deg, #166534, #ca8a04)', surface: 'rgba(255,255,240,.94)', surfaceAlt: 'rgba(254,249,195,.82)', border: '#eab308', ink: '#365314', radius: '24px 4px 24px 4px', shadow: '0 12px 28px rgba(77,124,15,.16)', font: serif,
  }, 500, 600),
  uk_st_patricks: festivalTheme('🍀 聖派翠克節・翡翠綠', '英國節慶', 'emerald', {
    description: '翡翠格紋、三葉草與節慶金', motifs: ['🍀', '🎻'],
    scene: 'repeating-linear-gradient(45deg, rgba(5,150,105,.08) 0 18px, transparent 18px 36px), repeating-linear-gradient(-45deg, rgba(234,179,8,.06) 0 18px, transparent 18px 36px), #ecfdf5',
    header: 'linear-gradient(90deg, #064e3b, #059669, #a16207)', surface: 'rgba(255,255,255,.93)', surfaceAlt: 'rgba(209,250,229,.8)', border: '#10b981', ink: '#064e3b', radius: '8px 24px', shadow: '0 10px 0 rgba(5,150,105,.16)', font: classic,
  }),
  uk_easter: festivalTheme('🐣 復活節・嫩芽青', '英國節慶', 'lime', {
    description: '粉彩彩蛋、春日草地與柔軟圓角', motifs: ['🐣', '🥚'],
    scene: 'radial-gradient(ellipse at 12% 20%, #fbcfe8 0 20px, transparent 21px), radial-gradient(ellipse at 86% 32%, #bfdbfe 0 23px, transparent 24px), linear-gradient(180deg, #fefce8, #ecfccb)',
    header: 'linear-gradient(90deg, #65a30d, #84cc16, #ec4899)', surface: 'rgba(255,255,255,.92)', surfaceAlt: 'rgba(236,252,203,.8)', border: '#a3e635', ink: '#3f6212', radius: '34px', shadow: '0 10px 25px rgba(101,163,13,.15)', font: rounded,
  }),
  uk_st_georges: festivalTheme('🏴 聖喬治日・十字紅', '英國節慶', 'red', {
    description: '中世紀旗幟、盾徽與騎士線條', motifs: ['🛡️', '🐉'],
    scene: 'linear-gradient(90deg, transparent 43%, rgba(220,38,38,.09) 43% 57%, transparent 57%), linear-gradient(0deg, transparent 43%, rgba(220,38,38,.09) 43% 57%, transparent 57%), #fff',
    header: 'linear-gradient(90deg, #7f1d1d 0 35%, #fca5a5 35% 39%, #b91c1c 39% 61%, #fca5a5 61% 65%, #7f1d1d 65%)', surface: 'rgba(255,255,255,.95)', surfaceAlt: 'rgba(254,226,226,.82)', border: '#b91c1c', ink: '#450a0a', radius: '0px', shadow: '6px 6px 0 rgba(127,29,29,.16)', font: classic,
  }),
  uk_may_day: festivalTheme('🌸 五月節・花舞粉', '英國節慶', 'pink', {
    description: '花環、彩帶與鄉村五月柱', motifs: ['🌸', '🎀'],
    scene: 'repeating-linear-gradient(115deg, rgba(236,72,153,.055) 0 8px, transparent 8px 24px), linear-gradient(150deg, #fdf2f8, #ecfeff 55%, #f0fdf4)',
    header: 'linear-gradient(90deg, #db2777, #8b5cf6, #0891b2)', surface: 'rgba(255,255,255,.91)', surfaceAlt: 'rgba(252,231,243,.78)', border: '#f9a8d4', ink: '#831843', radius: '28px 6px', shadow: '0 14px 30px rgba(219,39,119,.16)', font: rounded,
  }, 500, 600),
  uk_trooping_colour: festivalTheme('👑 御林軍閱兵・王室紫', '英國節慶', 'purple', {
    description: '王室紫、金邊與典禮布幔', motifs: ['👑', '🎺'],
    scene: 'repeating-linear-gradient(90deg, rgba(88,28,135,.055) 0 3px, transparent 3px 38px), linear-gradient(145deg, #faf5ff, #fef3c7)',
    header: 'linear-gradient(90deg, #3b0764, #7e22ce 68%, #a16207)', surface: 'rgba(255,255,255,.94)', surfaceAlt: 'rgba(243,232,255,.8)', border: '#a855f7', ink: '#3b0764', radius: '4px', shadow: '0 12px 0 rgba(161,98,7,.15)', font: classic,
  }, 700, 800),
  uk_summer_bank: festivalTheme('☀️ 夏季銀行假日・晴空青', '英國節慶', 'cyan', {
    description: '海岸晴空、野餐色塊與清爽留白', motifs: ['☀️', '🧺'],
    scene: 'linear-gradient(180deg, #cffafe 0 54%, #fef9c3 54% 72%, #dcfce7 72%)',
    header: 'linear-gradient(90deg, #0e7490, #06b6d4, #eab308)', surface: 'rgba(255,255,255,.88)', surfaceAlt: 'rgba(207,250,254,.76)', border: '#22d3ee', ink: '#164e63', radius: '22px', shadow: '0 15px 32px rgba(8,145,178,.17)', font: modern,
  }),
  uk_remembrance: festivalTheme('🌺 國殤紀念日・罌粟紅', '英國節慶', 'rose', {
    description: '罌粟花、石碑灰與安靜紀念感', motifs: ['🌺', '🕊️'],
    scene: 'radial-gradient(circle at 12% 20%, rgba(190,18,60,.13) 0 30px, transparent 31px), linear-gradient(150deg, #f8fafc, #e2e8f0)',
    header: 'linear-gradient(90deg, #1f2937, #475569 68%, #9f1239)', surface: 'rgba(255,255,255,.94)', surfaceAlt: 'rgba(241,245,249,.84)', border: '#9f1239', ink: '#1f2937', radius: '3px', shadow: '0 12px 25px rgba(31,41,55,.16)', font: serif,
  }, 700, 800),
  uk_christmas: festivalTheme('🎁 聖誕節・冬青綠', '英國節慶', 'teal', {
    description: '維多利亞聖誕、冬青與格紋禮盒', motifs: ['🎁', '🔔'],
    scene: 'repeating-linear-gradient(0deg, rgba(15,118,110,.06) 0 28px, transparent 28px 56px), repeating-linear-gradient(90deg, rgba(185,28,28,.055) 0 28px, transparent 28px 56px), #f0fdfa',
    header: 'linear-gradient(90deg, #134e4a, #0f766e 62%, #991b1b)', surface: 'rgba(255,255,255,.93)', surfaceAlt: 'rgba(204,251,241,.78)', border: '#b91c1c', ink: '#134e4a', radius: '10px', shadow: '0 14px 32px rgba(19,78,74,.21)', font: classic,
  }, 700, 800),
}

export const themeGroups = ['經典配色', '台灣節慶', '美國節慶', '英國節慶'] as const
