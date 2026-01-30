import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useCardStore = defineStore('card', () => {
  // 내 카드 목록
  const cards = ref([])
  // 카드 뽑기
  const newcard = ref([])
  const drawMessage = ref('')

  // API에서 { card: {...} } 형태로 올 수 있어서, 스토어에 저장할 때 1회 정제
  const normalizeCard = (item) => (item?.card && typeof item.card === 'object' ? item.card : item)

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
            if (drawnCard) cards.value = [...cards.value, drawnCard]
            drawMessage.value = '새 카드가 도감에 추가되었습니다!'
            console.log('새 카드가 도감에 추가되었습니다!')
        } else {
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
