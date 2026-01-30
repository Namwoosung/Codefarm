import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useCardStore = defineStore('card', () => {
  // 내 카드 목록
  const cards = ref([])
  // 카드 뽑기
  const newcard = ref([])
  const drawMessage = ref('')

  const cardList = async () => {
    try {
      const res = await api.get('/cards/me')
      cards.value = res.data.data?.cards ?? []
    } catch (err) {
      console.warn('[card.cardList] failed:', err?.response?.status, err?.response?.data ?? err)
    }
  }

  const cardDraw = async () => {
    try {
        const res = await api.post('/cards/draw')
        newcard.value = res.data.data
        console.log(res.data.message)
        // 보유한 카드인지 확인인
        const isAlreadyOwned = cards.value.some(card => card.id === newcard.id)

        if (!isAlreadyOwned) {
            cards.value.push(drawnCard)
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
