type ThemeGroup = '經典配色' | '台灣節慶' | '美國節慶' | '英國節慶'

type Theme = {
  label: string
  group: ThemeGroup
  bg: string
  text: string
  hover: string
  hoverText: string
  ring: string
}

const theme = (label: string, group: ThemeGroup, color: string, shade = 600, hoverShade = 700): Theme => ({
  label,
  group,
  bg: `bg-${color}-${shade}`,
  text: `text-${color}-${shade}`,
  hover: `hover:bg-${color}-${hoverShade}`,
  hoverText: `group-hover:text-${color}-${shade}`,
  ring: `focus:ring-${color}-500`,
})

export const themeConfig = {
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

  tw_lunar_new_year: theme('🧧 農曆新年・福氣紅', '台灣節慶', 'red'),
  tw_lantern: theme('🏮 元宵節・花燈橘', '台灣節慶', 'orange', 500, 600),
  tw_peace: theme('🕊️ 和平紀念日・和平藍', '台灣節慶', 'sky'),
  tw_children: theme('🧒 兒童節・童趣青', '台灣節慶', 'cyan'),
  tw_dragon_boat: theme('🐉 端午節・粽葉綠', '台灣節慶', 'green'),
  tw_qixi: theme('💞 七夕・浪漫粉', '台灣節慶', 'pink'),
  tw_ghost: theme('🪷 中元節・蓮花紫', '台灣節慶', 'violet'),
  tw_mid_autumn: theme('🥮 中秋節・月光金', '台灣節慶', 'yellow', 600, 700),
  tw_national_day: theme('🇹🇼 國慶日・青天藍', '台灣節慶', 'blue', 700, 800),
  tw_pride: theme('🌈 彩虹驕傲・亮彩桃', '台灣節慶', 'fuchsia', 500, 600),

  us_new_year: theme('🎆 新年・午夜靛藍', '美國節慶', 'indigo', 700, 800),
  us_valentines: theme('💘 情人節・愛心玫紅', '美國節慶', 'rose', 500, 600),
  us_st_patricks: theme('☘️ 聖派翠克節・幸運綠', '美國節慶', 'green'),
  us_memorial_day: theme('⭐ 陣亡將士紀念日・榮耀藍', '美國節慶', 'blue', 800, 900),
  us_independence: theme('🇺🇸 獨立日・自由紅', '美國節慶', 'red', 700, 800),
  us_labor_day: theme('🛠️ 勞動節・工業灰', '美國節慶', 'zinc', 700, 800),
  us_halloween: theme('🎃 萬聖節・南瓜橘', '美國節慶', 'orange'),
  us_thanksgiving: theme('🦃 感恩節・豐收金', '美國節慶', 'amber', 700, 800),
  us_christmas: theme('🎄 聖誕節・常青綠', '美國節慶', 'emerald', 700, 800),
  us_black_history: theme('✊🏿 黑人歷史月・傳承金', '美國節慶', 'yellow', 700, 800),

  uk_new_year: theme('🎇 新年・皇家藍', '英國節慶', 'blue', 700, 800),
  uk_st_davids: theme('🌼 聖大衛日・水仙黃', '英國節慶', 'yellow', 500, 600),
  uk_st_patricks: theme('🍀 聖派翠克節・翡翠綠', '英國節慶', 'emerald'),
  uk_easter: theme('🐣 復活節・嫩芽青', '英國節慶', 'lime'),
  uk_st_georges: theme('🏴 聖喬治日・十字紅', '英國節慶', 'red'),
  uk_may_day: theme('🌸 五月節・花舞粉', '英國節慶', 'pink', 500, 600),
  uk_trooping_colour: theme('👑 御林軍閱兵・王室紫', '英國節慶', 'purple', 700, 800),
  uk_summer_bank: theme('☀️ 夏季銀行假日・晴空青', '英國節慶', 'cyan'),
  uk_remembrance: theme('🌺 國殤紀念日・罌粟紅', '英國節慶', 'rose', 700, 800),
  uk_christmas: theme('🎁 聖誕節・冬青綠', '英國節慶', 'teal', 700, 800),
} as const

export const themeGroups = ['經典配色', '台灣節慶', '美國節慶', '英國節慶'] as const
