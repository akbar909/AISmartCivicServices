import client from './client';

export const getStats = async () => {
  const response = await client.get('/admin/stats');
  return response.data;
};
