import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useCardStore = defineStore('card', () => {
  // 내 카드 목록
  const cards = ref([])
  // 카드 뽑기
  const newcard = ref([])
  const drawMessage = ref('')

  const normalizeCard = (item) => {
    const c = item?.card && typeof item.card === 'object' ? item.card : item
    if (!c) return null
    const rawImg = c.image ?? c.cardImage ?? c.img ?? ''
    const img =
      typeof rawImg === 'string' && rawImg ? rawImg.replace(/\.svg$/i, '.png') : rawImg
    const rawCount = item?.count ?? c?.count ?? 1
    const count = Number.isFinite(Number(rawCount)) ? Number(rawCount) : 1
    return { ...c, image: img, cardImage: img, img, count }
  }

  const cardList = async () => {
    try {
      const res = await api.get('/cards/me')
      const raw = res.data.data?.cards ?? []
      cards.value = (Array.isArray(raw) ? raw : Object.values(raw)).map(normalizeCard).filter(Boolean)
    } catch (err) {
      console.warn('[card.cardList] failed:', err?.response?.status, err?.response?.data ?? err)
    }
  }

  const cardDraw = async () => {
    try {
        const res = await api.post('/cards/draw')
        const payload = res.data?.data
        newcard.value = payload
    
        // 보유한 카드인지 확인인
        if (payload?.isNew) {
            const drawnCard = normalizeCard(payload)
            if (drawnCard) cards.value = [...cards.value, { ...drawnCard, count: 1 }]
            drawMessage.value = '새 카드가 도감에 추가되었습니다!'
            console.log('새 카드가 도감에 추가되었습니다!')
        } else {
            const drawnCard = normalizeCard(payload)
            if (drawnCard) {
              const drawnId = drawnCard.cardId ?? drawnCard.id ?? null
              const idx = cards.value.findIndex((c) => {
                if (!c) return false
                if (drawnId != null) return c.cardId === drawnId || c.id === drawnId
                return c.no === drawnCard.no && c.grade === drawnCard.grade
              })
              if (idx >= 0) {
                const next = [...cards.value]
                const prev = next[idx]
                const prevCount = Number.isFinite(Number(prev?.count)) ? Number(prev.count) : 1
                next[idx] = { ...prev, count: prevCount + 1 }
                cards.value = next
              } else {
                // 혹시 목록에 없는데 "기존 카드"로 내려온 경우 대비
                cards.value = [...cards.value, { ...drawnCard, count: Number.isFinite(Number(drawnCard.count)) ? Number(drawnCard.count) : 1 }]
              }
            }
            drawMessage.value = '이미 보유 중인 카드입니다.'
            console.log('이미 보유 중인 카드입니다.')
        }
    } catch (err) {
        console.warn('[card.cardDraw] failed:', err?.response?.status, err?.response?.data ?? err)
    }
  }

  return {
    cards,
    newcard,
    drawMessage,
    cardList,
    cardDraw,
  }
})
