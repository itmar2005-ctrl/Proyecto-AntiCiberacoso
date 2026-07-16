import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

export const sendMessage = async (message, conversationId = null, useKnowledgeBase = true) => {
  const { data } = await api.post('/chat', { message, conversation_id: conversationId, use_knowledge_base: useKnowledgeBase });
  return data;
};

export const getHistory = async () => {
  const { data } = await api.get('/chat/history');
  return data;
};

export const getConversation = async (id) => {
  const { data } = await api.get(`/chat/history/${id}`);
  return data;
};

export const deleteConversation = async (id) => {
  await api.delete(`/chat/history/${id}`);
};

export const uploadDocument = async (file) => {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/documents/upload', form);
  return data;
};

export const uploadUrl = async (url) => {
  const { data } = await api.post(`/documents/upload-url?url=${encodeURIComponent(url)}`);
  return data;
};

export const getDocuments = async () => {
  const { data } = await api.get('/documents');
  return data;
};

export const deleteDocument = async (id) => {
  await api.delete(`/documents/${id}`);
};

export const stt = async (audioBlob) => {
  const form = new FormData();
  form.append('audio', audioBlob, 'recording.wav');
  const { data } = await api.post('/voice/stt', form);
  return data.text;
};

export const tts = async (text, voice = 'shimmer') => {
  const { data } = await api.post(`/voice/tts?text=${encodeURIComponent(text)}&voice=${voice}`);
  return data;
};

export default api;
