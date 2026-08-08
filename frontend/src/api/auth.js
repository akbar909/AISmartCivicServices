import client from './client';

export const signup = async (data) => {
  const response = await client.post('/auth/signup', data);
  return response.data;
};

export const login = async (data) => {
  const response = await client.post('/auth/login', data);
  return response.data;
};

export const getMe = async () => {
  const response = await client.get('/auth/me');
  return response.data;
};
