import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export interface ChatResponse {
  reply: string
  conversation_id: string
  sources: string[]
  model: string
  tokens_used: number
  processing_time: number
}

export const sendMessage = async (
  message: string,
  conversationId?: string | null,
  useKnowledgeBase = true
): Promise<ChatResponse> => {
  const { data } = await api.post('/chat', {
    message,
    conversation_id: conversationId,
    use_knowledge_base: useKnowledgeBase,
  })
  return data
}

export const startCall = async (): Promise<ChatResponse> => {
  return sendMessage('__CALL_START__')
}

export const getHistory = async () => {
  const { data } = await api.get('/chat/history')
  return data
}

export const getConversation = async (id: string) => {
  const { data } = await api.get(`/chat/history/${id}`)
  return data
}

export const deleteConversation = async (id: string) => {
  await api.delete(`/chat/history/${id}`)
}

export const uploadDocument = async (file: File) => {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/documents/upload', form)
  return data
}

export const uploadUrl = async (url: string) => {
  const { data } = await api.post(`/documents/upload-url?url=${encodeURIComponent(url)}`)
  return data
}

export const getDocuments = async () => {
  const { data } = await api.get('/documents')
  return data
}

export const deleteDocument = async (id: string) => {
  await api.delete(`/documents/${id}`)
}

export const speechToText = async (audioBlob: Blob): Promise<string> => {
  const form = new FormData()
  form.append('audio', audioBlob, 'recording.webm')
  const { data } = await api.post('/voice/stt', form)
  return data.text
}

export const textToSpeech = async (text: string, voice = 'shimmer') => {
  const { data } = await api.post(`/voice/tts?text=${encodeURIComponent(text)}&voice=${voice}`)
  return data
}
