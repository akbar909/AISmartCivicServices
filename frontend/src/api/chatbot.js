import client from './client';

export const suggestCategory = async (text) => {
  const response = await client.post('/chatbot/suggest', { text });
  return response.data;
};

export const sendChatMessage = async (message, history = []) => {
  const response = await client.post('/chatbot/message', { message, history });
  return response.data;
};
