import api from './index'

/**
 * 카드 데이터 정규화 함수
 * @param {object} item
 * @returns {object|null}
 */
export const normalizeCard = (item) => {
  const c = item?.card && typeof item.card === 'object' ? item.card : item
  if (!c) return null
  const rawImg = c.image ?? c.cardImage ?? c.img ?? ''
  const img =
    typeof rawImg === 'string' && rawImg ? rawImg.replace(/\.svg$/i, '.png') : rawImg
  const rawCount = item?.count ?? c?.count ?? 1
  const count = Number.isFinite(Number(rawCount)) ? Number(rawCount) : 1
  return { ...c, image: img, cardImage: img, img, count }
}

/**
 * 내 카드 목록 조회
 * GET /api/v1/cards/me
 * @returns {Promise<{ data: { cards: Array } }>}
 */
export const getCardList = async () => {
  return api.get('/cards/me')
}

/**
 * 카드 뽑기
 * POST /api/v1/cards/draw
 * @returns {Promise<{ data: object }>}
 */
export const drawCard = async () => {
  return api.post('/cards/draw')
}

/**
 * 카드 랭킹 조회
 * GET /api/v1/cards/rankings
 * @returns {Promise<{ data: { topCollectors: Array } }>}
 */
export const getCardRankings = async () => {
  return api.get('/cards/rankings')
}
