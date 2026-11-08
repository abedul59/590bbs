export const BULLETIN_HIDDEN_MARKER = '__590bbs_hidden__'

type BulletinLink = { name?: string; url?: string }
type BulletinLike = { links?: BulletinLink[] | null }

export const isBulletinHidden = (bulletin: BulletinLike | null | undefined) =>
  Array.isArray(bulletin?.links) && bulletin.links.some(link => link?.name === BULLETIN_HIDDEN_MARKER)

export const getVisibleBulletinLinks = (bulletin: BulletinLike | BulletinLink[] | null | undefined) => {
  const links = Array.isArray(bulletin) ? bulletin : bulletin?.links
  return Array.isArray(links) ? links.filter(link => link?.name !== BULLETIN_HIDDEN_MARKER) : []
}

export const setBulletinHidden = (bulletin: BulletinLike, hidden: boolean) => {
  const links = getVisibleBulletinLinks(bulletin)
  return hidden ? [...links, { name: BULLETIN_HIDDEN_MARKER, url: '' }] : links
}
