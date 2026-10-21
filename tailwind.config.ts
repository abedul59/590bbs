const festivalColors = [
  'amber', 'blue', 'cyan', 'emerald', 'fuchsia', 'green', 'indigo', 'lime',
  'orange', 'pink', 'purple', 'red', 'rose', 'sky', 'slate', 'teal', 'violet',
  'yellow', 'zinc',
].join('|')

export default {
  safelist: [
    { pattern: new RegExp(`^bg-(${festivalColors})-(500|600|700|800|900)$`), variants: ['hover'] },
    { pattern: new RegExp(`^text-(${festivalColors})-(500|600|700|800|900)$`), variants: ['group-hover'] },
    { pattern: new RegExp(`^ring-(${festivalColors})-500$`), variants: ['focus'] },
  ],
}
