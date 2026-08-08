import client from './client';

export const createComplaint = async (data) => {
  const response = await client.post('/complaints', data);
  return response.data;
};

export const getComplaints = async (params = {}) => {
  const response = await client.get('/complaints', { params });
  return response.data;
};

export const getComplaint = async (id) => {
  const response = await client.get(`/complaints/${id}`);
  return response.data;
};

export const updateComplaint = async (id, data) => {
  const response = await client.patch(`/complaints/${id}`, data);
  return response.data;
};

export const deleteComplaint = async (id) => {
  const response = await client.delete(`/complaints/${id}`);
  return response.data;
};

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await client.post('/complaints/upload-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
